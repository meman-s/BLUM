import pyautogui
import threading
import keyboard
import time

time.sleep(2)

# Устанавливаем начальные и конечные координаты
x_start, y_start = 2068, 900
x_end, y_end = 2798, 900

# Шаг
step = 5

# Количество шагов
num_steps = (x_end - x_start) // step + 1

# Задержка между кликами (в секундах)
delay = 0.001  # 1 миллисекунда


# Функция для определения, является ли пиксель серым
def is_gray(pixel):
    tolerance = 5
    """Проверяет, является ли пиксель серым."""
    # r, g, b = pixel
    return pixel[1] < 10


def click_position(x, y, stop_event):
    skip_next = 0  # Счетчик пропуска

    while not stop_event.is_set():
        # if skip_next > 0:
        #     # Пропускаем текущий пиксель
        #     skip_next -= 1
        #     continue
        pixel_color = pyautogui.pixel(x, y)  # Получаем цвет пикселя
        if not is_gray(pixel_color):  # Если пиксель не серый, производим клик
            pyautogui.click(x, y)
            print(f"Нажали на ({x}, {y}), {pixel_color}")
        else:
            # skip_next = 1 # Пропускаем следующие 5 пикселей

            time.sleep(0.1)


# Создаем событие для остановки потоков
stop_event = threading.Event()

# Создаем и запускаем потоки для кликов
threads = []
for i in range(num_steps):
    x = x_start + i * step
    y = y_start
    thread = threading.Thread(target=click_position, args=(x, y, stop_event))
    threads.append(thread)
    thread.start()


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
