import pyautogui
import numpy as np
import time
import cv2
from PIL import ImageGrab
import keyboard

x_start, y_start = 2113, 500
x_end, y_end = 2862, 500


def capture_screen():
    screenshot = ImageGrab.grab()
    frame = np.array(screenshot)
    frame = frame[:, :, ::-1]  # Convert RGB to BGR
    return frame


def is_gray(pixel, threshold=10):
    return abs(int(pixel[0]) - int(pixel[1])) < threshold and abs(int(pixel[1]) - int(pixel[2])) < threshold


def process_line(frame, prev_frame):
    global x_start, y_start, x_end, y_end
    if y_end >= frame.shape[0] or x_end >= frame.shape[1] or y_start >= frame.shape[0] or x_start >= frame.shape[1]:
        print("Координаты линии выходят за пределы изображения.")
        return []

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

    objects = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if 3 < w < 50:
            center_x = x + x_start + w // 2
            center_y = y + y_start + h // 2
            # Check if the object is gray
            if is_gray(line[y, x]):
                print(f"Skipped gray object at ({center_x}, {center_y})")
                continue
            objects.append({"position": (center_x, center_y)})

    return objects


def click_object(obj):
    x, y = obj['position']
    pyautogui.click(x, y)
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
    prev_frame = None
    while True:
        frame = capture_screen()
        if prev_frame is None:
            prev_frame = frame
            continue

        objects = process_line(frame, prev_frame)
        for obj in objects:
            click_object(obj)

        prev_frame = frame

        time.sleep(0.01)  # Reduced delay for faster processing

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
