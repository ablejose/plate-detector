from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse
import tempfile
import shutil

from replace_plate import process_image

app = FastAPI()

VERIFY_TOKEN = "plate_detector_verify"


@app.post("/process")
async def process(file: UploadFile = File(...)):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as input_file:
        shutil.copyfileobj(file.file, input_file)
        input_path = input_file.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as output_file:
        output_path = output_file.name

    process_image(input_path, output_path)

    return FileResponse(
        output_path,
        media_type="image/jpeg",
        filename="processed.jpg"
    )


@app.get("/webhook")
async def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return "Verification failed"


@app.post("/webhook")
async def receive_webhook(request: Request):

    data = await request.json()

    print("WHATSAPP EVENT:")
    print(data)

    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]

        print("TYPE:", msg["type"])

        if msg["type"] == "image":
            if msg["type"] == "image":

    print("IMAGE RECEIVED")

    import requests
    import os

    token = os.getenv("WHATSAPP_TOKEN")

    media_id = msg["image"]["id"]

    url = f"https://graph.facebook.com/v23.0/{media_id}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)

    print("MEDIA INFO:")
    print(response.json())

    except Exception as e:
        print("ERROR:", e)

    return {"status": "ok"}