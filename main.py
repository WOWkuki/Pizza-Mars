"""Pizza Station Ares - a roguelike in a pizzeria on Mars.

Run with:   .venv/bin/python main.py
"""

import math
import random
import sys

import pygame

from settings import (TITLE, CELL, MAP_W, MAP_H, VIEW_W, VIEW_H, PANEL_W,
                      SCREEN_W, SCREEN_H, FPS, SCALE, FINAL_FLOOR)
from dungeon import WALL, HATCH
from game import Game, FLOOR_NAMES
from items import ITEM_TYPES
from sprites import build_sprites

SPACE = (14, 8, 20)
PANEL_BG = (30, 18, 26)
TEXT = (230, 230, 230)
DIM = (150, 140, 150)
ORANGE = (240, 150, 60)
RED = (220, 60, 50)
GREEN = (100, 210, 100)

MOVE_KEYS = {
    pygame.K_UP: (0, -1), pygame.K_w: (0, -1), pygame.K_KP8: (0, -1),
    pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1), pygame.K_KP2: (0, 1),
    pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0), pygame.K_KP4: (-1, 0),
    pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0), pygame.K_KP6: (1, 0),
    pygame.K_q: (-1, -1), pygame.K_KP7: (-1, -1),
    pygame.K_e: (1, -1), pygame.K_KP9: (1, -1),
    pygame.K_z: (-1, 1), pygame.K_KP1: (-1, 1),
    pygame.K_c: (1, 1), pygame.K_KP3: (1, 1),
}
WAIT_KEYS = (pygame.K_SPACE, pygame.K_PERIOD, pygame.K_KP5)
EAT_KEYS = (pygame.K_h, pygame.K_1)
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
        self.shade = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        self.shade.fill((8, 0, 18, 170))       # darkens tiles you remember but can't see
        rng = random.Random(7)
        self.stars = [(rng.randrange(SCREEN_W), rng.randrange(SCREEN_H), rng.choice((1, 2)))
                      for _ in range(140)]
        self.state = "title"
        self.game = None
        self.running = True
        self.frame = 0
        pygame.key.set_repeat(220, 110)        # hold a key to keep walking

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
        if key in MOVE_KEYS:
            g.player_move(*MOVE_KEYS[key])
        elif key in WAIT_KEYS:
            g.player_wait()
        elif key in EAT_KEYS:
            g.eat_pizza()

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
        fill = int(w * max(0, value) / maximum)
        pygame.draw.rect(self.screen, colour, (x, y, fill, h))
        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, w, h), 1)

    def draw_stars(self):
        self.screen.fill(SPACE)
        for x, y, s in self.stars:
            twinkle = 150 + int(80 * math.sin(self.frame * 0.05 + x))
            self.screen.fill((twinkle, twinkle, twinkle), (x, y, s, s))

    def draw_title(self):
        self.draw_stars()
        # Mars
        cx, cy, r = SCREEN_W - 230, SCREEN_H + 60, 330
        pygame.draw.circle(self.screen, (120, 45, 30), (cx, cy), r)
        pygame.draw.circle(self.screen, (178, 74, 44), (cx - 14, cy - 14), r - 18)
        for dx, dy, cr in ((-150, -230, 30), (-40, -280, 18), (60, -190, 42), (-230, -120, 24)):
            pygame.draw.circle(self.screen, (140, 55, 34), (cx + dx, cy + dy), cr)
        # Title
        self.text("PIZZA STATION", (SCREEN_W // 2, 110), ORANGE, self.font_big, True, True)
        self.text("ARES", (SCREEN_W // 2, 175), (250, 212, 80), self.font_big, True, True)
        self.text("A roguelike pizzeria on Mars", (SCREEN_W // 2, 230), TEXT, self.font_mid, True)
        # Cast of characters
        names = ["chef", "pizza", "meatball", "drone", "anchovy", "calzone"]
        start = SCREEN_W // 2 - len(names) * 70 // 2
        for i, name in enumerate(names):
            big = pygame.transform.scale(self.sprites[name], (64, 64))
            self.screen.blit(big, (start + i * 70, 270))
        story = ["The year is 2097. Your Martian pizzeria has been overrun by",
                 "mutant meatballs, rogue delivery drones and alien anchovies.",
                 "Fight your way down 5 floors and defeat the Giant Calzone!"]
        for i, line in enumerate(story):
            self.text(line, (SCREEN_W // 2, 370 + i * 24), DIM, center=True)
        if (self.frame // 15) % 2 == 0:
            self.text("Press ENTER to start", (SCREEN_W // 2, 470), (250, 212, 80), self.font_mid, True)
        self.text("Move: arrows / WASD    Diagonal: Q E Z C    Eat pizza: H    Wait: SPACE    Quit: ESC",
                  (SCREEN_W // 2, SCREEN_H - 30), DIM, center=True)

    def camera(self):
        p = self.game.player
        cam_x = min(max(p.x - VIEW_W // 2, 0), MAP_W - VIEW_W)
        cam_y = min(max(p.y - VIEW_H // 2, 0), MAP_H - VIEW_H)
        return cam_x, cam_y

    def draw_map(self):
        g = self.game
        d = g.dungeon
        cam_x, cam_y = self.camera()
        self.screen.fill(SPACE, (0, 0, VIEW_W * CELL, SCREEN_H))
        for vy in range(VIEW_H):
            for vx in range(VIEW_W):
                mx, my = cam_x + vx, cam_y + vy
                if not d.explored[my][mx]:
                    continue
                tile = d.tiles[my][mx]
                if tile == WALL:
                    below_is_floor = my + 1 < MAP_H and d.tiles[my + 1][mx] != WALL
                    img = self.walls["front" if below_is_floor else "top"]
                elif tile == HATCH:
                    img = self.floors[d.style[my][mx]][0]
                    self.screen.blit(img, (vx * CELL, vy * CELL))
                    img = self.sprites["hatch"]
                else:
                    img = self.floors[d.style[my][mx]][(mx * 7 + my * 13) % 3]
                self.screen.blit(img, (vx * CELL, vy * CELL))
                if (mx, my) not in d.visible:
                    self.screen.blit(self.shade, (vx * CELL, vy * CELL))

        def on_screen(x, y):
            return (x - cam_x) * CELL, (y - cam_y) * CELL

        for item in g.items:
            if (item.x, item.y) in d.visible:
                self.screen.blit(self.sprites[item.sprite], on_screen(item.x, item.y))
        for m in g.monsters:
            if (m.x, m.y) in d.visible:
                sx, sy = on_screen(m.x, m.y)
                bob = 1 if m.kind == "drone" and (self.frame // 8) % 2 else 0   # drones hover
                self.screen.blit(self.sprites[m.sprite], (sx, sy - bob * 2))
                if m.hp < m.max_hp:
                    self.bar(sx + 2, sy - 4, CELL - 4, 4, m.hp, m.max_hp, RED)
        p = g.player
        self.screen.blit(self.sprites["chef"], on_screen(p.x, p.y))

    def draw_panel(self):
        g, p = self.game, self.game.player
        x0 = VIEW_W * CELL
        pygame.draw.rect(self.screen, PANEL_BG, (x0, 0, PANEL_W, SCREEN_H))
        pygame.draw.line(self.screen, ORANGE, (x0, 0), (x0, SCREEN_H), 2)
        x = x0 + 14
        self.text(TITLE, (x, 12), ORANGE, self.font_mid)
        self.text(f"Floor {g.floor}/{FINAL_FLOOR}: {FLOOR_NAMES.get(g.floor, '')}", (x, 44), TEXT)
        self.text(f"HP {max(p.hp, 0)}/{p.max_hp}", (x, 70), TEXT)
        self.bar(x + 90, 70, PANEL_W - 118, 16, p.hp, p.max_hp, GREEN)
        weapon = ITEM_TYPES[p.weapon]["name"] if p.weapon else "Bare hands"
        armor = ITEM_TYPES[p.armor]["name"] if p.armor else "Chef's coat"
        self.text(f"Attack {p.attack}   Defense {p.defense}", (x, 96), TEXT)
        self.text(f"Weapon: {weapon}", (x, 118), DIM)
        self.text(f"Armor:  {armor}", (x, 138), DIM)
        small = pygame.transform.scale(self.sprites["pizza"], (24, 24))
        self.screen.blit(small, (x - 4, 160))
        self.text(f"x {p.pizzas}  (H to eat)", (x + 24, 165), TEXT)
        coin = pygame.transform.scale(self.sprites["credits"], (24, 24))
        self.screen.blit(coin, (x - 4, 186))
        self.text(f"{p.credits} credits    Kills: {p.kills}", (x + 24, 191), TEXT)

        y = 222
        boss = g.boss
        if boss and (boss.x, boss.y) in g.dungeon.visible:
            self.text("GIANT CALZONE", (x, y), (250, 212, 80))
            self.bar(x, y + 20, PANEL_W - 28, 12, boss.hp, boss.max_hp, RED)
            y += 42

        pygame.draw.line(self.screen, (80, 50, 60), (x, y), (x0 + PANEL_W - 14, y))
        y += 8
        lines = []
        for msg, colour in g.messages[-10:]:
            for part in self.wrap(msg, PANEL_W - 28):
                lines.append((part, colour))
        max_lines = (SCREEN_H - 70 - y) // 19
        for part, colour in lines[-max_lines:]:
            self.text(part, (x, y), colour)
            y += 19

        self.text("Arrows/WASD move  QEZC diagonal", (x, SCREEN_H - 46), DIM)
        self.text("Walk into monsters to attack", (x, SCREEN_H - 26), DIM)

    def draw_end_screen(self):
        g = self.game
        overlay = pygame.Surface((VIEW_W * CELL, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))
        cx = VIEW_W * CELL // 2
        if g.state == "won":
            self.text("ORDER DELIVERED!", (cx, 190), (250, 212, 80), self.font_big, True, True)
            self.text("You defeated the Giant Calzone and saved the pizzeria!", (cx, 250), TEXT, center=True)
        else:
            self.text("YOUR SHIFT IS OVER", (cx, 190), RED, self.font_big, True, True)
            self.text(f"You were defeated by the {g.killer} on floor {g.floor}.", (cx, 250), TEXT, center=True)
        p = g.player
        self.text(f"Kills: {p.kills}    Credits: {p.credits}    Turns: {g.turn}", (cx, 290), DIM, center=True)
        self.text(f"SCORE: {g.score}", (cx, 330), ORANGE, self.font_mid, True)
        self.text("Press R to play again   -   ESC to quit", (cx, 390), TEXT, center=True)

    def render(self):
        if self.state == "title":
            self.draw_title()
        else:
            self.draw_map()
            self.draw_panel()
            if self.game.state != "playing":
                self.draw_end_screen()

    # ------------------------------------------------------------ main loop
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_key(event.key)
            self.render()
            pygame.display.flip()
            self.frame += 1
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    App().run()
    sys.exit()
