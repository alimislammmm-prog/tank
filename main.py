<<<<<<< HEAD
# 1111
import pygame
import random
import math
import sys

pygame.init()

# =========================
# НАСТРОЙКИ ИГРЫ
# =========================

WIDTH, HEIGHT = 1100, 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TANK BATTLE 2.2")

clock = pygame.time.Clock()

WHITE = (240, 240, 240)
BLACK = (15, 18, 23)
GREEN = (55, 190, 90)
RED = (220, 65, 65)
YELLOW = (255, 210, 60)
GRAY = (90, 100, 110)

font = pygame.font.SysFont("Arial", 25, bold=True)
big_font = pygame.font.SysFont("Arial", 65, bold=True)

# =========================
# ИГРОВЫЕ ПЕРЕМЕННЫЕ
# =========================

player = pygame.Vector2(550, 550)
player_angle = 0
player_speed = 260

health = 100
score = 0

bullets = []
enemies = []
particles = []

game_state = "menu"

shoot_delay = 0
enemy_timer = 0
level = 1

# =========================
# КАРТА
# =========================

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

# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def draw_text(text, font_obj, color, x, y):
    image = font_obj.render(text, True, color)
    screen.blit(image, (x, y))


def create_particles(position, color):
    for _ in range(12):
        direction = pygame.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        )

        if direction.length_squared() > 0:
            direction = direction.normalize()

        particles.append({
            "pos": pygame.Vector2(position),
            "vel": direction * random.randint(50, 180),
            "life": 0.5,
            "color": color
        })


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


# =========================
# РИСОВАНИЕ ТАНКА
# =========================

def draw_tank(position, angle, color, turret_angle=None):
    body = pygame.Surface((64, 64), pygame.SRCALPHA)

    # Гусеницы
    pygame.draw.rect(
        body, (35, 38, 40),
        (5, 5, 54, 54), border_radius=9
    )

    # Корпус
    pygame.draw.rect(
        body, color,
        (13, 10, 38, 44), border_radius=9
    )

    # Детали корпуса
    pygame.draw.rect(
        body, (100, 110, 100),
        (17, 15, 30, 34), border_radius=6
    )

    pygame.draw.line(
        body, (25, 30, 30),
        (21, 14), (21, 50), 3
    )

    pygame.draw.line(
        body, (25, 30, 30),
        (43, 14), (43, 50), 3
    )

    # Башня
    pygame.draw.circle(body, color, (32, 32), 12)
    pygame.draw.circle(body, (35, 40, 35), (32, 32), 7)

    rotated_body = pygame.transform.rotate(body, -angle)

    rect = rotated_body.get_rect(
        center=(int(position.x), int(position.y))
    )

    screen.blit(rotated_body, rect)

    # Ствол башни
    if turret_angle is not None:

        direction = pygame.Vector2(
            math.cos(turret_angle),
            math.sin(turret_angle)
        )

        start = position
        end = position + direction * 35

        pygame.draw.line(
            screen, (35, 40, 35),
            start, end, 9
        )

        pygame.draw.line(
            screen, (180, 190, 170),
            start, end, 4
        )


# =========================
# СОЗДАНИЕ ВРАГОВ
# =========================

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
                    "speed": random.randint(85, 120) + level * 5,
                    "cooldown": random.uniform(0.5, 2)
                })

                return


# =========================
# СТРЕЛЬБА ИГРОКА
# =========================

def player_shoot(mouse_position):

    global shoot_delay

    if shoot_delay > 0:
        return

    direction = pygame.Vector2(mouse_position) - player

    if direction.length_squared() == 0:
        return

    direction = direction.normalize()

    bullets.append({
        "pos": player + direction * 35,
        "vel": direction * 650,
        "enemy": False,
        "damage": 1
    })

    shoot_delay = 0.22


# =========================
# СТРЕЛЬБА ВРАГОВ
# =========================

def enemy_shoot(enemy):

    direction = player - enemy["pos"]

    if direction.length_squared() == 0:
        return

    direction = direction.normalize()

    bullets.append({
        "pos": enemy["pos"] + direction * 30,
        "vel": direction * 350,
        "enemy": True,
        "damage": 10
    })


# =========================
# ПЕРЕЗАПУСК
# =========================

