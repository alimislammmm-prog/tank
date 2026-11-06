import random

bullets = []
enemies = []

score = 0
health = 100
shoot_delay = 0

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

            enemies.append({
                "pos": position,
                "health": 2,
                "speed": 100,
                "cooldown": 1
            })

            return


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


# Ойын циклінің ішінде:

shoot_delay = max(0, shoot_delay - dt)

if pygame.mouse.get_pressed()[0]:
    player_shoot(pygame.mouse.get_pos())

# Қарсыластардың қозғалысы
for enemy in enemies:

    direction = player - enemy["pos"]

    if direction.length() > 150:

        direction = direction.normalize()

        enemy["pos"] += direction * enemy["speed"] * dt

    # Қарсыластың ату уақыты
    enemy["cooldown"] -= dt

    if enemy["cooldown"] <= 0:

        enemy_shoot(enemy)

        enemy["cooldown"] = random.uniform(1.2, 2.5)


# Оқтардың қозғалысы
for bullet in bullets[:]:

    bullet["pos"] += bullet["vel"] * dt

    if not (
        0 < bullet["pos"].x < WIDTH
        and 0 < bullet["pos"].y < HEIGHT
    ):

        bullets.remove(bullet)
        continue

    # Ойыншыға қарсылас оғы тисе
    if bullet["enemy"]:

        if bullet["pos"].distance_to(player) < 23:

            health -= bullet["damage"]
            bullets.remove(bullet)

    # Ойыншының оғы қарсыласқа тисе
    else:

        for enemy in enemies[:]:

            if bullet["pos"].distance_to(enemy["pos"]) < 23:

                enemy["health"] -= bullet["damage"]

                bullets.remove(bullet)

                if enemy["health"] <= 0:

                    enemies.remove(enemy)
                    score += 100

                break