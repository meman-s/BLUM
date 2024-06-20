import pyautogui
import numpy as np
import time
import cv2
import keyboard
from PIL import ImageGrab

# Координаты линии, по которой будем отслеживать изменения цвета
x_start, y_start = 1777, 556
x_end, y_end = 2532, 577

# Цветовые диапазоны для листиков (замените на свои значения)
leaf_color_lower = np.array([35, 100, 100])
leaf_color_upper = np.array([80, 255, 255])


# Функция для захвата экрана
def capture_screen():
    screenshot = ImageGrab.grab()
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return frame


# Функция для обработки области под линией и поиска объектов, меняющих цвет
def process_line(frame):
    global x_start, y_start, x_end, y_end
    if y_end >= frame.shape[0] or x_end >= frame.shape[1] or y_start >= frame.shape[0] or x_start >= frame.shape[1]:
        print("Координаты линии выходят за пределы изображения.")
        return []

    # Область под линией
    area_under_line = frame[y_start:y_end + 1, x_start:x_end + 1]

    # Преобразование в HSV
    hsv_area = cv2.cvtColor(area_under_line, cv2.COLOR_BGR2HSV)

    # Находим контуры объектов в области
    contours, _ = cv2.findContours(cv2.inRange(hsv_area, leaf_color_lower, leaf_color_upper), cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    objects = []
    for contour in contours:
        # Вычисляем площадь контура
        area = cv2.contourArea(contour)

        # Минимальная площадь объекта (настройте под свои нужды)
        if area > 50:
            # Вычисляем координаты центра контура
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"]) + x_start
                cy = int(M["m01"] / M["m00"]) + y_start

                # Добавляем объект в список
                objects.append({"type": "object", "position": (cx, cy)})

    return objects


# Функция для клика по объекту
def click_object(obj):
    x, y = obj['position']
    pyautogui.click(x, y)
    print(f"Clicked on object at ({x}, {y})")


# Основная функция программы
def main():
    while True:
        if keyboard.is_pressed('esc'):
            print("Программа остановлена пользователем.")
            break

        frame = capture_screen()
        objects = process_line(frame)

        for obj in objects:
            click_object(obj)

        time.sleep(0.1)  # Немного задержки, чтобы уменьшить нагрузку на систему


if __name__ == "__main__":
    main()
