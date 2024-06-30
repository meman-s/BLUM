import pyautogui
import numpy as np
import time
import cv2
from PIL import ImageGrab, Image, ImageTk
import tkinter as tk

# Начальная точка: (1777, 577)
# Переместите мышь в конечную точку и нажмите Enter.
# Нажмите Enter, когда будете готовы.
# Конечная точка: (2532, 556)

# Координаты линии, по которой будем отслеживать изменения цвета

x_start, y_start = 1777, 577
x_end, y_end = 2532, 556

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


def visualize_line(frame):
    cv2.line(frame, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)
    img = Image.fromarray(frame)
    img.show()


def capture_and_show_color():
    print("Нажмите Enter для захвата экрана.")
    input()
    frame = capture_screen()

    root = tk.Tk()
    root.title("Выберите объект и нажмите Enter")
    canvas = tk.Canvas(root, width=frame.shape[1], height=frame.shape[0])
    canvas.pack()

    img = Image.fromarray(frame)
    photo = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)

    def get_color(event):
        x, y = event.x, event.y
        pixel_color = frame[y, x]
        hsv_color = cv2.cvtColor(np.uint8([[pixel_color]]), cv2.COLOR_BGR2HSV)[0][0]
        print(f"Цвет выбранного объекта: BGR={pixel_color}, HSV={hsv_color}")
        root.destroy()

    canvas.bind("<Button-1>", get_color)
    root.mainloop()


def show_frame_with_click_points(frame):
    for point in click_points:
        cv2.circle(frame, point, 5, (0, 0, 255), -1)
    cv2.imshow("Frame with Click Points", frame)
    cv2.waitKey(1)


def main():
    while True:
        frame = capture_screen()
        objects = process_line(frame)

        for obj in objects:
            click_object(obj)

        show_frame_with_click_points(frame)

        if cv2.waitKey(1) == 27:  # ESC key to stop
            break

        time.sleep(0.1)  # Немного задержки, чтобы уменьшить нагрузку на систему

    cv2.destroyAllWindows()


if __name__ == "__main__":
    while True:
        print("Выберите опцию:")
        print("1. Калибровать линию")
        print("2. Калибровать цвет")
        print("3. Запустить основную программу")
        choice = input("Введите номер опции: ")

        if choice == "1":
            calibrate_line()
        elif choice == "2":
            capture_and_show_color()
        elif choice == "3":
            main()
        else:
            print("Неверный выбор, попробуйте снова.")
