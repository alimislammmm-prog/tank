
import pygame
import random
import math
import sys

pygame.init()

WIDTH, HEIGHT = 1100, 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("TANK BATTLE 2.2")

clock = pygame.time.Clock()

WHITE = (240, 240, 240)
GREEN = (55, 190, 90)
RED = (220, 65, 65)
YELLOW = (255, 210, 60)

font = pygame.font.SysFont("Arial", 25, bold=True)
big_font = pygame.font.SysFont("Arial", 65, bold=True)

player = pygame.Vector2(550, 550)

player_angle = 0
player_speed = 260

health = 100
score = 0
level = 1

bullets = []
enemies = []

game_state = "menu"

shoot_delay = 0
enemy_timer = 0

walls = [
    pygame.Rect(130, 120, 180, 35),
    pygame.Rect(420, 160, 35, 180),
    pygame.Rect(720, 100, 180, 35),
    pygame.Rect(850, 250, 35, 180),
    pygame.Rect(150, 400, 35, 150),
    pygame.Rect(370, 480, 180, 35),
    pygame.Rect(650, 430, 180, 35),
    pygame.Rect(920, 530, 100, 35)
]


def draw_text(text, font_obj, color, x, y):

    image = font_obj.render(text, True, color)

    screen.blit(image, (x, y))


def circle_wall_collision(position, radius):

    for wall in walls:

        closest_x = max(wall.left, min(position.x, wall.right))
        closest_y = max(wall.top, min(position.y, wall.bottom))

        dx = position.x - closest_x
        dy = position.y - closest_y

        if dx * dx + dy * dy < radius * radius:
            return True

    return False


def move_tank(position, movement, radius):

    new_position = pygame.Vector2(position)

    test_x = pygame.Vector2(
        new_position.x + movement.x,
        new_position.y
    )

    if not circle_wall_collision(test_x, radius):
        if radius < test_x.x < WIDTH - radius:
            new_position.x = test_x.x

    test_y = pygame.Vector2(
        new_position.x,
        new_position.y + movement.y
    )

    if not circle_wall_collision(test_y, radius):
        if radius < test_y.y < HEIGHT - radius:
            new_position.y = test_y.y

    return new_position


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
            screen, (35, 40, 35),
            position,
            position + direction * 35,
            8
        )


def reset_game():

    global player, health, score, level
    global bullets, enemies, shoot_delay, enemy_timer

    player = pygame.Vector2(550, 550)

    health = 100
    score = 0
    level = 1

    bullets = []
    enemies = []

    shoot_delay = 0
    enemy_timer = 0


def spawn_enemy():

    positions = [
        pygame.Vector2(50, 50),
        pygame.Vector2(WIDTH - 50, 50),
        pygame.Vector2(50, HEIGHT - 50),
        pygame.Vector2(WIDTH - 50, HEIGHT - 50)
    ]

    random.shuffle(positions)

    for position in positions:

        if position.distance_to(player) > 250:

            if not circle_wall_collision(position, 22):

                enemies.append({
                    "pos": position,
                    "angle": 0,
                    "health": 2 + level // 2,
                    "speed": 90 + level * 5,
                    "cooldown": 1
                })

                return


def shoot(position, target, enemy=False):

    direction = pygame.Vector2(target) - position

    if direction.length_squared() == 0:
        return

    direction = direction.normalize()

    bullets.append({
        "pos": pygame.Vector2(position) + direction * 30,
        "vel": direction * (350 if enemy else 650),
        "enemy": enemy
    })


