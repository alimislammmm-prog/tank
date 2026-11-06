
import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TANK BATTLE - PART 2")

clock = pygame.time.Clock()

GREEN = (55, 190, 90)
RED = (220, 65, 65)
WHITE = (240, 240, 240)
YELLOW = (255, 210, 60)
BLACK = (25, 30, 35)

font = pygame.font.SysFont("Arial", 25, bold=True)

player = pygame.Vector2(550, 550)
player_angle = 0
player_speed = 260

bullets = []
enemies = []

score = 0
shoot_delay = 0
enemy_timer = 0


def draw_tank(position, angle, color, turret=None):

    body = pygame.Surface((64, 64), pygame.SRCALPHA)

    pygame.draw.rect(body, (35, 38, 40),
                     (5, 5, 54, 54), border_radius=9)

    pygame.draw.rect(body, color,
                     (13, 10, 38, 44), border_radius=9)

    pygame.draw.circle(body, color, (32, 32), 12)

    rotated = pygame.transform.rotate(body, -angle)

    rect = rotated.get_rect(center=position)

    screen.blit(rotated, rect)

    if turret is not None:

        direction = pygame.Vector2(
            math.cos(turret),
            math.sin(turret)
        )

        pygame.draw.line(
            screen, BLACK, position,
            position + direction * 35, 8
        )


def shoot(position, target, enemy=False):

    direction = pygame.Vector2(target) - position

    if direction.length_squared() == 0:
        return

    direction = direction.normalize()

    bullets.append({
        "pos": pygame.Vector2(position) + direction * 35,
        "vel": direction * (350 if enemy else 650),
        "enemy": enemy
    })


def spawn_enemy():

    positions = [
        (50, 50),
        (WIDTH - 50, 50),
        (50, HEIGHT - 50),
        (WIDTH - 50, HEIGHT - 50)
    ]

    position = pygame.Vector2(random.choice(positions))

    if position.distance_to(player) > 200:

        enemies.append({
            "pos": position,
            "angle": 0,
            "health": 2,
            "speed": 100,
            "cooldown": 1
        })


while True:

    dt = min(clock.tick(60) / 1000, 0.04)

    mouse = pygame.Vector2(pygame.mouse.get_pos())

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

    turret_angle = math.atan2(
        mouse.y - player.y,
        mouse.x - player.x
    )

    shoot_delay = max(0, shoot_delay - dt)

    if pygame.mouse.get_pressed()[0] and shoot_delay <= 0:

        shoot(player, mouse)

        shoot_delay = 0.22

    enemy_timer += dt

    if enemy_timer >= 2:

        if len(enemies) < 5:
            spawn_enemy()

        enemy_timer = 0

    for enemy in enemies[:]:

        direction = player - enemy["pos"]

        distance = direction.length()

        if distance > 0:

            direction = direction.normalize()

            enemy["angle"] = math.degrees(
                math.atan2(direction.y, direction.x)
            )

            if distance > 150:

                enemy["pos"] += direction * enemy["speed"] * dt

        enemy["cooldown"] -= dt

        if enemy["cooldown"] <= 0:

            shoot(enemy["pos"], player, True)

            enemy["cooldown"] = random.uniform(1.2, 2.5)

    for bullet in bullets[:]:

        bullet["pos"] += bullet["vel"] * dt

        if not (0 < bullet["pos"].x < WIDTH
                and 0 < bullet["pos"].y < HEIGHT):

            bullets.remove(bullet)
            continue

        if bullet["enemy"]:

            if bullet["pos"].distance_to(player) < 23:

                bullets.remove(bullet)

        else:

            for enemy in enemies[:]:

                if bullet["pos"].distance_to(enemy["pos"]) < 23:

                    enemy["health"] -= 1

                    bullets.remove(bullet)

                    if enemy["health"] <= 0:

                        enemies.remove(enemy)
                        score += 100

                    break

    screen.fill((29, 38, 43))

    draw_tank(player, player_angle, GREEN, turret_angle)

    for enemy in enemies:
        draw_tank(enemy["pos"], enemy["angle"], RED)

    for bullet in bullets:

        color = RED if bullet["enemy"] else YELLOW

        pygame.draw.circle(
            screen, color,
            (int(bullet["pos"].x), int(bullet["pos"].y)),
            6
        )

    text = font.render(f"SCORE: {score}", True, WHITE)

    screen.blit(text, (20, 20))

    pygame.display.flip()
