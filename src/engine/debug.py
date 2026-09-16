import pygame
import game

def draw_fps(screen, clock, font):
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

def draw_pos_info(screen, player, font):
    pos_text = font.render(f"Pos: ({int(player.pos_x)}, {int(player.pos_y)})", True, (255, 255, 255))
    angle_text = font.render(f"Angle: {int(player.angle % 360)}°", True, (255, 255, 255))
    
    screen.blit(pos_text, (10, 35))
    screen.blit(angle_text, (10, 60))

def draw_mouse_pos(screen, font):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_text = font.render(f"Mouse: ({mouse_x}, {mouse_y})", True, (255, 255, 255))
    screen.blit(mouse_text, (10, 85))

def draw_rays(screen, player, hit_points):
    """Draws lines from the player to where the raycasts hit the walls."""
    start_pos = (int(player.pos_x), int(player.pos_y))
    
    for hit_point in hit_points:
        pygame.draw.line(screen, (0, 255, 255), start_pos, hit_point, 2)
        pygame.draw.circle(screen, (255, 0, 255), hit_point, 4)