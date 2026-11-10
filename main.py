"""Pizza Station Ares - an Isaac-style real-time roguelike in a pizzeria on Mars.

Run with:   .venv/bin/python main.py
"""

import math
import random
import sys

import pygame

from settings import (
    TITLE, CELL, ROOM_W, ROOM_H, VIEW_W, VIEW_H, PANEL_W,
    SCREEN_W, SCREEN_H, FPS, SCALE, FINAL_FLOOR,
    RESOLUTIONS, GRAPHICS_LEVELS, MAPS, MAP_ORDER,
)
from dungeon import WALL, OBSTACLE, DOOR, HATCH, DOOR_TILES
from game import (
    Game, FLOOR_NAMES,
    load_profile, save_profile, record_progress,
    save_run, load_run, has_saved_run, get_save_summary, clear_saved_run,
)
from items import ITEM_TYPES
from sprites import build_sprites

SPACE = (14, 8, 20)
PANEL_BG = (30, 18, 26)
TEXT = (230, 230, 230)
DIM = (155, 145, 155)
ORANGE = (240, 150, 60)
YELLOW = (250, 212, 80)
RED = (225, 65, 55)
GREEN = (100, 210, 100)
CYAN = (100, 210, 240)

EAT_KEYS = (pygame.K_h, pygame.K_e, pygame.K_SPACE, pygame.K_1)
START_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.profile = load_profile()
        res_idx = self.profile.get("resolution_index", 2)
        if not (0 <= res_idx < len(RESOLUTIONS)):
            res_idx = 2
        self.res_index = res_idx
        self.window_size = RESOLUTIONS[self.res_index][1]
        self.graphics = self.profile.get("graphics_quality", "High")
        if self.graphics not in GRAPHICS_LEVELS:
            self.graphics = "High"

        self.display = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        # All drawing uses the logical 1212x624 surface and scales to self.display
        self.screen = pygame.Surface((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 22)
        self.font_mid = pygame.font.Font(None, 32)
        self.font_big = pygame.font.Font(None, 68)
        self.sprites, self.floors, self.walls = build_sprites(SCALE)
        self.vignette = self._build_room_vignette()

        rng = random.Random(7)
        self.stars = [
            (rng.randrange(SCREEN_W), rng.randrange(SCREEN_H), rng.choice((1, 2)))
            for _ in range(140)
        ]
        # States: "title", "play_menu", "map_select", "settings", "playing"
        self.state = "title"
        self.menu_index = 0
        self.selected_map_idx = 0
        self.buttons = []         # list of (pygame.Rect, action_id) for the active menu
        self.game = None
        self.running = True
        self.frame = 0
        self.mouse_pos = (VIEW_W // 2, VIEW_H // 2)
        self.mouse_shooting = False

    def _build_room_vignette(self):
        """Soft warm edge shading so the whole room is bright and readable."""
        surf = pygame.Surface((VIEW_W, VIEW_H), pygame.SRCALPHA)
        cx, cy = VIEW_W / 2.0, VIEW_H / 2.0
        max_d = math.hypot(cx, cy)
        step = 12
        for y in range(0, VIEW_H, step):
            for x in range(0, VIEW_W, step):
                d = math.hypot(x + step * 0.5 - cx, y + step * 0.5 - cy) / max_d
                alpha = int(max(0.0, (d - 0.55) / 0.45) * 75)
                if alpha > 0:
                    surf.fill((12, 4, 18, alpha), (x, y, step, step))
        return surf

    def to_canvas_pos(self, pos):
        """Convert actual window mouse coordinates to logical 1212x624 canvas coordinates."""
        wx, wy = pos
        dw, dh = self.display.get_size()
        return int(wx * SCREEN_W / max(1, dw)), int(wy * SCREEN_H / max(1, dh))

    def apply_resolution(self, index):
        self.res_index = index % len(RESOLUTIONS)
        self.window_size = RESOLUTIONS[self.res_index][1]
        self.display = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        self.profile["resolution_index"] = self.res_index
        save_profile(self.profile)

    def cycle_graphics(self, step=1):
        idx = (GRAPHICS_LEVELS.index(self.graphics) + step) % len(GRAPHICS_LEVELS)
        self.graphics = GRAPHICS_LEVELS[idx]
        self.profile["graphics_quality"] = self.graphics
        save_profile(self.profile)

    # ---------------------------------------------------------------- input
    def new_game(self, seed=None, map_id="ares_station"):
        self.game = Game(seed=seed, map_id=map_id)
        self.state = "playing"
        save_run(self.game)

    def continue_saved_game(self):
        loaded = load_run()
        if loaded is not None:
            self.game = loaded
            self.state = "playing"
            return True
        return False

    def trigger_menu_action(self, action):
        if action == "open_play":
            self.state = "play_menu"
            self.menu_index = 0 if has_saved_run() else 1
        elif action == "open_settings":
            self.state = "settings"
            self.menu_index = 0
        elif action == "quit":
            self.running = False
        elif action == "load_game":
            self.continue_saved_game()
        elif action == "open_map_select":
            self.state = "map_select"
            self.menu_index = 0
        elif action == "back_title":
            self.state = "title"
            self.menu_index = 0
        elif action == "back_play":
            self.state = "play_menu"
            self.menu_index = 1
        elif action == "res_prev":
            self.apply_resolution(self.res_index - 1)
        elif action == "res_next":
            self.apply_resolution(self.res_index + 1)
        elif action == "gfx_prev":
            self.cycle_graphics(-1)
        elif action == "gfx_next":
            self.cycle_graphics(1)
        elif action == "toggle_unlock_all":
            unlocked = self.profile.setdefault("unlocked_maps", ["ares_station"])
            if len(unlocked) < len(MAP_ORDER):
                self.profile["unlocked_maps"] = list(MAP_ORDER)
            else:
                self.profile["unlocked_maps"] = ["ares_station"]
            save_profile(self.profile)
        elif action.startswith("start_map:"):
            map_id = action.split(":", 1)[1]
            if map_id in self.profile.get("unlocked_maps", ["ares_station"]):
                self.new_game(map_id=map_id)

    def handle_key(self, key):
        if self.state == "title":
            options = ["open_play", "open_settings", "quit"]
            if key == pygame.K_ESCAPE:
                self.running = False
            elif key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(options)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(options)
            elif key in START_KEYS:
                self.trigger_menu_action(options[self.menu_index])
            return

        if self.state == "play_menu":
            options = ["load_game", "open_map_select", "back_title"]
            if key == pygame.K_ESCAPE:
                self.trigger_menu_action("back_title")
            elif key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(options)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(options)
            elif key in START_KEYS:
                act = options[self.menu_index]
                if act == "load_game" and not has_saved_run():
                    self.trigger_menu_action("open_map_select")
                else:
                    self.trigger_menu_action(act)
            return

        if self.state == "map_select":
            if key == pygame.K_ESCAPE:
                self.trigger_menu_action("back_play")
            elif key in (pygame.K_LEFT, pygame.K_a, pygame.K_UP, pygame.K_w):
                self.selected_map_idx = (self.selected_map_idx - 1) % len(MAP_ORDER)
            elif key in (pygame.K_RIGHT, pygame.K_d, pygame.K_DOWN, pygame.K_s):
                self.selected_map_idx = (self.selected_map_idx + 1) % len(MAP_ORDER)
            elif key == pygame.K_u:
                self.trigger_menu_action("toggle_unlock_all")
            elif key in START_KEYS:
                map_id = MAP_ORDER[self.selected_map_idx]
                self.trigger_menu_action(f"start_map:{map_id}")
            return

        if self.state == "settings":
            if key == pygame.K_ESCAPE:
                self.trigger_menu_action("back_title")
            elif key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % 3
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % 3
            elif key in (pygame.K_LEFT, pygame.K_a):
                if self.menu_index == 0:
                    self.trigger_menu_action("res_prev")
                elif self.menu_index == 1:
                    self.trigger_menu_action("gfx_prev")
            elif key in (pygame.K_RIGHT, pygame.K_d):
                if self.menu_index == 0:
                    self.trigger_menu_action("res_next")
                elif self.menu_index == 1:
                    self.trigger_menu_action("gfx_next")
            elif key in START_KEYS:
                if self.menu_index == 0:
                    self.trigger_menu_action("res_next")
                elif self.menu_index == 1:
                    self.trigger_menu_action("gfx_next")
                else:
                    self.trigger_menu_action("back_title")
            return

        # In-game key handling
        g = self.game
        if key == pygame.K_ESCAPE:
            if g and g.state == "playing":
                save_run(g)
            self.running = False
            return
        if key == pygame.K_m:
            # Save & return to starter menu
            if g and g.state == "playing":
                save_run(g)
            self.state = "title"
            self.menu_index = 0
            return
        if key == pygame.K_F5 and g and g.state == "playing":
            save_run(g)
            g.log("Game saved! You can Load it anytime from the Play menu.", CYAN)
            return

        if g.state != "playing":
            if key in (pygame.K_r, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.new_game(map_id=g.map_id)
            return
        if key in EAT_KEYS:
            g.eat_pizza()

    def handle_mouse_down(self, button, pos):
        cpos = self.to_canvas_pos(pos)
        self.mouse_pos = cpos
        if self.state in ("title", "play_menu", "map_select", "settings"):
            if button == 1:
                for rect, action in self.buttons:
                    if rect.collidepoint(cpos):
                        self.trigger_menu_action(action)
                        return
            return

        g = self.game
        if g.state != "playing":
            return
        if button == 1:
            self.mouse_shooting = True
            if g.player.fire_timer <= 0.0:
                g.player_shoot(cpos)
        elif button == 3:
            g.eat_pizza()

    def step_game(self, dt):
        if self.state != "playing" or self.game.state != "playing":
            return
        g = self.game
        prev_pos = g.current_pos
        prev_floor = g.floor
        prev_cleared = g.rooms_cleared

        keys = pygame.key.get_pressed()
        dx = float(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT])
            - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        )
        dy = float(
            (keys[pygame.K_s] or keys[pygame.K_DOWN])
            - (keys[pygame.K_w] or keys[pygame.K_UP])
        )
        self.mouse_pos = self.to_canvas_pos(pygame.mouse.get_pos())
        lmb_held = bool(pygame.mouse.get_pressed()[0]) or self.mouse_shooting
        g.update(dt, dx, dy, aim_target=self.mouse_pos, shooting=lmb_held)

        # Auto-save and check map unlocks when clearing a room, moving rooms, or finishing a run
        if g.state != "playing":
            newly = record_progress(g, self.profile)
            if newly:
                g.unlocked_notice = newly
            clear_saved_run()
        elif g.current_pos != prev_pos or g.floor != prev_floor or g.rooms_cleared != prev_cleared:
            newly = record_progress(g, self.profile)
            for m_name in newly:
                g.log(f"NEW MAP UNLOCKED: {m_name}!", YELLOW)
            save_run(g)

    # -------------------------------------------------------------- drawing
    def text(self, string, pos, colour=TEXT, font=None, center=False, shadow=False):
        font = font or self.font
        img = font.render(string, True, colour)
        rect = img.get_rect()
        if center:
            rect.center = pos
        else:
            rect.topleft = pos
        if shadow:
            self.screen.blit(font.render(string, True, (0, 0, 0)), rect.move(3, 3))
        self.screen.blit(img, rect)
        return rect

    def wrap(self, string, width):
        words, lines, current = string.split(), [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if self.font.size(test)[0] <= width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def bar(self, x, y, w, h, value, maximum, colour):
        pygame.draw.rect(self.screen, (60, 20, 25), (x, y, w, h))
        fill = int(w * max(0, value) / max(1, maximum))
        pygame.draw.rect(self.screen, colour, (x, y, fill, h))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, w, h), 1)

    def draw_button(self, rect, label, action, selected=False, enabled=True, subtitle=None):
        hovered = rect.collidepoint(self.mouse_pos) and enabled
        active = selected or hovered
        if not enabled:
            bg = (28, 22, 32)
            border = (75, 68, 82)
            txt_col = (110, 102, 115)
        elif active:
            bg = (78, 38, 34)
            border = YELLOW
            txt_col = YELLOW
        else:
            bg = (42, 24, 34)
            border = ORANGE
            txt_col = TEXT

        pygame.draw.rect(self.screen, bg, rect, border_radius=6)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=6)
        if subtitle:
            self.text(label, (rect.centerx, rect.centery - 9), txt_col, self.font_mid, center=True)
            self.text(subtitle, (rect.centerx, rect.centery + 14), DIM if enabled else txt_col, self.font, center=True)
        else:
            self.text(label, rect.center, txt_col, self.font_mid, center=True)
        if enabled:
            self.buttons.append((rect, action))

    def draw_stars_and_mars(self):
        self.screen.fill(SPACE)
        for x, y, s in self.stars:
            if self.graphics == "Low":
                twinkle = 185
            else:
                twinkle = 150 + int(80 * math.sin(self.frame * 0.05 + x))
            self.screen.fill((twinkle, twinkle, twinkle), (x, y, s, s))
        cx, cy, r = SCREEN_W - 230, SCREEN_H + 60, 330
        pygame.draw.circle(self.screen, (120, 45, 30), (cx, cy), r)
        pygame.draw.circle(self.screen, (178, 74, 44), (cx - 14, cy - 14), r - 18)
        for dx, dy, cr in ((-150, -230, 30), (-40, -280, 18), (60, -190, 42), (-230, -120, 24)):
            pygame.draw.circle(self.screen, (140, 55, 34), (cx + dx, cy + dy), cr)

    def draw_title(self):
        """Starter Main Menu with Play, Settings, and Quit buttons."""
        self.buttons = []
        self.draw_stars_and_mars()
        self.text("PIZZA STATION", (SCREEN_W // 2, 85), ORANGE, self.font_big, True, True)
        self.text("ARES", (SCREEN_W // 2, 145), YELLOW, self.font_big, True, True)
        self.text("An Isaac-style action roguelike on Mars", (SCREEN_W // 2, 195), TEXT, self.font_mid, True)

        names = ["chef", "pizza", "meatball", "drone", "anchovy", "calzone"]
        start = SCREEN_W // 2 - len(names) * 74 // 2
        step_on = (self.frame // 16) % 2 == 1
        for i, name in enumerate(names):
            alt_key = "chef_walk" if name == "chef" else f"{name}_step"
            key = alt_key if step_on and alt_key in self.sprites else name
            big = pygame.transform.scale(self.sprites[key], (60, 60))
            self.screen.blit(big, (start + i * 74, 225))

        unlocked_cnt = len(self.profile.get("unlocked_maps", ["ares_station"]))
        self.text(
            f"Unlocked Maps: {unlocked_cnt}/{len(MAP_ORDER)}    "
            f"Resolution: {RESOLUTIONS[self.res_index][0]}    Graphics: {self.graphics}",
            (SCREEN_W // 2, 310), CYAN, center=True,
        )

        bw, bh = 340, 54
        bx = SCREEN_W // 2 - bw // 2
        items = [
            ("PLAY", "open_play", "Start a new run or load your saved game"),
            ("SETTINGS", "open_settings", "Change resolution and graphics quality"),
            ("QUIT", "quit", "Exit to desktop"),
        ]
        for idx, (label, act, sub) in enumerate(items):
            rect = pygame.Rect(bx, 342 + idx * 68, bw, bh)
            self.draw_button(rect, label, act, selected=(self.menu_index == idx), subtitle=sub)

        self.text(
            "Click any button with the mouse  -or-  use Up/Down + ENTER",
            (SCREEN_W // 2, SCREEN_H - 26), DIM, center=True,
        )

    def draw_play_menu(self):
        """Play Submenu: choose between Load Saved Game and Start New Game."""
        self.buttons = []
        self.draw_stars_and_mars()
        self.text("SELECT PLAY MODE", (SCREEN_W // 2, 110), ORANGE, self.font_big, True, True)
        self.text("Continue your previous shift or start a fresh mission", (SCREEN_W // 2, 165), TEXT, self.font_mid, True)

        summary = get_save_summary()
        has_save = summary is not None
        load_sub = summary if has_save else "No saved game found - start a new game first"

        bw, bh = 480, 68
        bx = SCREEN_W // 2 - bw // 2
        r_load = pygame.Rect(bx, 230, bw, bh)
        r_new = pygame.Rect(bx, 320, bw, bh)
        r_back = pygame.Rect(bx, 410, bw, 54)

        self.draw_button(
            r_load, "LOAD SAVED GAME", "load_game",
            selected=(self.menu_index == 0), enabled=has_save, subtitle=load_sub,
        )
        self.draw_button(
            r_new, "START NEW GAME", "open_map_select",
            selected=(self.menu_index == 1), enabled=True,
            subtitle="Choose from 4 Martian maps and campaigns",
        )
        self.draw_button(
            r_back, "BACK TO MAIN MENU", "back_title",
            selected=(self.menu_index == 2), enabled=True,
        )

        self.text(
            "Tip: Your game auto-saves every room, or press F5 / M in-game to save & return to menu.",
            (SCREEN_W // 2, SCREEN_H - 30), DIM, center=True,
        )

    def draw_map_select(self):
        """Map Selection screen with 4 unlockable campaigns."""
        self.buttons = []
        self.draw_stars_and_mars()
        self.text("CHOOSE YOUR MAP", (SCREEN_W // 2, 56), ORANGE, self.font_big, True, True)
        self.text(
            "Clear floors and defeat bosses to unlock new Martian sectors!",
            (SCREEN_W // 2, 104), TEXT, self.font_mid, True,
        )

        unlocked = self.profile.get("unlocked_maps", ["ares_station"])
        best_scores = self.profile.get("best_scores", {})

        card_w, card_h = 510, 185
        positions = [
            (66, 134),
            (SCREEN_W - 66 - card_w, 134),
            (66, 338),
            (SCREEN_W - 66 - card_w, 338),
        ]

        for idx, map_id in enumerate(MAP_ORDER):
            info = MAPS[map_id]
            is_unlocked = map_id in unlocked
            cx, cy = positions[idx]
            rect = pygame.Rect(cx, cy, card_w, card_h)
            hovered = rect.collidepoint(self.mouse_pos) and is_unlocked
            selected = (self.selected_map_idx == idx) or hovered

            bg = (44, 24, 34) if is_unlocked else (24, 18, 28)
            border = YELLOW if (selected and is_unlocked) else (info["accent"] if is_unlocked else (75, 68, 82))
            pygame.draw.rect(self.screen, bg, rect, border_radius=8)
            pygame.draw.rect(self.screen, border, rect, 2, border_radius=8)

            # Preview floor tile + boss icon on the left side of the card
            style = info["styles"][0]
            tile_img = pygame.transform.scale(self.floors[style][0], (64, 64))
            self.screen.blit(tile_img, (cx + 18, cy + 22))
            boss_img = pygame.transform.scale(self.sprites["calzone"], (56, 56))
            self.screen.blit(boss_img, (cx + 22, cy + 26))

            stars_str = f"{info['difficulty']}/4"
            title_col = info["accent"] if is_unlocked else DIM
            self.text(f"{idx + 1}. {info['name']}", (cx + 98, cy + 16), title_col, self.font_mid)
            self.text(f"{info['subtitle']}   |   Difficulty: {stars_str}", (cx + 98, cy + 46), TEXT if is_unlocked else DIM)

            for l_i, line in enumerate(self.wrap(info["desc"], card_w - 114)[:2]):
                self.text(line, (cx + 98, cy + 72 + l_i * 20), DIM)

            best = best_scores.get(map_id, 0)
            if is_unlocked:
                status = f"UNLOCKED  -  Click to Play!   (Best Score: {best})"
                self.text(status, (cx + 98, cy + 146), GREEN)
                self.buttons.append((rect, f"start_map:{map_id}"))
            else:
                self.text(f"LOCKED  -  Unlock: {info['unlock_text']}", (cx + 98, cy + 146), RED)

        # Bottom buttons: Back and Demo Unlock Toggle
        r_back = pygame.Rect(66, 548, 240, 48)
        r_demo = pygame.Rect(SCREEN_W - 66 - 360, 548, 360, 48)
        self.draw_button(r_back, "BACK", "back_play")
        all_unlocked = len(unlocked) >= len(MAP_ORDER)
        demo_label = "LOCK EXTRA MAPS" if all_unlocked else "UNLOCK ALL MAPS (DEMO)"
        self.draw_button(r_demo, demo_label, "toggle_unlock_all")

    def draw_settings(self):
        """Settings Menu for changing resolution and graphics quality."""
        self.buttons = []
        self.draw_stars_and_mars()
        self.text("SETTINGS", (SCREEN_W // 2, 95), ORANGE, self.font_big, True, True)
        self.text("Customize resolution and visual effects", (SCREEN_W // 2, 150), TEXT, self.font_mid, True)

        bw, bh = 540, 66
        bx = SCREEN_W // 2 - bw // 2

        # Row 1: Resolution
        res_name = RESOLUTIONS[self.res_index][0]
        r_res = pygame.Rect(bx, 220, bw, bh)
        self.draw_button(
            r_res, f"Resolution:  < {res_name} >", "res_next",
            selected=(self.menu_index == 0),
            subtitle="Click or press Left/Right to resize the game window",
        )

        # Row 2: Graphics Quality
        gfx_desc = {
            "High": "Dynamic oven firelight, room vignette, shadows & full particles",
            "Medium": "Room vignette & shadows on, reduced particles",
            "Low": "Fastest flat pixel rendering (no alpha overlays or extra particles)",
        }[self.graphics]
        r_gfx = pygame.Rect(bx, 310, bw, bh)
        self.draw_button(
            r_gfx, f"Graphics Quality:  < {self.graphics} >", "gfx_next",
            selected=(self.menu_index == 1),
            subtitle=gfx_desc,
        )

        # Row 3: Back
        r_back = pygame.Rect(bx, 420, bw, 56)
        self.draw_button(
            r_back, "SAVE & BACK TO MENU", "back_title",
            selected=(self.menu_index == 2),
        )

    def draw_room(self):
        g = self.game
        room = g.room
        self.screen.fill(SPACE, (0, 0, VIEW_W, VIEW_H))
        anim_alt = (self.frame // 14) % 2 == 1

        # 1. Draw floor, walls, and doors
        floor_variants = self.floors[room.style]
        for ty in range(ROOM_H):
            for tx in range(ROOM_W):
                sx, sy = tx * CELL, ty * CELL
                tile = room.tiles[ty][tx]
                if tile == WALL:
                    below_is_floor = ty + 1 < ROOM_H and room.tiles[ty + 1][tx] != WALL
                    img = self.walls["front" if below_is_floor else "top"]
                    self.screen.blit(img, (sx, sy))
                elif tile == DOOR:
                    door_dir = None
                    for d, (dx, dy) in DOOR_TILES.items():
                        if (tx, ty) == (dx, dy):
                            door_dir = d
                            break
                    nb_pos = room.doors.get(door_dir)
                    is_boss_door = (
                        nb_pos is not None
                        and g.dungeon.rooms[nb_pos].role == "boss"
                        or room.role == "boss"
                    )
                    if room.locked:
                        key = "door_boss_locked" if is_boss_door else "door_locked"
                    else:
                        key = "door_boss_open" if is_boss_door else "door_open"
                    self.screen.blit(self.walls[key], (sx, sy))
                else:
                    f_img = floor_variants[(tx * 7 + ty * 13) % 3]
                    self.screen.blit(f_img, (sx, sy))

        # 1b. Draw walkable floor decorations
        for tx, ty, d_kind in room.floor_decor:
            if d_kind in self.walls:
                self.screen.blit(self.walls[d_kind], (tx * CELL, ty * CELL))

        # 1c. Draw wall fixtures
        for tx, ty, w_kind in room.wall_decor:
            key = f"{w_kind}_alt" if anim_alt and f"{w_kind}_alt" in self.walls else w_kind
            if key in self.walls:
                self.screen.blit(self.walls[key], (tx * CELL, ty * CELL))
                if w_kind == "wall_oven" and self.graphics == "High":
                    glow_r = 26 + (self.frame % 6)
                    glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (245, 130, 40, 45), (glow_r, glow_r), glow_r)
                    self.screen.blit(glow, (tx * CELL + CELL // 2 - glow_r, (ty + 1) * CELL - 8))

        # 1d. Draw solid furniture (big tables, kitchen counters, ovens, freezers, crates)
        for ty in range(ROOM_H):
            for tx in range(ROOM_W):
                tile = room.tiles[ty][tx]
                sx, sy = tx * CELL, ty * CELL
                if tile == OBSTACLE:
                    f_key = room.furniture[ty][tx] or "obstacle"
                    if f_key == "oven_block" and anim_alt:
                        f_key = "oven_block_alt"
                    self.screen.blit(self.walls.get(f_key, self.walls["obstacle"]), (sx, sy))
                elif tile == HATCH:
                    self.screen.blit(self.sprites["hatch"], (sx, sy))

        # 2. Draw items on the floor
        bob_item = int(math.sin(self.frame * 0.12) * 3)
        for item in room.items:
            if item.key in ("rolling_pin", "cutter", "apron", "oxygen"):
                ring_r = 17 + int(math.sin(self.frame * 0.15) * 2)
                pygame.draw.circle(
                    self.screen, (250, 212, 80),
                    (int(item.x), int(item.y) + 8), ring_r, 2
                )
            spr = self.sprites[item.sprite]
            self.screen.blit(
                spr,
                (int(item.x) - spr.get_width() // 2, int(item.y) - spr.get_height() // 2 + bob_item),
            )

        # 3. Draw particles (scaled by graphics quality)
        particles = g.particles if self.graphics != "Low" else g.particles[::2]
        for pt in particles:
            pygame.draw.circle(self.screen, pt[4], (int(pt[0]), int(pt[1])), 3)

        # 4. Draw monsters with frame-by-frame animations
        for m in room.monsters:
            step_on = int(m.timer * 6.0) % 2 == 1
            if m.kind == "calzone":
                spr_key = "calzone_boss_step" if step_on else "calzone_boss"
            else:
                spr_key = f"{m.sprite}_step" if step_on and f"{m.sprite}_step" in self.sprites else m.sprite
            spr = self.sprites[spr_key]
            if m.kind == "anchovy" and g.player.x > m.x:
                spr = pygame.transform.flip(spr, True, False)

            if m.kind == "drone":
                bob = int(math.sin(self.frame * 0.22 + m.x) * 4)
            elif m.kind == "meatball":
                bob = abs(int(math.sin(m.timer * 7.0) * 5))
            else:
                bob = 2 if step_on else 0

            if self.graphics != "Low":
                pygame.draw.ellipse(
                    self.screen, (16, 8, 20),
                    (int(m.x) - int(m.radius * 0.8), int(m.y) + int(m.radius * 0.55), int(m.radius * 1.6), 8),
                )
            draw_x = int(m.x) - spr.get_width() // 2
            draw_y = int(m.y) - spr.get_height() // 2 - bob
            if m.mini_boss and m.kind != "calzone":
                pygame.draw.circle(self.screen, (235, 90, 70), (int(m.x), int(m.y) + 6), int(m.radius) + 4, 2)
            self.screen.blit(spr, (draw_x, draw_y))
            if m.hit_flash > 0:
                pygame.draw.circle(self.screen, (255, 255, 255), (int(m.x), int(m.y)), int(m.radius), 2)
            if m.hp < m.max_hp:
                bw = max(36, spr.get_width() - 8)
                self.bar(int(m.x) - bw // 2, draw_y - 7, bw, 5, m.hp, m.max_hp, RED)

        # 5. Draw chef with walking animation + held weapon aimed at mouse cursor
        p = g.player
        if self.graphics != "Low":
            pygame.draw.ellipse(
                self.screen, (16, 8, 20),
                (int(p.x) - 12, int(p.y) + 12, 24, 8),
            )
        show_chef = p.hit_flash <= 0.0 or (self.frame // 2) % 2 == 0
        if show_chef:
            walk_step = p.moving and (int(p.walk_timer * 10.0) % 2 == 1)
            chef_key = "chef_walk" if walk_step else "chef"
            spr = self.sprites[chef_key]
            facing_left = math.cos(p.aim_angle) < 0
            if facing_left:
                spr = pygame.transform.flip(spr, True, False)
            hop = 2 if walk_step else int(math.sin(self.frame * 0.08) * 1)
            self.screen.blit(
                spr,
                (int(p.x) - spr.get_width() // 2, int(p.y) - spr.get_height() // 2 - hop),
            )

            w_base = self.sprites[p.held_weapon_sprite]
            deg = -math.degrees(p.aim_angle)
            if facing_left:
                w_img = pygame.transform.flip(w_base, False, True)
            else:
                w_img = w_base
            w_rot = pygame.transform.rotate(w_img, deg)
            recoil = (p.recoil_timer / 0.12) * 6.0 if p.recoil_timer > 0 else 0.0
            hold_dist = 15.0 - recoil
            wx = p.x + math.cos(p.aim_angle) * hold_dist
            wy = p.y + 3.0 + math.sin(p.aim_angle) * hold_dist
            self.screen.blit(w_rot, (int(wx) - w_rot.get_width() // 2, int(wy) - w_rot.get_height() // 2))

        if p.muzzle_timer > 0:
            mx_tip = int(p.x + math.cos(p.aim_angle) * 27.0)
            my_tip = int(p.y + 3.0 + math.sin(p.aim_angle) * 27.0)
            pygame.draw.circle(self.screen, (255, 160, 50), (mx_tip, my_tip), 7)
            pygame.draw.circle(self.screen, (255, 245, 160), (mx_tip, my_tip), 4)

        # 6. Draw projectiles
        for proj in g.projectiles:
            px, py = int(proj.x), int(proj.y)
            r = int(proj.radius)
            if proj.from_player:
                if proj.kind == "cutter":
                    pygame.draw.circle(self.screen, (220, 225, 238), (px, py), r)
                    pygame.draw.circle(self.screen, (90, 95, 115), (px, py), r, 2)
                    spin = proj.age * 22.0
                    for k_ang in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
                        bx = px + int(math.cos(spin + k_ang) * (r + 2))
                        by = py + int(math.sin(spin + k_ang) * (r + 2))
                        pygame.draw.line(self.screen, (240, 245, 255), (px, py), (bx, by), 2)
                    pygame.draw.circle(self.screen, RED, (px, py), 3)
                elif proj.kind == "spice":
                    pygame.draw.circle(self.screen, (250, 145, 50), (px, py), r)
                    pygame.draw.circle(self.screen, YELLOW, (px, py), max(2, r - 2))
                else:
                    pygame.draw.circle(self.screen, (245, 215, 110), (px, py), r)
                    pygame.draw.circle(self.screen, (205, 65, 45), (px, py), max(2, r - 3))
            else:
                if proj.kind == "cheese":
                    pulse = 1 if (self.frame // 4) % 2 == 0 else -1
                    pygame.draw.circle(self.screen, (240, 130, 35), (px, py), r + pulse)
                    pygame.draw.circle(self.screen, (255, 220, 90), (px, py), max(3, r - 2))
                else:
                    pygame.draw.circle(self.screen, (255, 55, 55), (px, py), r)
                    pygame.draw.circle(self.screen, (255, 200, 190), (px, py), max(2, r - 3))

        # 7. Subtle room edge lighting (when Graphics Quality is Medium or High)
        if self.graphics in ("Medium", "High"):
            self.screen.blit(self.vignette, (0, 0))

        # 8. Draw aiming crosshair at mouse cursor when inside the room area
        mx, my = self.mouse_pos
        if 0 <= mx < VIEW_W and 0 <= my < VIEW_H and g.state == "playing":
            pygame.draw.circle(self.screen, YELLOW, (mx, my), 9, 1)
            pygame.draw.line(self.screen, ORANGE, (mx - 13, my), (mx - 5, my), 2)
            pygame.draw.line(self.screen, ORANGE, (mx + 5, my), (mx + 13, my), 2)
            pygame.draw.line(self.screen, ORANGE, (mx, my - 13), (mx, my - 5), 2)
            pygame.draw.line(self.screen, ORANGE, (mx, my + 5), (mx, my + 13), 2)

    def draw_minimap(self, x0, y0, w, h):
        """Draw an Isaac-style room minimap on the side panel."""
        g = self.game
        rooms = g.dungeon.rooms
        pygame.draw.rect(self.screen, (18, 10, 18), (x0, y0, w, h))
        pygame.draw.rect(self.screen, (85, 55, 65), (x0, y0, w, h), 1)

        cell_w, cell_h = 26, 18
        cx = x0 + w // 2 - g.current_pos[0] * (cell_w + 4)
        cy = y0 + h // 2 - g.current_pos[1] * (cell_h + 4)

        for (gx, gy), room in rooms.items():
            seen_neighbor = any(
                nb in rooms and rooms[nb].visited for nb in room.doors.values()
            )
            if not room.visited and not seen_neighbor:
                continue

            rx = cx + gx * (cell_w + 4) - cell_w // 2
            ry = cy + gy * (cell_h + 4) - cell_h // 2
            if rx < x0 + 4 or rx + cell_w > x0 + w - 4 or ry < y0 + 4 or ry + cell_h > y0 + h - 4:
                continue

            if (gx, gy) == g.current_pos:
                fill = (235, 155, 55) if not room.locked else (215, 70, 60)
                border = (255, 245, 200)
            elif room.visited:
                fill = (75, 115, 85) if room.cleared else (110, 70, 75)
                border = (155, 175, 165)
            else:
                fill = (40, 32, 46)
                border = (95, 85, 105)

            pygame.draw.rect(self.screen, fill, (rx, ry, cell_w, cell_h))
            pygame.draw.rect(self.screen, border, (rx, ry, cell_w, cell_h), 1)

            if room.role == "boss":
                self.text("B", (rx + cell_w // 2, ry + cell_h // 2), RED, center=True)
            elif room.role == "treasure":
                self.text("$", (rx + cell_w // 2, ry + cell_h // 2), YELLOW, center=True)

    def draw_panel(self):
        g, p = self.game, self.game.player
        x0 = VIEW_W
        pygame.draw.rect(self.screen, PANEL_BG, (x0, 0, PANEL_W, SCREEN_H))
        pygame.draw.line(self.screen, ORANGE, (x0, 0), (x0, SCREEN_H), 2)
        x = x0 + 14

        self.text(g.map_info["name"], (x, 10), g.map_info["accent"], self.font_mid)
        self.text(f"Floor {g.floor}/{FINAL_FLOOR}: {FLOOR_NAMES.get(g.floor, '')}", (x, 40), TEXT)
        self.text(f"HP {max(p.hp, 0)}/{p.max_hp}", (x, 64), TEXT)
        self.bar(x + 90, 64, PANEL_W - 118, 16, p.hp, p.max_hp, GREEN)

        weapon = ITEM_TYPES[p.weapon]["name"] if p.weapon else "Hot Dough Launcher"
        armor = ITEM_TYPES[p.armor]["name"] if p.armor else "Chef's Coat"
        self.text(f"Damage {p.attack}   Defense {p.defense}", (x, 88), TEXT)
        self.text(f"Weapon: {weapon}", (x, 108), DIM)
        self.text(f"Armor:  {armor}", (x, 126), DIM)

        small = pygame.transform.scale(self.sprites["pizza"], (22, 22))
        self.screen.blit(small, (x - 2, 146))
        self.text(f"x {p.pizzas}  (H / RMB to eat)", (x + 24, 150), TEXT)

        coin = pygame.transform.scale(self.sprites["credits"], (22, 22))
        self.screen.blit(coin, (x - 2, 170))
        self.text(f"{p.credits} credits    Kills: {p.kills}", (x + 24, 174), TEXT)

        self.text("Floor Map (B=Boss, $=Supply)", (x, 198), DIM)
        self.draw_minimap(x, 216, PANEL_W - 28, 108)

        y = 332
        boss = g.boss
        if boss:
            self.text(boss.name.upper(), (x, y), YELLOW)
            self.bar(x, y + 18, PANEL_W - 28, 12, boss.hp, boss.max_hp, RED)
            y += 38

        pygame.draw.line(self.screen, (80, 50, 60), (x, y), (x0 + PANEL_W - 14, y))
        y += 6
        lines = []
        for msg, colour in g.messages[-10:]:
            for part in self.wrap(msg, PANEL_W - 28):
                lines.append((part, colour))
        max_lines = max(1, (SCREEN_H - 54 - y) // 18)
        for part, colour in lines[-max_lines:]:
            self.text(part, (x, y), colour)
            y += 18

        self.text("WASD Move  LMB Shoot  H Eat", (x, SCREEN_H - 42), DIM)
        self.text("M: Save & Menu   F5: Quick Save", (x, SCREEN_H - 22), DIM)

    def draw_end_screen(self):
        g = self.game
        overlay = pygame.Surface((VIEW_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        cx = VIEW_W // 2
        if g.state == "won":
            self.text("ORDER DELIVERED!", (cx, 175), YELLOW, self.font_big, True, True)
            self.text(f"You conquered {g.map_info['name']}!", (cx, 235), TEXT, center=True)
        else:
            self.text("YOUR SHIFT IS OVER", (cx, 175), RED, self.font_big, True, True)
            self.text(f"You were defeated by the {g.killer} on Floor {g.floor}.", (cx, 235), TEXT, center=True)
        p = g.player
        self.text(
            f"Kills: {p.kills}    Credits: {p.credits}    Rooms Cleared: {g.rooms_cleared}",
            (cx, 275), DIM, center=True,
        )
        self.text(f"SCORE: {g.score}", (cx, 315), ORANGE, self.font_mid, True)
        if g.unlocked_notice:
            self.text(
                f"NEW MAP UNLOCKED: {', '.join(g.unlocked_notice)}!",
                (cx, 355), GREEN, self.font_mid, True,
            )
        self.text("Press R to play again   -   M for Main Menu   -   ESC to quit", (cx, 405), TEXT, center=True)

    def render(self):
        if self.state == "title":
            self.draw_title()
        elif self.state == "play_menu":
            self.draw_play_menu()
        elif self.state == "map_select":
            self.draw_map_select()
        elif self.state == "settings":
            self.draw_settings()
        else:
            self.draw_room()
            self.draw_panel()
            if self.game.state != "playing":
                self.draw_end_screen()

    def present(self):
        """Scale logical canvas to the selected resolution and fit the actual window."""
        dw, dh = self.display.get_size()
        rw, rh = self.window_size
        surf = self.screen
        if (rw, rh) != (SCREEN_W, SCREEN_H):
            surf = pygame.transform.scale(surf, (rw, rh))
        if surf.get_size() != (dw, dh):
            surf = pygame.transform.scale(surf, (dw, dh))
        self.display.blit(surf, (0, 0))
        pygame.display.flip()

    # ------------------------------------------------------------ main loop
    def run(self):
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state == "playing" and self.game and self.game.state == "playing":
                        save_run(self.game)
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event.button, event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_shooting = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = self.to_canvas_pos(event.pos)
            self.step_game(dt)
            self.render()
            self.present()
            self.frame += 1
        pygame.quit()


if __name__ == "__main__":
    App().run()
    sys.exit()