def reset_game():

    global player, health, score, bullets
    global enemies, particles, level
    global shoot_delay, enemy_timer

    player = pygame.Vector2(550, 550)

    health = 100
    score = 0
    level = 1

    bullets = []
    enemies = []
    particles = []

    shoot_delay = 0
    enemy_timer = 0


# =========================
# ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ
# =========================

while True:

    dt = min(clock.tick(FPS) / 1000, 0.04)

    mouse_position = pygame.Vector2(
        pygame.mouse.get_pos()
    )

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # Пауза
            if event.key == pygame.K_ESCAPE:

                if game_state == "playing":
                    game_state = "pause"

                elif game_state == "pause":
                    game_state = "playing"

            # Начало игры
            if event.key == pygame.K_RETURN:

                if game_state in (
                    "menu", "game_over", "victory"
                ):

                    reset_game()
                    game_state = "playing"

            # Перезапуск
            if event.key == pygame.K_r:

                if game_state in ("game_over", "victory"):

                    reset_game()
                    game_state = "playing"

    # =========================
    # ФОН
    # =========================

    screen.fill((29, 38, 43))

    for x in range(0, WIDTH, 40):

        pygame.draw.line(
            screen, (38, 47, 51),
            (x, 0), (x, HEIGHT)
        )

    for y in range(0, HEIGHT, 40):

        pygame.draw.line(
            screen, (38, 47, 51),
            (0, y), (WIDTH, y)
        )

    # =========================
    # ГЛАВНОЕ МЕНЮ
    # =========================

    if game_state == "menu":

        draw_text(
            "TANK BATTLE",
            big_font, GREEN, 330, 190
        )

        draw_text(
            "2.2 EDITION",
            font, WHITE, 455, 270
        )

        draw_text(
            "WASD - движение",
            font, WHITE, 425, 370
        )

        draw_text(
            "МЫШЬ - направление башни",
            font, WHITE, 370, 415
        )

        draw_text(
            "ЛКМ - СТРЕЛЬБА",
            font, YELLOW, 430, 460
        )

        draw_text(
            "ENTER - НАЧАТЬ ИГРУ",
            font, YELLOW, 390, 550
        )

    # =========================
    # ИГРОВОЙ ПРОЦЕСС
    # =========================

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

            movement = (
                movement.normalize() * player_speed * dt
            )

            player = move_tank(
                player, movement, 23
            )

            player_angle = math.degrees(
                math.atan2(movement.y, movement.x)
            )

        # Направление башни
        turret_direction = mouse_position - player

        turret_angle = math.atan2(
            turret_direction.y,
            turret_direction.x
        )

        # ВЫСТРЕЛ ЛЕВОЙ КНОПКОЙ МЫШИ
        shoot_delay = max(0, shoot_delay - dt)

        if pygame.mouse.get_pressed()[0]:
            player_shoot(mouse_position)

        # Создание врагов
        enemy_timer += dt

        if enemy_timer >= max(0.7, 2.3 - level * 0.12):

            if len(enemies) < 3 + level:
                spawn_enemy()

            enemy_timer = 0

        # Движение врагов
        for enemy in enemies[:]:

            direction = player - enemy["pos"]

            distance = direction.length()

            if distance > 0:

                direction = direction.normalize()

                enemy["angle"] = math.degrees(
                    math.atan2(direction.y, direction.x)
                )

                if distance > 150:

                    movement = (
                        direction * enemy["speed"] * dt
                    )

                    enemy["pos"] = move_tank(
                        enemy["pos"], movement, 22
                    )

            # Вражеская стрельба
            enemy["cooldown"] -= dt

            if enemy["cooldown"] <= 0:

                enemy_shoot(enemy)

                enemy["cooldown"] = random.uniform(
                    1.2, 2.5
                )

        # Обработка пуль
        for bullet in bullets[:]:

            bullet["pos"] += bullet["vel"] * dt

            if not (
                0 < bullet["pos"].x < WIDTH
                and 0 < bullet["pos"].y < HEIGHT
            ):

                bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(
                bullet["pos"].x - 5,
                bullet["pos"].y - 5,
                10, 10
            )

            hit_wall = any(
                bullet_rect.colliderect(wall)
                for wall in walls
            )

            if hit_wall:

                create_particles(
                    bullet["pos"], YELLOW
                )

                bullets.remove(bullet)
                continue

            # Попадание во врага
            if bullet["enemy"]:

                if bullet["pos"].distance_to(player) < 23:

                    health -= bullet["damage"]

                    create_particles(player, RED)

                    bullets.remove(bullet)

            # Попадание игрока во врага
            else:

                for enemy in enemies[:]:

                    if bullet["pos"].distance_to(
                        enemy["pos"]
                    ) < 23:

                        enemy["health"] -= bullet["damage"]

                        create_particles(
                            bullet["pos"], YELLOW
                        )

                        bullets.remove(bullet)

                        if enemy["health"] <= 0:

                            enemies.remove(enemy)

                            score += 100

                            create_particles(
                                enemy["pos"], RED
                            )

                        break

        # Уровни
        new_level = score // 500 + 1

        if new_level > level:
            level = new_level

        # Победа и поражение
        if health <= 0:
            game_state = "game_over"

        if score >= 2000:
            game_state = "victory"

    # =========================
    # ПАУЗА
    # =========================

    elif game_state == "pause":

        draw_text(
            "PAUSE", big_font, YELLOW, 430, 270
        )

        draw_text(
            "ESC - ПРОДОЛЖИТЬ",
            font, WHITE, 410, 380
        )

    # =========================
    # ПОРАЖЕНИЕ
    # =========================

    elif game_state == "game_over":

        draw_text(
            "GAME OVER", big_font, RED, 340, 260
        )

        draw_text(
            f"ТВОЙ СЧЁТ: {score}",
            font, WHITE, 440, 350
        )

        draw_text(
            "ENTER - ИГРАТЬ СНОВА",
            font, YELLOW, 385, 430
        )

    # =========================
    # ПОБЕДА
    # =========================

    elif game_state == "victory":

        draw_text(
            "VICTORY!", big_font, GREEN, 395, 260
        )

        draw_text(
            f"ТВОЙ СЧЁТ: {score}",
            font, WHITE, 440, 350
        )

        draw_text(
            "ENTER - ИГРАТЬ СНОВА",
            font, YELLOW, 385, 430
        )

    # =========================
    # ОТРИСОВКА КАРТЫ
    # =========================

    for wall in walls:

        pygame.draw.rect(
            screen, (70, 85, 85),
            wall, border_radius=5
        )

        pygame.draw.rect(
            screen, (110, 130, 125),
            wall, 2, border_radius=5
        )

    # =========================
    # ТАНКИ
    # =========================

    if game_state != "menu":

        draw_tank(
            player,
            player_angle,
            GREEN,
            turret_angle if game_state == "playing" else None
        )

    for enemy in enemies:

        draw_tank(
            enemy["pos"],
            enemy["angle"],
            RED
        )

    # =========================
    # ПУЛИ
    # =========================

    for bullet in bullets:

        color = RED if bullet["enemy"] else YELLOW

        pygame.draw.circle(
            screen,
            color,
            (
                int(bullet["pos"].x),
                int(bullet["pos"].y)
            ),
            6
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(bullet["pos"].x),
                int(bullet["pos"].y)
            ),
            2
        )

    # =========================
    # ЧАСТИЦЫ
    # =========================

    for particle in particles[:]:

        particle["pos"] += particle["vel"] * dt

        particle["life"] -= dt

        if particle["life"] <= 0:

            particles.remove(particle)
            continue

        pygame.draw.circle(
            screen,
            particle["color"],
            (
                int(particle["pos"].x),
                int(particle["pos"].y)
            ),
            3
        )

    # =========================
    # ИНТЕРФЕЙС
    # =========================

    pygame.draw.rect(
        screen, (20, 25, 30),
        (0, 0, WIDTH, 65)
    )

    draw_text(
        f"SCORE: {score}",
        font, WHITE, 25, 18
    )

    draw_text(
        f"LEVEL: {level}",
        font, YELLOW, 260, 18
    )

    draw_text(
        "HP", font, WHITE, 790, 18
    )

    pygame.draw.rect(
        screen, RED,
        (850, 23, 180, 20)
    )

    pygame.draw.rect(
        screen, GREEN,
        (850, 23, 180 * max(0, health) / 100, 20)
    )

    pygame.draw.rect(
        screen, WHITE,
        (850, 23, 180, 20), 2
    )

    pygame.display.flip()
