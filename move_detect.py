import pyautogui
import numpy as np
import time
import cv2
from PIL import ImageGrab
import keyboard
import threading

# Начальные и конечные координаты
x_start, y_start = 2053, 500
x_end, y_end = 2779, 500

# Интервалы
screenshot_interval = 0  # Интервал между захватами экрана в секундах
processing_interval = 0  # Интервал между обработками в секундах

# Флаг для прерывания работы программы
stop_flag = threading.Event()


def capture_screen():
    """Захватывает текущий скриншот."""
    try:
        print("Попытка захвата экрана...")
        screenshot = ImageGrab.grab()
        frame = np.array(screenshot)
        frame = frame[:, :, ::-1]  # Convert RGB to BGR
        print("Захват экрана успешен.")
        return frame
    except Exception as e:
        print(f"Ошибка захвата экрана: {e}")
        return None


def is_gray(pixel):
    """Проверяет, является ли пиксель серым по указанным условиям."""
    return (pixel[0] > 30 and pixel[1] > 30 and pixel[2] > 30) and \
           (pixel[0] < 255 and pixel[1] < 230 and pixel[2] < 230)


def process_line(frame, prev_frame, clicked_positions):
    """Обрабатывает линию для поиска объектов и избегает повторных кликов на уже кликнутых местах."""
    global x_start, y_start, x_end, y_end
    if frame is None or prev_frame is None:
        print("Отсутствуют данные для обработки.")
        return []

    if y_end >= frame.shape[0] or x_end >= frame.shape[1] or y_start >= frame.shape[0] or x_start >= frame.shape[1]:
        print("Координаты линии выходят за пределы изображения.")
        return []

    try:
        line = frame[y_start:y_end + 1, x_start:x_end + 1]
        prev_line = prev_frame[y_start:y_end + 1, x_start:x_end + 1]

        if line.size == 0 or prev_line.size == 0:
            print("Линия пуста. Проверьте координаты.")
            return []

        gray_line = cv2.cvtColor(line, cv2.COLOR_BGR2GRAY)
        prev_gray_line = cv2.cvtColor(prev_line, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray_line, prev_gray_line)
        _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        print(f"Количество контуров: {len(contours)}")

        objects = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 3:
                center_x = x + x_start + w // 2
                center_y = y + y_start + h // 2
                # Проверка цвета центра объекта
                center_pixel = line[center_y - y_start, center_x - x_start]
                if is_gray(center_pixel):
                    print(f"Skipped gray object at ({center_x}, {center_y}), color: {center_pixel}")
                    continue
                # Убедимся, что объект не был ранее кликнут
                if (center_x, center_y) not in clicked_positions:
                    objects.append({"position": (center_x, center_y)})
                    clicked_positions.add((center_x, center_y))
                else:
                    print(f"Object at ({center_x}, {center_y}) already clicked.")
            else:
                print(f"Контур слишком маленький: ({x}, {y}, {w}, {h})")

        print(f"Обнаружено {len(objects)} объектов.")
        return objects
    except Exception as e:
        print(f"Ошибка обработки линии: {e}")
        return []


def click_object(obj):
    """Производит клик по объекту."""
    x, y = obj['position']
    try:
        pyautogui.click(x, y + 5)
        print(f"Clicked at ({x}, {y})")
    except Exception as e:
        print(f"Ошибка клика по ({x}, {y}): {e}")


def calibrate_line():
    """Калибрует начальные и конечные точки линии."""
    global x_start, y_start, x_end, y_end
    print("Калибровка линии. Переместите мышь в начальную точку и нажмите Enter.")
    input("Нажмите Enter, когда будете готовы.")
    x_start, y_start = pyautogui.position()
    print(f"Начальная точка: ({x_start}, {y_start})")

    print("Переместите мышь в конечную точку и нажмите Enter.")
    input("Нажмите Enter, когда будете готовы.")
    x_end, y_end = pyautogui.position()
    print(f"Конечная точка: ({x_end}, {y_end})")


def periodic_click(x, y, interval, stop_event):
    """Функция для периодического клика на указанные координаты."""
    while not stop_event.is_set():
        try:
            pyautogui.click(x, y)
            print(f"Периодический клик по ({x}, {y})")
        except Exception as e:
            print(f"Ошибка периодического клика по ({x}, {y}): {e}")
        time.sleep(interval)


def monitor_escape_key(stop_event):
    """Отслеживает нажатие клавиши ESC для остановки программы."""
    keyboard.wait('esc')
    print("ESC нажата. Завершение работы программы.")
    stop_event.set()


def main():
    """Основная функция программы."""
    print("Основная программа запущена.")
    prev_frame = None
    clicked_positions = set()  # Множество для хранения позиций уже кликнутых объектов
    while not stop_flag.is_set():  # Продолжаем, пока флаг не установлен
        frame = capture_screen()
        if frame is None:
            print("Ошибка захвата экрана. Повторяем попытку.")
            time.sleep(processing_interval)
            continue

        if prev_frame is None:
            prev_frame = frame
            time.sleep(processing_interval)
            continue

        objects = process_line(frame, prev_frame, clicked_positions)
        for obj in objects:
            click_object(obj)

        prev_frame = frame
        time.sleep(processing_interval)  # Задержка между обработками

    print("Программа остановлена.")


if __name__ == "__main__":
    # Создаем событие для остановки
    stop_flag = threading.Event()

    # Запускаем поток для отслеживания нажатия клавиши ESC
    escape_thread = threading.Thread(target=monitor_escape_key, args=(stop_flag,))
    escape_thread.start()

    # Запускаем периодический клик в отдельном потоке
    periodic_click_thread = threading.Thread(target=periodic_click, args=(2416, 1364, 20, stop_flag))
    periodic_click_thread.start()

    while True:
        print("Выберите опцию:")
        print("1. Калибровать линию")
        print("2. Запустить основную программу")
        choice = input("Введите номер опции: ")

        if choice == "1":
            calibrate_line()
        elif choice == "2":
            print("Запуск основной программы...")
            time.sleep(2)
            main()
        else:
            print("Неверный выбор, попробуйте снова.")

        # Прерываем работу периодического клика и завершаем поток отслеживания клавиши ESC
        stop_flag.set()
        periodic_click_thread.join()
        escape_thread.join()
        break  # Выходим из цикла выбора опций после завершения работы