while True:

    dt = min(clock.tick(60) / 1000, 0.04)

    mouse = pygame.Vector2(pygame.mouse.get_pos())

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:

                if game_state == "playing":
                    game_state = "pause"

                elif game_state == "pause":
                    game_state = "playing"

            if event.key == pygame.K_RETURN:

                if game_state in ("menu", "game_over", "victory"):

                    reset_game()
                    game_state = "playing"

    screen.fill((29, 38, 43))

    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (38, 47, 51),
                         (x, 0), (x, HEIGHT))

    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, (38, 47, 51),
                         (0, y), (WIDTH, y))

    if game_state == "menu":

        draw_text("TANK BATTLE", big_font, GREEN, 330, 190)
        draw_text("2.2 EDITION", font, WHITE, 455, 270)
        draw_text("WASD - MOVEMENT", font, WHITE, 405, 370)
        draw_text("MOUSE - TURRET", font, WHITE, 420, 415)
        draw_text("LEFT CLICK - SHOOT", font, YELLOW, 395, 460)
        draw_text("ENTER - START", font, YELLOW, 430, 550)

    elif game_state == "playing":

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

            player = move_tank(player, movement, 23)

            player_angle = math.degrees(
                math.atan2(movement.y, movement.x)
            )

        turret_angle = math.atan2(
            mouse.y - player.y,
            mouse.x - player.x
        )

        shoot_delay = max(0, shoot_delay - dt)

        if pygame.mouse.get_pressed()[0] and shoot_delay <= 0:

            shoot(player, mouse)

            shoot_delay = 0.22

        enemy_timer += dt

        if enemy_timer >= max(0.7, 2.3 - level * 0.12):

            if len(enemies) < 3 + level:
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

                    movement = direction * enemy["speed"] * dt

                    enemy["pos"] = move_tank(
                        enemy["pos"], movement, 22
                    )

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

            bullet_rect = pygame.Rect(
                bullet["pos"].x - 5,
                bullet["pos"].y - 5,
                10, 10
            )

            if any(bullet_rect.colliderect(wall) for wall in walls):

                bullets.remove(bullet)
                continue

            if bullet["enemy"]:

                if bullet["pos"].distance_to(player) < 23:

                    health -= 10

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

        level = score // 500 + 1

        if health <= 0:
            game_state = "game_over"

        if score >= 2000:
            game_state = "victory"

    elif game_state == "pause":

        draw_text("PAUSE", big_font, YELLOW, 430, 270)
        draw_text("ESC - CONTINUE", font, WHITE, 405, 380)

    elif game_state == "game_over":

        draw_text("GAME OVER", big_font, RED, 340, 260)

        draw_text(
            f"YOUR SCORE: {score}",
            font, WHITE, 430, 350
        )

        draw_text("ENTER - RESTART", font, YELLOW, 400, 430)

    elif game_state == "victory":

        draw_text("VICTORY!", big_font, GREEN, 395, 260)

        draw_text(
            f"YOUR SCORE: {score}",
            font, WHITE, 430, 350
        )

        draw_text("ENTER - RESTART", font, YELLOW, 400, 430)

    # Қабырғаларды салу

    for wall in walls:

        pygame.draw.rect(
            screen, (70, 85, 85),
            wall, border_radius=5
        )

        pygame.draw.rect(
            screen, (110, 130, 125),
            wall, 2, border_radius=5
        )

    # Танктерді салу

    if game_state != "menu":

        turret = None

        if game_state == "playing":
            turret = turret_angle

        draw_tank(player, player_angle, GREEN, turret)

    for enemy in enemies:

        draw_tank(
            enemy["pos"],
            enemy["angle"],
            RED
        )

    # Оқтарды салу

    for bullet in bullets:

        color = RED if bullet["enemy"] else YELLOW

        pygame.draw.circle(
            screen,
            color,
            (int(bullet["pos"].x), int(bullet["pos"].y)),
            6
        )

    # Интерфейс

    pygame.draw.rect(screen, (20, 25, 30),
                     (0, 0, WIDTH, 65))

    draw_text(f"SCORE: {score}", font, WHITE, 25, 18)

    draw_text(f"LEVEL: {level}", font, YELLOW, 260, 18)

    draw_text("HP", font, WHITE, 790, 18)

    pygame.draw.rect(screen, RED, (850, 23, 180, 20))

    pygame.draw.rect(
        screen, GREEN,
        (850, 23, 180 * max(0, health) / 100, 20)
    )

    pygame.draw.rect(screen, WHITE, (850, 23, 180, 20), 2)

    pygame.display.flip()
