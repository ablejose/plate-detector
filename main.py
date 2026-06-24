from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse
import tempfile
import shutil
import requests
import os

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

                            print("IMAGE RECEIVED")


                            token = os.getenv("WHATSAPP_TOKEN")
                            headers = {
                                "Authorization": f"Bearer {token}"
                            }


                            print("PHONE_NUMBER_ID:", os.getenv("PHONE_NUMBER_ID"))
                            print("TOKEN EXISTS:", bool(token))
                            print("TOKEN LENGTH:", len(token) if token else 0)

                            image_url = msg["image"]["url"]

                            print("IMAGE URL FOUND:", image_url[:80])

                            image_response = requests.get(
                                image_url,
                                headers=headers
                            )

                            with open("whatsapp_input.jpg", "wb") as f:
                                f.write(image_response.content)
                                print("DOWNLOAD STATUS:", image_response.status_code)
                                print("CONTENT TYPE:", image_response.headers.get("content-type"))
                                print("FILE SIZE:", os.path.getsize("whatsapp_input.jpg"))

                            print("IMAGE DOWNLOADED")
                            process_image(
                                "whatsapp_input.jpg",
                                "whatsapp_output.jpg"
                            )
                            

                            print("IMAGE PROCESSED")
                            files = {
                                "file": (
                                    "whatsapp_output.jpg",
                                    open("whatsapp_output.jpg", "rb"),
                                    "image/jpeg"
                                )
                            }

                            print("OUTPUT EXISTS:", os.path.exists("whatsapp_output.jpg"))
                            print("OUTPUT SIZE:", os.path.getsize("whatsapp_output.jpg"))

                            data_upload = {
                                "messaging_product": "whatsapp"
                            }

                            upload_response = requests.post(
                                f"https://graph.facebook.com/v23.0/{os.getenv('PHONE_NUMBER_ID')}/media",
                                headers={
                                    "Authorization": f"Bearer {token}"
                                },
                                files=files,
                                data=data_upload
                            )

                            upload_json = upload_response.json()

                            print("UPLOAD RESPONSE:")
                            print(upload_json)

                            if "id" not in upload_json:
                                return {"status": "upload failed"}

                            media_id_uploaded = upload_json["id"]

                            sender = msg["from"]

                            send_response = requests.post(
                                f"https://graph.facebook.com/v23.0/{os.getenv('PHONE_NUMBER_ID')}/messages",
                                headers={
                                    "Authorization": f"Bearer {token}",
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "messaging_product": "whatsapp",
                                    "to": sender,
                                    "type": "image",
                                    "image": {
                                        "id": media_id_uploaded
                                    }
                                }
                            )

                            print("SEND RESPONSE:")
                            print(send_response.json())

                        
        except Exception as e:
                    print("ERROR:", e)

                    return {"status": "ok"}

