import pygame
import random
import sys

# ---------------------- КОНСТАНТЫ ----------------------
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
GRID_SIZE = 20

BOARD_BACKGROUND_COLOR = (0, 0, 0)  # Чёрный фон
SNAKE_COLOR = (0, 255, 0)          # Зелёный цвет змейки
APPLE_COLOR = (255, 0, 0)          # Красный цвет яблока

# Направления движения (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


def handle_keys(snake):
    """
    Обрабатывает события от клавиатуры и устанавливает для змейки
    новое направление движения (snake.next_direction).

    :param snake: объект класса Snake
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT


class GameObject:
    """
    Базовый класс для игровых объектов. Содержит общие атрибуты и метод draw,
    который переопределяется в потомках.
    """

    def __init__(self, position=None, body_color=None):
        """
        Инициализирует базовые атрибуты.

        :param position: кортеж (x, y), позиция объекта
        :param body_color: цвет объекта, кортеж (R, G, B)
        """
        if position is None:
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """
        Отрисовывает объект на поверхности surface. Должен быть переопределён
        в дочерних классах.

        :param surface: поверхность для рисования
        """
        pass


class Apple(GameObject):
    """
    Класс, описывающий яблоко на игровом поле.
    Наследуется от GameObject.
    """

    def __init__(self):
        """
        Инициализирует яблоко:
        - Задаёт красный цвет.
        - Сразу случайно позиционирует.
        """
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает для яблока случайную позицию. Позиция кратна GRID_SIZE
        и не выходит за границы экрана.
        """
        x = random.randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """
        Отрисовывает яблоко в виде квадрата 20x20 (GRID_SIZE).

        :param surface: поверхность для рисования
        """
        rect = pygame.Rect(self.position[0], self.position[1],
                           GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """Класс, описывающий змейку. Наследуется от GameObject."""

    def __init__(self):
        """
        Инициализирует змейку:
        - Длина = 1.
        - Начальная позиция = центр экрана.
        - Направление = вправо.
        - next_direction = None.
        - Начальный цвет = зелёный.
        """
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 1
        # Список сегментов: голова + тело
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None  # Для "стирания" хвоста

    def get_head_position(self):
        """
        Возвращает позицию головы змейки (первый элемент positions).

        :return: (x, y) — координаты головы
        """
        return self.positions[0]

    def update_direction(self):
        """
        Обновляет направление движения змейки на основе self.next_direction,
        если оно не приводит к развороту на 180°.
        """
        if self.next_direction is not None:
            cur_dx, cur_dy = self.direction
            new_dx, new_dy = self.next_direction
            if (cur_dx + new_dx, cur_dy + new_dy) != (0, 0):
                self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """
        Сдвигает змейку на одну клетку согласно текущему направлению.
        Учитывает "оборачивание" за границы экрана.
        При столкновении с собой сбрасывает игру.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Столкновение с собой (кроме первых двух элементов: голова и "шея")
        if new_head in self.positions[2:]:
            self.reset()
            return

        self.positions.insert(0, new_head)

        # Убираем хвост, если длина превышена
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self, surface):
        """
        Отрисовывает змейку (все сегменты).
        Стирает хвост, если self.last не None.

        :param surface: поверхность для рисования
        """
        if self.last is not None:
            tail_rect = pygame.Rect(self.last[0], self.last[1],
                                    GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, tail_rect)
            self.last = None

        for pos in self.positions:
            rect = pygame.Rect(pos[0], pos[1], GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)

    def reset(self):
        """
        Сбрасывает змейку в исходное состояние:
        - Длина = 1.
        - Позиция = центр экрана.
        - Случайное направление.
        """
        self.length = 1
        center_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [center_pos]
        self.position = center_pos
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None


def main():
    """
    Основная функция, запускающая игру:
    - Инициализирует Pygame и окно.
    - Создаёт объекты змейки и яблока.
    - Запускает игровой цикл.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Изгиб Питона — классическая Змейка")
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()
        clock.tick(20)


if __name__ == "__main__":
    main()
