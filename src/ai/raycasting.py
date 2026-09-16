import pygame
import math

def castrays(startx, starty, angle, track_mask, screen_width, screen_height, ray_len):
    rad = math.radians(angle)
    sin_rad = math.sin(rad)
    cos_rad = math.cos(rad)

    for dist in range(ray_len):
        checkx = int(startx - dist * sin_rad)
        checky = int(starty - dist * cos_rad)

        # Boundary checks replace the costly try-except block
        if checkx < 0 or checkx >= screen_width or checky < 0 or checky >= screen_height:
            return dist, (checkx, checky)

        if track_mask.get_at((checkx, checky)):
            return dist, (checkx, checky)

    endpoint = (int(startx - ray_len * sin_rad), int(starty - ray_len * cos_rad))
    return ray_len, endpoint

def get_data(player, track_mask, ray_len):
    angles = [player.angle + offset for offset in [-45, -30, -15, 0, 15, 30, 45]]
    distances = []
    hitpoints = []

    screen = pygame.display.get_surface()
    sw, sh = screen.get_width(), screen.get_height()

    for angle in angles:
        dist, point = castrays(player.pos_x, player.pos_y, angle, track_mask, sw, sh, ray_len)
        distances.append(dist)
        hitpoints.append(point)
    return distances, hitpoints