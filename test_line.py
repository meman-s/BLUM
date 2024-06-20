import cv2
import numpy as np
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab

# Координаты линии, по которой будем отслеживать изменения цвета
x_start, y_start = 1777, 556
x_end, y_end = 2532, 577

# Цветовые диапазоны для различных объектов (по результатам вашего анализа)
color_ranges = {
    "leaf": ([19, 248, 168], [41, 235, 248]),  # Зеленый
    "bomb": ([130, 130, 139], [0, 17, 139]),   # Серый
    "ice": ([242, 231, 149], [94, 98, 242])    # Голубой
}

def capture_screen():
    screenshot = ImageGrab.grab()
    frame = np.array(screenshot, dtype=np.uint8)
    frame = frame[:, :, ::-1]  # Convert RGB to BGR
    return frame

def process_line(frame):
    global x_start, y_start, x_end, y_end

    line = frame[y_start:y_start+1, x_start:x_end]

    if line.size == 0:
        print("Линия пуста. Проверьте координаты.")
        return []

    print("Размер линии:", line.shape)

    hsv_line = cv2.cvtColor(line, cv2.COLOR_BGR2HSV)
    objects = []

    for name, (bgr_lower, bgr_upper) in color_ranges.items():
        mask = cv2.inRange(hsv_line, np.array(bgr_lower), np.array(bgr_upper))
        if np.any(mask):
            print(f"Объект '{name}' обнаружен.")
            objects.append(name)

    return objects

def show_image_with_line(frame):
    root = tk.Tk()
    root.title("Calibration")

    # Convert the frame to ImageTk format
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    photo = ImageTk.PhotoImage(image)

    # Create a Canvas widget to display the image
    canvas = tk.Canvas(root, width=image.width, height=image.height)
    canvas.pack()
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)

    # Display the window
    root.mainloop()

def main():
    frame = capture_screen()

    # Ensure frame is a numpy array
    if isinstance(frame, np.ndarray):
        # Визуализация линии для проверки координат
        cv2.line(frame, (x_start, y_start), (x_end, y_end), (0, 255, 0), 2)

        # Show the frame with the line using tkinter
        show_image_with_line(frame)

        objects = process_line(frame)
        print("Обнаруженные объекты на линии:", objects)
    else:
        print("Ошибка: кадр не является numpy массивом")

if __name__ == "__main__":
    main()