=======

import pygame
import random
import math
import sys

pygame.init()

# =========================
# НАСТРОЙКИ ИГРЫ
# =========================

WIDTH, HEIGHT = 1100, 700
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TANK BATTLE 2.2")

clock = pygame.time.Clock()

WHITE = (240, 240, 240)
BLACK = (15, 18, 23)
GREEN = (55, 190, 90)
RED = (220, 65, 65)
YELLOW = (255, 210, 60)
GRAY = (90, 100, 110)

font = pygame.font.SysFont("Arial", 25, bold=True)
big_font = pygame.font.SysFont("Arial", 65, bold=True)

# =========================
# ИГРОВЫЕ ПЕРЕМЕННЫЕ
# =========================

player = pygame.Vector2(550, 550)
player_angle = 0
player_speed = 260

health = 100
score = 0

bullets = []
enemies = []
particles = []

game_state = "menu"

shoot_delay = 0
enemy_timer = 0
level = 1

# =========================
# КАРТА
# =========================

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

# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

def draw_text(text, font_obj, color, x, y):
    image = font_obj.render(text, True, color)
    screen.blit(image, (x, y))


def create_particles(position, color):
    for _ in range(12):
        direction = pygame.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        )

        if direction.length_squared() > 0:
            direction = direction.normalize()

        particles.append({
            "pos": pygame.Vector2(position),
            "vel": direction * random.randint(50, 180),
            "life": 0.5,
            "color": color
        })


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


