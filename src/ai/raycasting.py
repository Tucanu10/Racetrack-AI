import pygame
import math

def castrays(startx, starty, angle, track_mask, screen, ray_len):
    rad = math.radians(angle)

    for dist in range(ray_len):
        checkx = int(startx - dist * math.sin(rad))
        checky = int(starty - dist * math.cos(rad))

        if checkx < 0 or checkx >= screen.get_width() or checky < 0 or checky >= screen.get_height():
            return dist, (checkx, checky)

        try:
            if track_mask.get_at((checkx, checky)):
                return dist, (checkx, checky)
        except IndexError:
            pass

    endpoint = (int(startx - ray_len * math.sin(rad)), int(starty - ray_len * math.cos(rad)))
    return ray_len, endpoint

def get_data(player, track_mask, ray_len):
    angles = [player.angle + offset for offset in [-45, -30, -15, 0, 15, 30, 45]]
    distances = []
    hitpoints = []

    for angle in angles:
        dist, point = castrays(player.pos_x, player.pos_y, angle, track_mask, pygame.display.get_surface(), ray_len)
        distances.append(dist)
        hitpoints.append(point)
    return distances, hitpoints