# Ойын картасы
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


# Қабырғамен соқтығысуды тексеру
def circle_wall_collision(position, radius):

    for wall in walls:

        closest_x = max(
            wall.left,
            min(position.x, wall.right)
        )

        closest_y = max(
            wall.top,
            min(position.y, wall.bottom)
        )

        dx = position.x - closest_x
        dy = position.y - closest_y

        if dx * dx + dy * dy < radius * radius:
            return True

    return False


# Танктің қозғалысын шектеу
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


# Қабырғаларды экранға шығару
for wall in walls:

    pygame.draw.rect(
        screen,
        (70, 85, 85),
        wall,
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        (110, 130, 125),
        wall,
        2,
        border_radius=5
    )


# Деңгей жүйесі
level = score // 500 + 1


# Денсаулық көрсеткіші
pygame.draw.rect(
    screen, RED,
    (850, 23, 180, 20)
)

pygame.draw.rect(
    screen, GREEN,
    (850, 23, 180 * max(0, health) / 100, 20)
)


# Жеңіс және жеңіліс жүйесі
if health <= 0:

    game_state = "game_over"

if score >= 2000:

    game_state = "victory"


# Жеңіліс экраны
if game_state == "game_over":

    draw_text(
        "GAME OVER",
        big_font, RED, 340, 260
    )

    draw_text(
        f"TVOЙ СЧЁТ: {score}",
        font, WHITE, 440, 350
    )


# Жеңіс экраны
if game_state == "victory":

    draw_text(
        "VICTORY!",
        big_font, GREEN, 395, 260
    )

    draw_text(
        f"ТВОЙ СЧЁТ: {score}",
        font, WHITE, 440, 350
    )