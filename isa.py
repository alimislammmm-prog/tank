import pygame
import math
import sys

pygame.init()

WIDTH, HEIGHT = 1100, 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TANK BATTLE 2.2")

clock = pygame.time.Clock()

GREEN = (55, 190, 90)
WHITE = (240, 240, 240)

player = pygame.Vector2(550, 550)
player_angle = 0
player_speed = 260

def draw_tank(position, angle, color, turret_angle=None):

    body = pygame.Surface((64, 64), pygame.SRCALPHA)

    # Гусеницалар
    pygame.draw.rect(
        body, (35, 38, 40),
        (5, 5, 54, 54), border_radius=9
    )

    # Танктің корпусы
    pygame.draw.rect(
        body, color,
        (13, 10, 38, 44), border_radius=9
    )

    # Мұнара
    pygame.draw.circle(body, color, (32, 32), 12)
    pygame.draw.circle(body, (35, 40, 35), (32, 32), 7)

    rotated_body = pygame.transform.rotate(body, -angle)

    rect = rotated_body.get_rect(
        center=(int(position.x), int(position.y))
    )

    screen.blit(rotated_body, rect)

    # Танктің ұңғысы
    if turret_angle is not None:

        direction = pygame.Vector2(
            math.cos(turret_angle),
            math.sin(turret_angle)
        )

        end = position + direction * 35

        pygame.draw.line(
            screen, WHITE,
            position, end, 5
        )


# Негізгі ойын циклі
while True:

    dt = min(clock.tick(FPS) / 1000, 0.04)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill((29, 38, 43))

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

        movement = movement.normalize() * player_speed * dt

        player += movement

        player_angle = math.degrees(
            math.atan2(movement.y, movement.x)
        )

    # Мұнараны тышқан арқылы басқару
    mouse_position = pygame.Vector2(pygame.mouse.get_pos())

    turret_direction = mouse_position - player

    turret_angle = math.atan2(
        turret_direction.y,
        turret_direction.x
    )

    draw_tank(
        player,
        player_angle,
        GREEN,
        turret_angle
    )

    pygame.display.flip()