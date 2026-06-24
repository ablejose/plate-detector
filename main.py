from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import shutil
import os
from replace_plate import process_image
import tempfile
import os

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import tempfile
import shutil
import os

from replace_plate import process_image

app = FastAPI()


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