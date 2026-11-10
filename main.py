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
)
from dungeon import WALL, OBSTACLE, DOOR, HATCH, DOOR_TILES
from game import Game, FLOOR_NAMES
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
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 22)
        self.font_mid = pygame.font.Font(None, 32)
        self.font_big = pygame.font.Font(None, 72)
        self.sprites, self.floors, self.walls = build_sprites(SCALE)
        self.vignette = self._build_room_vignette()

        rng = random.Random(7)
        self.stars = [
            (rng.randrange(SCREEN_W), rng.randrange(SCREEN_H), rng.choice((1, 2)))
            for _ in range(140)
        ]
        self.state = "title"
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
        # Only lightly shade the outer wall frame so the room interior is well-lit
        step = 12
        for y in range(0, VIEW_H, step):
            for x in range(0, VIEW_W, step):
                d = math.hypot(x + step * 0.5 - cx, y + step * 0.5 - cy) / max_d
                alpha = int(max(0.0, (d - 0.55) / 0.45) * 75)
                if alpha > 0:
                    surf.fill((12, 4, 18, alpha), (x, y, step, step))
        return surf

    # ---------------------------------------------------------------- input
    def new_game(self, seed=None):
        self.game = Game(seed)
        self.state = "playing"

    def handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self.running = False
            return
        if self.state == "title":
            if key in START_KEYS:
                self.new_game()
            return
        g = self.game
        if g.state != "playing":
            if key in (pygame.K_r, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.new_game()
            return
        if key in EAT_KEYS:
            g.eat_pizza()

    def handle_mouse_down(self, button, pos):
        self.mouse_pos = pos
        if self.state == "title" and button == 1:
            self.new_game()
            return
        if self.state != "playing":
            return
        g = self.game
        if g.state != "playing":
            return
        if button == 1:
            # Left click shoots immediately toward the mouse cursor
            self.mouse_shooting = True
            if g.player.fire_timer <= 0.0:
                g.player_shoot(pos)
        elif button == 3:
            # Right click eats a pizza slice
            g.eat_pizza()

    def step_game(self, dt):
        if self.state != "playing" or self.game.state != "playing":
            return
        keys = pygame.key.get_pressed()
        dx = float(
            (keys[pygame.K_d] or keys[pygame.K_RIGHT])
            - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        )
        dy = float(
            (keys[pygame.K_s] or keys[pygame.K_DOWN])
            - (keys[pygame.K_w] or keys[pygame.K_UP])
        )
        mx, my = pygame.mouse.get_pos()
        self.mouse_pos = (mx, my)
        lmb_held = bool(pygame.mouse.get_pressed()[0]) or self.mouse_shooting
        self.game.update(dt, dx, dy, aim_target=self.mouse_pos, shooting=lmb_held)

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

    def draw_stars(self):
        self.screen.fill(SPACE)
        for x, y, s in self.stars:
            twinkle = 150 + int(80 * math.sin(self.frame * 0.05 + x))
            self.screen.fill((twinkle, twinkle, twinkle), (x, y, s, s))

    def draw_title(self):
        self.draw_stars()
        cx, cy, r = SCREEN_W - 230, SCREEN_H + 60, 330
        pygame.draw.circle(self.screen, (120, 45, 30), (cx, cy), r)
        pygame.draw.circle(self.screen, (178, 74, 44), (cx - 14, cy - 14), r - 18)
        for dx, dy, cr in ((-150, -230, 30), (-40, -280, 18), (60, -190, 42), (-230, -120, 24)):
            pygame.draw.circle(self.screen, (140, 55, 34), (cx + dx, cy + dy), cr)

        self.text("PIZZA STATION", (SCREEN_W // 2, 105), ORANGE, self.font_big, True, True)
        self.text("ARES", (SCREEN_W // 2, 170), YELLOW, self.font_big, True, True)
        self.text("An Isaac-style action roguelike on Mars", (SCREEN_W // 2, 225), TEXT, self.font_mid, True)

        names = ["chef", "pizza", "meatball", "drone", "anchovy", "calzone"]
        start = SCREEN_W // 2 - len(names) * 74 // 2
        for i, name in enumerate(names):
            big = pygame.transform.scale(self.sprites[name], (64, 64))
            self.screen.blit(big, (start + i * 74, 265))

        story = [
            "The year is 2097. Your Martian pizzeria has been overrun by",
            "mutant meatballs, rogue delivery drones and alien anchovies.",
            "Clear rooms, collect upgrades, and defeat the Giant Calzone on Floor 5!",
        ]
        for i, line in enumerate(story):
            self.text(line, (SCREEN_W // 2, 360 + i * 24), DIM, center=True)

        if (self.frame // 25) % 2 == 0:
            self.text("Press ENTER or Left-Click to start", (SCREEN_W // 2, 465), YELLOW, self.font_mid, True)
        self.text(
            "Move: WASD / Arrows    Aim: Mouse    Shoot: Left Click (LMB)    Eat Pizza: H / Right Click    Quit: ESC",
            (SCREEN_W // 2, SCREEN_H - 28), DIM, center=True,
        )

    def draw_room(self):
        g = self.game
        room = g.room
        self.screen.fill(SPACE, (0, 0, VIEW_W, VIEW_H))

        # 1. Draw floor, walls, obstacles, doors, and hatch
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
                    # Check if this door leads to the boss room
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
                    # Floor base
                    f_img = floor_variants[(tx * 7 + ty * 13) % 3]
                    self.screen.blit(f_img, (sx, sy))
                    if tile == OBSTACLE:
                        self.screen.blit(self.walls["obstacle"], (sx, sy))
                    elif tile == HATCH:
                        self.screen.blit(self.sprites["hatch"], (sx, sy))

        # 2. Draw items on the floor (with a subtle bobbing animation)
        bob_item = int(math.sin(self.frame * 0.1) * 3)
        for item in room.items:
            if item.key in ("rolling_pin", "cutter", "apron", "oxygen"):
                # Pedestal glow under upgrade items
                pygame.draw.circle(
                    self.screen, (250, 212, 80),
                    (int(item.x), int(item.y) + 8), 18, 2
                )
            spr = self.sprites[item.sprite]
            self.screen.blit(
                spr,
                (int(item.x) - spr.get_width() // 2, int(item.y) - spr.get_height() // 2 + bob_item),
            )

        # 3. Draw particles (sauce splatters / hit sparks)
        for pt in g.particles:
            pygame.draw.circle(self.screen, pt[4], (int(pt[0]), int(pt[1])), 3)

        # 4. Draw monsters
        for m in room.monsters:
            spr_key = "calzone_boss" if m.kind == "calzone" else m.sprite
            spr = self.sprites[spr_key]
            bob = 3 if m.kind == "drone" and (self.frame // 10) % 2 else 0
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

        # 5. Draw chef (flashes briefly during invincibility frames)
        p = g.player
        show_chef = p.iframe_timer <= 0.0 or (self.frame // 3) % 2 == 0
        if show_chef:
            spr = self.sprites["chef"]
            self.screen.blit(
                spr,
                (int(p.x) - spr.get_width() // 2, int(p.y) - spr.get_height() // 2),
            )
        # Small directional aim dot around the chef showing aim angle
        aim_x = int(p.x + math.cos(p.aim_angle) * 24)
        aim_y = int(p.y + math.sin(p.aim_angle) * 24)
        pygame.draw.circle(self.screen, YELLOW, (aim_x, aim_y), 3)

        # 6. Draw projectiles
        for proj in g.projectiles:
            px, py = int(proj.x), int(proj.y)
            r = int(proj.radius)
            if proj.from_player:
                if proj.kind == "cutter":
                    pygame.draw.circle(self.screen, (220, 225, 238), (px, py), r)
                    pygame.draw.circle(self.screen, (90, 95, 115), (px, py), r, 2)
                    pygame.draw.circle(self.screen, RED, (px, py), 3)
                elif proj.kind == "spice":
                    pygame.draw.circle(self.screen, (250, 145, 50), (px, py), r)
                    pygame.draw.circle(self.screen, YELLOW, (px, py), max(2, r - 2))
                else:
                    pygame.draw.circle(self.screen, (245, 215, 110), (px, py), r)
                    pygame.draw.circle(self.screen, (205, 65, 45), (px, py), max(2, r - 3))
            else:
                if proj.kind == "cheese":
                    pygame.draw.circle(self.screen, (240, 130, 35), (px, py), r)
                    pygame.draw.circle(self.screen, (255, 220, 90), (px, py), max(3, r - 2))
                else:
                    pygame.draw.circle(self.screen, (255, 55, 55), (px, py), r)
                    pygame.draw.circle(self.screen, (255, 200, 190), (px, py), max(2, r - 3))

        # 7. Subtle room edge lighting (entire room stays clearly visible!)
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
            # Show room if visited or adjacent to any visited room
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

            # Special room icons
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

        self.text(TITLE, (x, 10), ORANGE, self.font_mid)
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

        # Floor Minimap
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

        self.text("Move: WASD   Aim: Mouse", (x, SCREEN_H - 42), DIM)
        self.text("Shoot: Left-Click   Eat: H / RMB", (x, SCREEN_H - 22), DIM)

    def draw_end_screen(self):
        g = self.game
        overlay = pygame.Surface((VIEW_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        self.screen.blit(overlay, (0, 0))
        cx = VIEW_W // 2
        if g.state == "won":
            self.text("ORDER DELIVERED!", (cx, 190), YELLOW, self.font_big, True, True)
            self.text("You defeated the Giant Calzone and saved the pizzeria!", (cx, 250), TEXT, center=True)
        else:
            self.text("YOUR SHIFT IS OVER", (cx, 190), RED, self.font_big, True, True)
            self.text(f"You were defeated by the {g.killer} on Floor {g.floor}.", (cx, 250), TEXT, center=True)
        p = g.player
        self.text(
            f"Kills: {p.kills}    Credits: {p.credits}    Rooms Cleared: {g.rooms_cleared}",
            (cx, 290), DIM, center=True,
        )
        self.text(f"SCORE: {g.score}", (cx, 330), ORANGE, self.font_mid, True)
        self.text("Press R to play again   -   ESC to quit", (cx, 390), TEXT, center=True)

    def render(self):
        if self.state == "title":
            self.draw_title()
        else:
            self.draw_room()
            self.draw_panel()
            if self.game.state != "playing":
                self.draw_end_screen()

    # ------------------------------------------------------------ main loop
    def run(self):
        while self.running:
            dt = min(0.05, self.clock.tick(FPS) / 1000.0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event.button, event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_shooting = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
            self.step_game(dt)
            self.render()
            pygame.display.flip()
            self.frame += 1
        pygame.quit()


if __name__ == "__main__":
    App().run()
    sys.exit()
