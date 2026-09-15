import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
import game
import debug
import map0.checkpoints as checkpoints

pygame.init()
screen = pygame.display.set_mode((1080, 720))
clock = pygame.time.Clock()
running = True
dt = 0
debug_font = pygame.font.SysFont(None, 28)
show_debug = False

sprites = pygame.sprite.Group()
player = game.Player("images/car.png", 83, 325)
sprites.add(player)

track_map = game.Track("src/map0/map.png")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                show_debug = not show_debug
        

    screen.fill((48, 51, 53))
    screen.blit(track_map.image, (0, 0))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        crashed = player.move(100, dt, track_map)
        if crashed and not show_debug:
            print("Crashed! Game Over.")
            running = False

    if keys[pygame.K_a]:
        player.rotate(300 * dt)
    
    if keys[pygame.K_d]:
        player.rotate(-300 * dt)

    sprites.draw(screen)
    
    laps = player.check_checkpoints(checkpoints.checkpoints)

    if laps > 0:
        player.laps += (int)(laps)
        print(f"Lap completed! Total laps: {player.laps}")
        # Update the player's lap count

    if show_debug:
        debug.draw_fps(screen, clock, debug_font)
        debug.draw_pos_info(screen, player, debug_font)
        debug.draw_mouse_pos(screen, debug_font)
        
        for checkpoint in checkpoints.checkpoints:
            pygame.draw.rect(screen, (0, 255, 0), checkpoint, 2) 
            
        if pygame.mouse.get_pressed()[0]:
            mouse_pos = pygame.mouse.get_pos()
            player.pos_x, player.pos_y = mouse_pos
            
            player.rect.centerx = round(player.pos_x)
            player.rect.centery = round(player.pos_y)

    pygame.display.flip()
    dt = clock.tick(60) / 1000 

pygame.quit()