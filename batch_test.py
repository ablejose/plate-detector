from ultralytics import YOLO
import cv2
import os

# Load model once
model = YOLO(
    r"C:\Users\ABLE\runs\detect\train3\weights\best.pt"
)

# Load logo once
logo = cv2.imread("logo.png")

input_folder = "test_images"
output_folder = "outputs"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):

    if filename.lower().endswith((".jpg", ".jpeg", ".png")):

        image_path = os.path.join(input_folder, filename)

        image = cv2.imread(image_path)

        results = model(image)

        for box in results[0].boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            logo_resized = cv2.resize(
                logo,
                (x2 - x1, y2 - y1)
            )

            image[y1:y2, x1:x2] = logo_resized

        output_path = os.path.join(output_folder, filename)

        cv2.imwrite(output_path, image)

        print(f"Processed: {filename}")

print("Finished!")