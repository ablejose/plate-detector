from ultralytics import YOLO
import cv2

# Load once when app starts
model = YOLO("best.pt")
logo = cv2.imread("logo.png")


def process_image(input_path, output_path):

    image = cv2.imread(input_path)

    results = model(image)

    for box in results[0].boxes:

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        logo_resized = cv2.resize(
            logo,
            (x2 - x1, y2 - y1)
        )

        image[y1:y2, x1:x2] = logo_resized

    cv2.imwrite(output_path, image)

    return output_path