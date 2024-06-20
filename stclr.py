import cv2
import numpy as np
from PIL import ImageGrab, Image, ImageTk
import tkinter as tk


def capture_screen():
    screenshot = ImageGrab.grab()
    frame = np.array(screenshot)
    frame = frame[:, :, ::-1]  # Convert RGB to BGR
    return frame


def pick_color():
    frame = capture_screen()

    root = tk.Tk()
    root.title("Выберите объект и нажмите Enter")
    canvas = tk.Canvas(root, width=frame.shape[1], height=frame.shape[0])
    canvas.pack()

    img = Image.fromarray(frame)
    photo = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)

    selected_colors = []

    def get_color(event):
        x, y = event.x, event.y
        pixel_color = frame[y, x]
        hsv_color = cv2.cvtColor(np.uint8([[pixel_color]]), cv2.COLOR_BGR2HSV)[0][0]
        selected_colors.append(hsv_color)
        print(f"Цвет выбранного объекта: BGR={pixel_color}, HSV={hsv_color}")

    def on_enter(event):
        root.quit()
        root.destroy()

    canvas.bind("<Button-1>", get_color)
    root.bind("<Return>", on_enter)
    root.mainloop()

    return selected_colors


def calculate_ranges(hsv_colors):
    if not hsv_colors:
        print("Не выбраны цвета для калибровки.")
        return None, None

    hsv_colors = np.array(hsv_colors)
    lower_bound = np.min(hsv_colors, axis=0)
    upper_bound = np.max(hsv_colors, axis=0)

    return lower_bound, upper_bound


def main():
    print("Нажмите Enter для захвата экрана и выбора цветов.")
    input()
    hsv_colors = pick_color()
    lower_bound, upper_bound = calculate_ranges(hsv_colors)

    if lower_bound is not None and upper_bound is not None:
        print(f"Нижняя граница HSV: {lower_bound}")
        print(f"Верхняя граница HSV: {upper_bound}")
    else:
        print("Не удалось определить диапазоны цветов.")


if __name__ == "__main__":
    main()

