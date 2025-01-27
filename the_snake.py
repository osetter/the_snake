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

# Направления движения в формате (dx, dy)
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
    Базовый класс для игровых объектов.
    Содержит общие атрибуты и метод draw, который переопределяется в потомках.
    """
    def __init__(self, position=None, body_color=None):
        """
        Инициализирует базовые атрибуты.
        
        :param position: кортеж (x, y), задающий позицию объекта
        :param body_color: цвет объекта, кортеж (R, G, B)
        """
        # По умолчанию позиция — центр экрана.
        if position is None:
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position

        self.body_color = body_color

    def draw(self, surface):
        """
        Отрисовывает объект на поверхности surface.
        Должен быть переопределён в дочерних классах.
        
        :param surface: поверхность (screen) для рисования
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
          - Задаёт цвет (красный).
          - Вызывает метод для случайной установки позиции.
        """
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает для яблока случайную позицию на игровом поле.
        Позиция кратна GRID_SIZE и не выходит за границы экрана.
        """
        x = random.randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """
        Отрисовывает яблоко в виде заполненного квадрата 20x20 (GRID_SIZE).
        
        :param surface: поверхность (screen) для рисования
        """
        rect = pygame.Rect(self.position[0], self.position[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """
    Класс, описывающий змейку.
    Наследуется от GameObject.
    """
    def __init__(self):
        """
        Инициализирует змейку:
          - Длина = 1.
          - Начальная позиция = центр экрана (список из одной координаты).
          - Начальное направление — вправо.
          - Следующее направление — None (будет устанавливаться при нажатии клавиш).
          - Начальный цвет — зелёный.
        """
        super().__init__(body_color=SNAKE_COLOR)
        self.length = 1
        # Список всех сегментов змейки; изначально — только голова
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        # Позиция последнего сегмента, чтобы «затирать» след при движении
        self.last = None

    def get_head_position(self):
        """
        Возвращает позицию головы змейки (первый элемент списка positions).

        :return: (x, y) — координаты головы змейки
        """
        return self.positions[0]

    def update_direction(self):
        """
        Обновляет направление движения змейки на основе
        self.next_direction, если последнее допустимо.
        Запрещает движение «назад» (в противоположную сторону).
        """
        if self.next_direction is not None:
            # Текущее направление
            cur_dx, cur_dy = self.direction
            # Новое направление
            new_dx, new_dy = self.next_direction

            # Запрещаем разворот на 180 градусов:
            # (cur_dx, cur_dy) и (new_dx, new_dy) не должны быть инверсией друг друга
            if (cur_dx + new_dx, cur_dy + new_dy) != (0, 0):
                self.direction = self.next_direction

            # Сбросим next_direction, чтобы не «зависать» на ней
            self.next_direction = None

    def move(self):
        """
        Двигает змейку на одну клетку в текущем направлении.
        Добавляет новую голову в начало списка positions и, если
        длина змейки не увеличилась, удаляет последний сегмент.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Рассчитываем новую позицию головы с учётом «оборачивания» за края
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Проверяем столкновение с собой (исключаем позицию головы)
        # Если новая голова совпадает с любым сегментом (кроме самой старой хвостовой
        # при движении), значит, произошло столкновение.
        if new_head in self.positions[2:]:
            self.reset()
            return

        # Добавляем новую голову
        self.positions.insert(0, new_head)

        # Если длина превышает текущее максимальное значение, хвост не удаляем,
        # значит, змейка «выросла» после яблока.
        if len(self.positions) > self.length:
            # Запоминаем последний сегмент для «стирания» следа
            self.last = self.positions.pop()

    def draw(self, surface):
        """
        Отрисовывает все сегменты змейки. Также «затирает» след
        (рисует чёрный квадрат на месте последнего сегмента).
        
        :param surface: поверхность (screen) для рисования
        """
        # Стираем «хвост», если last не None.
        if self.last is not None:
            tail_rect = pygame.Rect(self.last[0], self.last[1], GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, tail_rect)
            self.last = None  # Сбросим, чтобы не стирать каждый раз

        # Отрисовываем все сегменты змейки
        for pos in self.positions:
            rect = pygame.Rect(pos[0], pos[1], GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)

    def reset(self):
        """
        Сбрасывает змейку в исходное состояние после столкновения с собой.
        Устанавливает длину = 1, позицию — центр экрана и случайное начальное направление.
        """
        self.length = 1
        # Снова только голова в центре
        center_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [center_pos]
        self.position = center_pos

        # Случайное новое направление (UP, DOWN, LEFT, RIGHT)
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None


def main():
    """
    Основная функция, запускающая игру.
    Инициализирует Pygame, создаёт объекты Snake и Apple,
    запускает игровой цикл.
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Изгиб Питона — классическая Змейка")
    clock = pygame.time.Clock()

    # Создаём змейку и яблоко
    snake = Snake()
    apple = Apple()

    while True:
        # 1. Обработка нажатий клавиш
        handle_keys(snake)

        # 2. Обновление направления (учитываем next_direction)
        snake.update_direction()

        # 3. Движение змейки
        snake.move()

        # 4. Проверка, съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            # Увеличиваем длину змейки на 1
            snake.length += 1
            # Перемещаем яблоко на новую случайную позицию
            apple.randomize_position()

        # 5. Отрисовка фона
        # Вместо полной заливки можем затирать хвост через snake.draw(),
        # но иногда полезно обновить весь фон, чтобы «убрать артефакты».
        # screen.fill(BOARD_BACKGROUND_COLOR)

        # 6. Отрисовка объектов
        apple.draw(screen)
        snake.draw(screen)

        # 7. Обновление экрана
        pygame.display.update()

        # Ограничиваем частоту кадров
        clock.tick(20)


if __name__ == "__main__":
    main()
