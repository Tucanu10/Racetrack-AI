import pygame

pygame.init()
screen = pygame.display.set_mode((1080, 720))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((48, 51, 53))

    pygame.image.load("images/car.png")

    player_pos.y += 300 * dt  # Gravity effect

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        player_pos.y -= 500 * dt

    pygame.display.update()  # Update the display
    dt = clock.tick(60) / 1000 

pygame.quit()