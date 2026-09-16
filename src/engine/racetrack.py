import sys
import os
import importlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
import game
import debug
import config

# Dynamically load the active map's checkpoints and image
checkpoints = importlib.import_module(f"{config.ACTIVE_MAP}.checkpoints")
MAP_IMAGE_PATH = f"src/{config.ACTIVE_MAP}/map.png"

# ── Init ─────────────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((1080, 720))
pygame.display.set_caption("Racetrack — Player Mode")
clock = pygame.time.Clock()
dt = 0.0
debug_font = pygame.font.SysFont(None, 28)
hud_font   = pygame.font.SysFont(None, 30)
show_debug = False

MAX_SPEED = 200.0
ACCEL     = 280.0   # units / s²  (acceleration while holding W)
BRAKE     = 500.0   # units / s²  (deceleration while holding S)
COAST     = 140.0   # units / s²  (passive deceleration)

track_map = game.Track(MAP_IMAGE_PATH)

def make_player():
    start_x, start_y = getattr(checkpoints, 'START_POS', (83, 325))
    p = game.Player("images/car.png", start_x, start_y)
    p.current_speed = 0.0
    return p

player  = make_player()
crashed = False
lap_time = 0.0
running  = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                show_debug = not show_debug
            if event.key == pygame.K_r and crashed:
                player   = make_player()
                crashed  = False
                lap_time = 0.0

    if not crashed:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            player.rotate( 300 * dt)
        if keys[pygame.K_d]:
            player.rotate(-300 * dt)

        if keys[pygame.K_w]:
            player.current_speed = min(player.current_speed + ACCEL * dt, MAX_SPEED)
        elif keys[pygame.K_s]:
            player.current_speed = max(player.current_speed - BRAKE * dt, 0.0)
        else:
            player.current_speed = max(player.current_speed - COAST * dt, 0.0)

        if player.move(player.current_speed, dt, track_map):
            crashed = True
            player.current_speed = 0.0

        if player.check_checkpoints(checkpoints.checkpoints):
            player.laps += 1
            lap_time = 0.0

        lap_time                        += dt
        player.current_lap_time          = lap_time
        player.time_since_last_checkpoint += dt

    screen.fill((48, 51, 53))
    screen.blit(track_map.image, (0, 0))
    screen.blit(player.image, player.rect.topleft)

    total_cps = len(checkpoints.checkpoints)
    hud_lines = [
        f"Lap:         {player.laps + 1}",
        f"Checkpoint:  {player.current_checkpoint} / {total_cps}",
        f"Speed:       {int(player.current_speed)}",
        f"Lap time:    {lap_time:.2f}s",
    ]
    for i, text in enumerate(hud_lines):
        surf = hud_font.render(text, True, (230, 230, 230))
        screen.blit(surf, (12, 12 + i * 26))

    if crashed:
        overlay = pygame.Surface((1080, 720), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))
        big   = pygame.font.SysFont(None, 58)
        small = pygame.font.SysFont(None, 32)
        crash_surf = big.render("CRASHED!", True, (255, 80, 80))
        hint_surf  = small.render("Press  R  to restart", True, (200, 200, 200))
        cx = 540
        screen.blit(crash_surf, (cx - crash_surf.get_width() // 2, 320))
        screen.blit(hint_surf,  (cx - hint_surf.get_width()  // 2, 390))

    if show_debug:
        debug.draw_fps(screen, clock, debug_font)
        debug.draw_pos_info(screen, player, debug_font)
        debug.draw_mouse_pos(screen, debug_font)
        for cp in checkpoints.checkpoints:
            pygame.draw.rect(screen, (0, 255, 0), cp, 2)
        if pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            player.pos_x, player.pos_y = float(mx), float(my)
            player.rect.centerx = round(player.pos_x)
            player.rect.centery = round(player.pos_y)

    pygame.display.flip()
    dt = clock.tick(100) / 1000

pygame.quit()