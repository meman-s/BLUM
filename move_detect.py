import pyautogui
import numpy as np
import time
import cv2
from PIL import ImageGrab
import keyboard

# Начальная точка: (1777, 577)
# Конечная точка: (2532, 556)
x_start, y_start = 1777, 556
x_end, y_end = 2532, 577

click_points = []


def capture_screen():
    screenshot = ImageGrab.grab()
    frame = np.array(screenshot)
    frame = frame[:, :, ::-1]  # Convert RGB to BGR
    return frame


def process_line(frame):
    global x_start, y_start, x_end, y_end
    if y_end >= frame.shape[0] or x_end >= frame.shape[1] or y_start >= frame.shape[0] or x_start >= frame.shape[1]:
        print("Координаты линии выходят за пределы изображения.")
        return []
    line = frame[y_start:y_end + 1, x_start:x_end + 1]
    if line.size == 0:
        print("Линия пуста. Проверьте координаты.")
        return []

    gray_line = cv2.cvtColor(line, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_line, 1, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    objects = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        objects.append({"position": (x + x_start, y + y_start)})

    return objects


def click_object(obj):
    x, y = obj['position']
    pyautogui.click(x, y)
    click_points.append((x, y))
    print(f"Clicked at ({x}, {y})")


def calibrate_line():
    global x_start, y_start, x_end, y_end
    print("Калибровка линии. Переместите мышь в начальную точку и нажмите Enter.")
    input("Нажмите Enter, когда будете готовы.")
    x_start, y_start = pyautogui.position()
    print(f"Начальная точка: ({x_start}, {y_start})")

    print("Переместите мышь в конечную точку и нажмите Enter.")
    input("Нажмите Enter, когда будете готовы.")
    x_end, y_end = pyautogui.position()
    print(f"Конечная точка: ({x_end}, {y_end})")


def main():
    while True:
        frame = capture_screen()
        objects = process_line(frame)

        for obj in objects:
            click_object(obj)

        time.sleep(0.1)  # Немного задержки, чтобы уменьшить нагрузку на систему

        if keyboard.is_pressed("esc"):  # ESC key to stop
            print("Программа остановлена.")
            break


if __name__ == "__main__":
    while True:
        print("Выберите опцию:")
        print("1. Калибровать линию")
        print("2. Запустить основную программу")
        choice = input("Введите номер опции: ")

        if choice == "1":
            calibrate_line()
        elif choice == "2":
            main()
        else:
            print("Неверный выбор, попробуйте снова.")
