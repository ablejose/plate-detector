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

    return {"status": "ok"}