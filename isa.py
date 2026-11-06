import pygame
import math
import sys

pygame.init()

WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TANK BATTLE - PART 1")

clock = pygame.time.Clock()

WHITE = (240, 240, 240)
GREEN = (55, 190, 90)
BLACK = (25, 30, 35)

player = pygame.Vector2(550, 350)
player_angle = 0
player_speed = 260

font = pygame.font.SysFont("Arial", 25, bold=True)


def draw_tank(position, angle, turret_angle):

    body = pygame.Surface((64, 64), pygame.SRCALPHA)

    pygame.draw.rect(
        body, (35, 38, 40),
        (5, 5, 54, 54), border_radius=9
    )

    pygame.draw.rect(
        body, GREEN,
        (13, 10, 38, 44), border_radius=9
    )

    pygame.draw.circle(body, GREEN, (32, 32), 12)
    pygame.draw.circle(body, BLACK, (32, 32), 7)

    rotated = pygame.transform.rotate(body, -angle)

    rect = rotated.get_rect(
        center=(int(position.x), int(position.y))
    )

    screen.blit(rotated, rect)

    direction = pygame.Vector2(
        math.cos(turret_angle),
        math.sin(turret_angle)
    )

    pygame.draw.line(
        screen, BLACK,
        position,
        position + direction * 35,
        9
    )


while True:

    dt = min(clock.tick(60) / 1000, 0.04)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    movement = pygame.Vector2(0, 0)

    if keys[pygame.K_w]:
        movement.y -= 1

    if keys[pygame.K_s]:
        movement.y += 1

    if keys[pygame.K_a]:
        movement.x -= 1

    if keys[pygame.K_d]:
        movement.x += 1

    if movement.length_squared() > 0:

        movement = movement.normalize()

        player += movement * player_speed * dt

        player_angle = math.degrees(
            math.atan2(movement.y, movement.x)
        )

    player.x = max(32, min(WIDTH - 32, player.x))
    player.y = max(32, min(HEIGHT - 32, player.y))

    mouse = pygame.Vector2(pygame.mouse.get_pos())

    direction = mouse - player

    turret_angle = math.atan2(direction.y, direction.x)

    screen.fill((29, 38, 43))

    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (38, 47, 51),
                         (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (38, 47, 51),
                         (0, y), (WIDTH, y))

    draw_tank(player, player_angle, turret_angle)

    text = font.render("WASD - MOVE | MOUSE - TURRET",
                       True, WHITE)

    screen.blit(text, (20, 20))

    pygame.display.flip()