# =========================
# РИСОВАНИЕ ТАНКА
# =========================

def draw_tank(position, angle, color, turret_angle=None):
    body = pygame.Surface((64, 64), pygame.SRCALPHA)

    # Гусеницы
    pygame.draw.rect(
        body, (35, 38, 40),
        (5, 5, 54, 54), border_radius=9
    )

    # Корпус
    pygame.draw.rect(
        body, color,
        (13, 10, 38, 44), border_radius=9
    )

    # Детали корпуса
    pygame.draw.rect(
        body, (100, 110, 100),
        (17, 15, 30, 34), border_radius=6
    )

    pygame.draw.line(
        body, (25, 30, 30),
        (21, 14), (21, 50), 3
    )

    pygame.draw.line(
        body, (25, 30, 30),
        (43, 14), (43, 50), 3
    )

    # Башня
    pygame.draw.circle(body, color, (32, 32), 12)
    pygame.draw.circle(body, (35, 40, 35), (32, 32), 7)

    rotated_body = pygame.transform.rotate(body, -angle)

    rect = rotated_body.get_rect(
        center=(int(position.x), int(position.y))
    )

    screen.blit(rotated_body, rect)

    # Ствол башни
    if turret_angle is not None:

        direction = pygame.Vector2(
            math.cos(turret_angle),
            math.sin(turret_angle)
        )

        start = position
        end = position + direction * 35

        pygame.draw.line(
            screen, (35, 40, 35),
            start, end, 9
        )

        pygame.draw.line(
            screen, (180, 190, 170),
            start, end, 4
        )


# =========================
# СОЗДАНИЕ ВРАГОВ
# =========================

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
                    "speed": random.randint(85, 120) + level * 5,
                    "cooldown": random.uniform(0.5, 2)
                })

                return


# =========================
# СТРЕЛЬБА ИГРОКА
# =========================

def player_shoot(mouse_position):

    global shoot_delay

    if shoot_delay > 0:
        return

    direction = pygame.Vector2(mouse_position) - player

    if direction.length_squared() == 0:
        return

    direction = direction.normalize()

    bullets.append({
        "pos": player + direction * 35,
        "vel": direction * 650,
        "enemy": False,
        "damage": 1
    })

    shoot_delay = 0.22


# =========================
# СТРЕЛЬБА ВРАГОВ
# =========================

def enemy_shoot(enemy):

    direction = player - enemy["pos"]

    if direction.length_squared() == 0:
        return

    direction = direction.normalize()

    bullets.append({
        "pos": enemy["pos"] + direction * 30,
        "vel": direction * 350,
        "enemy": True,
        "damage": 10
    })


# =========================
# ПЕРЕЗАПУСК
# =========================

def reset_game():

    global player, health, score, bullets
    global enemies, particles, level
    global shoot_delay, enemy_timer

    player = pygame.Vector2(550, 550)

    health = 100
    score = 0
    level = 1

    bullets = []
    enemies = []
    particles = []

    shoot_delay = 0
    enemy_timer = 0


