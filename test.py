import threading
import time
import pyautogui
import keyboard

time.sleep(2)

# Устанавливаем начальные и конечные координаты для двух линий
x_start1, y_start1 = 2068, 900
x_end1, y_end1 = 2798, 900
x_start2, y_start2 = 2068, 1000  # Вторая линия на 100 пикселей ниже первой
x_end2, y_end2 = 2798, 1000

# Шаг
step = 5

# Количество шагов для каждой линии
num_steps1 = (x_end1 - x_start1) // step + 1
num_steps2 = (x_end2 - x_start2) // step + 1

# Задержка между кликами (в секундах)
delay = 0.001  # 1 миллисекунда


# Функция для определения, является ли пиксель серым
def is_gray(pixel):
    """Проверяет, является ли пиксель серым."""
    return pixel[1] < 10


def click_position(x_start, y_start, num_steps, stop_event):
    """Функция для кликов по одной линии."""
    for i in range(num_steps):
        x = x_start + i * step
        y = y_start

        if stop_event.is_set():
            break

        pixel_color = pyautogui.pixel(x, y)  # Получаем цвет пикселя
        if not is_gray(pixel_color):  # Если пиксель не серый, производим клик
            pyautogui.click(x, y)
            print(f"Нажали на ({x}, {y}), {pixel_color}")
        else:
            print(f"Пропущен серый пиксель на ({x}, {y}), {pixel_color}")

        time.sleep(delay)


# Создаем событие для остановки потоков
stop_event = threading.Event()

# Создаем и запускаем потоки для кликов по двум линиям
threads = []
thread1 = threading.Thread(target=click_position, args=(x_start1, y_start1, num_steps1, stop_event))
thread2 = threading.Thread(target=click_position, args=(x_start2, y_start2, num_steps2, stop_event))

threads.append(thread1)
threads.append(thread2)

thread1.start()
thread2.start()


# Функция для обработки нажатия Esc
def check_escape():
    keyboard.wait('esc')
    stop_event.set()


# Запускаем поток для отслеживания нажатия клавиши Esc
esc_thread = threading.Thread(target=check_escape)
esc_thread.start()

# Ожидаем завершения всех потоков
for thread in threads:
    thread.join()

print("Программа завершена.")


# # Функция для определения, является ли пиксель серым
# def is_gray(pixel):
#     """Проверяет, является ли пиксель серым."""
#     return pixel[1] < 10