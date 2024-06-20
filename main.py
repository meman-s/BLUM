from pyrogram import Client, filters
from pyrogram.types import Message
from PIL import Image
import io
import cv2
import numpy as np

# Ваши API ID и API Hash
api_id = '22763881'
api_hash = 'ddca4957037bc6e63a47b2642c0bb8f7'

app = Client("my_bot", api_id=api_id, api_hash=api_hash)

# Функция для распознавания объектов на изображении
def process_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    objects = []

    # Распознавание зеленых листиков
    lower_green = np.array([50, 100, 100])
    upper_green = np.array([70, 255, 255])
    mask_green = cv2.inRange(image_cv, lower_green, upper_green)
    contours_green, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours_green:
        x, y, w, h = cv2.boundingRect(contour)
        objects.append({"type": "leaf", "position": (x + w // 2, y + h // 2)})

    # Распознавание бомб (например, красного цвета)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask_red = cv2.inRange(image_cv, lower_red, upper_red)
    contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours_red:
        x, y, w, h = cv2.boundingRect(contour)
        objects.append({"type": "bomb", "position": (x + w // 2, y + h // 2)})

    # Распознавание льдинок (например, голубого цвета)
    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([130, 255, 255])
    mask_blue = cv2.inRange(image_cv, lower_blue, upper_blue)
    contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours_blue:
        x, y, w, h = cv2.boundingRect(contour)
        objects.append({"type": "ice", "position": (x + w // 2, y + h // 2)})

    return objects

# Обработчик сообщений с изображениями
@app.on_message(filters.photo)
def handle_image(client, message: Message):
    photo = message.photo[-1]  # Берем изображение наивысшего качества
    photo.download("current_game.jpg")

    with open("current_game.jpg", "rb") as file:
        image_data = file.read()

    objects = process_image(image_data)

    for obj in objects:
        if obj["type"] == "leaf":
            # Нажимаем на листик
            print(f"Leaf at {obj['position']}")
            # Ваш код для нажатия на листик
        elif obj["type"] == "bomb":
            # Избегаем нажатия на бомбу
            print(f"Bomb at {obj['position']}")
            # Ваш код для избегания бомбы
        elif obj["type"] == "ice":
            # Обрабатываем льдинку
            print(f"Ice at {obj['position']}")
            # Ваш код для обработки льдинки

if __name__ == "__main__":
    app.run()