# =========================
# ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ
# =========================

while True:

    dt = min(clock.tick(FPS) / 1000, 0.04)

    mouse_position = pygame.Vector2(
        pygame.mouse.get_pos()
    )

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            # Пауза
            if event.key == pygame.K_ESCAPE:

                if game_state == "playing":
                    game_state = "pause"

                elif game_state == "pause":
                    game_state = "playing"

            # Начало игры
            if event.key == pygame.K_RETURN:

                if game_state in (
                    "menu", "game_over", "victory"
                ):

                    reset_game()
                    game_state = "playing"

            # Перезапуск
            if event.key == pygame.K_r:

                if game_state in ("game_over", "victory"):

                    reset_game()
                    game_state = "playing"

    # =========================
    # ФОН
    # =========================

    screen.fill((29, 38, 43))

    for x in range(0, WIDTH, 40):

        pygame.draw.line(
            screen, (38, 47, 51),
            (x, 0), (x, HEIGHT)
        )

    for y in range(0, HEIGHT, 40):

        pygame.draw.line(
            screen, (38, 47, 51),
            (0, y), (WIDTH, y)
        )

    # =========================
    # ГЛАВНОЕ МЕНЮ
    # =========================

    if game_state == "menu":

        draw_text(
            "TANK BATTLE",
            big_font, GREEN, 330, 190
        )

        draw_text(
            "2.2 EDITION",
            font, WHITE, 455, 270
        )

        draw_text(
            "WASD - движение",
            font, WHITE, 425, 370
        )

        draw_text(
            "МЫШЬ - направление башни",
            font, WHITE, 370, 415
        )

        draw_text(
            "ЛКМ - СТРЕЛЬБА",
            font, YELLOW, 430, 460
        )

        draw_text(
            "ENTER - НАЧАТЬ ИГРУ",
            font, YELLOW, 390, 550
        )

    # =========================
    # ИГРОВОЙ ПРОЦЕСС
    # =========================

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

            movement = (
                movement.normalize() * player_speed * dt
            )

            player = move_tank(
                player, movement, 23
            )

            player_angle = math.degrees(
                math.atan2(movement.y, movement.x)
            )

        # Направление башни
        turret_direction = mouse_position - player

        turret_angle = math.atan2(
            turret_direction.y,
            turret_direction.x
        )

        # ВЫСТРЕЛ ЛЕВОЙ КНОПКОЙ МЫШИ
        shoot_delay = max(0, shoot_delay - dt)

        if pygame.mouse.get_pressed()[0]:
            player_shoot(mouse_position)

        # Создание врагов
        enemy_timer += dt

        if enemy_timer >= max(0.7, 2.3 - level * 0.12):

            if len(enemies) < 3 + level:
                spawn_enemy()

            enemy_timer = 0

        # Движение врагов
        for enemy in enemies[:]:

            direction = player - enemy["pos"]

            distance = direction.length()

            if distance > 0:

                direction = direction.normalize()

                enemy["angle"] = math.degrees(
                    math.atan2(direction.y, direction.x)
                )

                if distance > 150:

                    movement = (
                        direction * enemy["speed"] * dt
                    )

                    enemy["pos"] = move_tank(
                        enemy["pos"], movement, 22
                    )

            # Вражеская стрельба
            enemy["cooldown"] -= dt

            if enemy["cooldown"] <= 0:

                enemy_shoot(enemy)

                enemy["cooldown"] = random.uniform(
                    1.2, 2.5
                )

        # Обработка пуль
        for bullet in bullets[:]:

            bullet["pos"] += bullet["vel"] * dt

            if not (
                0 < bullet["pos"].x < WIDTH
                and 0 < bullet["pos"].y < HEIGHT
            ):

                bullets.remove(bullet)
                continue

            bullet_rect = pygame.Rect(
                bullet["pos"].x - 5,
                bullet["pos"].y - 5,
                10, 10
            )

            hit_wall = any(
                bullet_rect.colliderect(wall)
                for wall in walls
            )

            if hit_wall:

                create_particles(
                    bullet["pos"], YELLOW
                )

                bullets.remove(bullet)
                continue

            # Попадание во врага
            if bullet["enemy"]:

                if bullet["pos"].distance_to(player) < 23:

                    health -= bullet["damage"]

                    create_particles(player, RED)

                    bullets.remove(bullet)

            # Попадание игрока во врага
            else:

                for enemy in enemies[:]:

                    if bullet["pos"].distance_to(
                        enemy["pos"]
                    ) < 23:

                        enemy["health"] -= bullet["damage"]

                        create_particles(
                            bullet["pos"], YELLOW
                        )

                        bullets.remove(bullet)

                        if enemy["health"] <= 0:

                            enemies.remove(enemy)

                            score += 100

                            create_particles(
                                enemy["pos"], RED
                            )

                        break

        # Уровни
        new_level = score // 500 + 1

        if new_level > level:
            level = new_level

        # Победа и поражение
        if health <= 0:
            game_state = "game_over"

        if score >= 2000:
            game_state = "victory"

    # =========================
    # ПАУЗА
    # =========================

    elif game_state == "pause":

        draw_text(
            "PAUSE", big_font, YELLOW, 430, 270
        )

        draw_text(
            "ESC - ПРОДОЛЖИТЬ",
            font, WHITE, 410, 380
        )

    # =========================
    # ПОРАЖЕНИЕ
    # =========================

    elif game_state == "game_over":

        draw_text(
            "GAME OVER", big_font, RED, 340, 260
        )

        draw_text(
            f"ТВОЙ СЧЁТ: {score}",
            font, WHITE, 440, 350
        )

        draw_text(
            "ENTER - ИГРАТЬ СНОВА",
            font, YELLOW, 385, 430
        )

    # =========================
    # ПОБЕДА
    # =========================

    elif game_state == "victory":

        draw_text(
            "VICTORY!", big_font, GREEN, 395, 260
        )

        draw_text(
            f"ТВОЙ СЧЁТ: {score}",
            font, WHITE, 440, 350
        )

        draw_text(
            "ENTER - ИГРАТЬ СНОВА",
            font, YELLOW, 385, 430
        )

    # =========================
    # ОТРИСОВКА КАРТЫ
    # =========================

    for wall in walls:

        pygame.draw.rect(
            screen, (70, 85, 85),
            wall, border_radius=5
        )

        pygame.draw.rect(
            screen, (110, 130, 125),
            wall, 2, border_radius=5
        )

    # =========================
    # ТАНКИ
    # =========================

    if game_state != "menu":

        draw_tank(
            player,
            player_angle,
            GREEN,
            turret_angle if game_state == "playing" else None
        )

    for enemy in enemies:

        draw_tank(
            enemy["pos"],
            enemy["angle"],
            RED
        )

    # =========================
    # ПУЛИ
    # =========================

    for bullet in bullets:

        color = RED if bullet["enemy"] else YELLOW

        pygame.draw.circle(
            screen,
            color,
            (
                int(bullet["pos"].x),
                int(bullet["pos"].y)
            ),
            6
        )

        pygame.draw.circle(
            screen,
            WHITE,
            (
                int(bullet["pos"].x),
                int(bullet["pos"].y)
            ),
            2
        )

    # =========================
    # ЧАСТИЦЫ
    # =========================

    for particle in particles[:]:

        particle["pos"] += particle["vel"] * dt

        particle["life"] -= dt

        if particle["life"] <= 0:

            particles.remove(particle)
            continue

        pygame.draw.circle(
            screen,
            particle["color"],
            (
                int(particle["pos"].x),
                int(particle["pos"].y)
            ),
            3
        )

    # =========================
    # ИНТЕРФЕЙС
    # =========================

    pygame.draw.rect(
        screen, (20, 25, 30),
        (0, 0, WIDTH, 65)
    )

    draw_text(
        f"SCORE: {score}",
        font, WHITE, 25, 18
    )

    draw_text(
        f"LEVEL: {level}",
        font, YELLOW, 260, 18
    )

    draw_text(
        "HP", font, WHITE, 790, 18
    )

    pygame.draw.rect(
        screen, RED,
        (850, 23, 180, 20)
    )

    pygame.draw.rect(
        screen, GREEN,
        (850, 23, 180 * max(0, health) / 100, 20)
    )

    pygame.draw.rect(
        screen, WHITE,
        (850, 23, 180, 20), 2
    )

    pygame.display.flip()
>>>>>>> ac5513964ff78330dbe5fc0059eb6388d1644b68
