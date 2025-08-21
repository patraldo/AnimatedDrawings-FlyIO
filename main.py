# main.py
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
import os
import subprocess
import uuid

app = FastAPI(title="Animate Your Alien")

# Make directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

@app.post("/animate")
async def animate(
    image: UploadFile = File(...),
    animation_type: str = Form("hug"),
):
    # Save uploaded image
    input_path = f"uploads/{uuid.uuid4()}.png"
    with open(input_path, "wb") as f:
        f.write(await image.read())

    # Output path
    output_path = f"outputs/{os.path.basename(input_path).split('.')[0]}.mp4"

    # Run Animated Drawings CLI
    result = subprocess.run([
        "python", "-m", "animated_drawings.cli",
        "--input_image", input_path,
        "--output_video", output_path,
        "--animation_type", animation_type,
        "--model_run_dir", "models",
        "--realism_level", "0.25",
        "--mirror_enable", "True"
    ], capture_output=True, text=True)

    if result.returncode != 0 or not os.path.exists(output_path):
        return {"error": "Animation failed", "details": result.stderr}

    return FileResponse(output_path, media_type="video/mp4", filename="animated.mp4")

@app.get("/")
async def home():
    return {
        "message": "🛸 Animate Your Alien",
        "upload_url": "/animate",
        "method": "POST",
        "fields": ["image (PNG)", "animation_type (e.g. hug, wave, bounce)"]
    }
