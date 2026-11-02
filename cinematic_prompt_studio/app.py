"""Cinematic Military Sci-Fi Prompt Studio API.

Serves the browser UI and generates structured prompt packages via OpenAI Responses API.
The API key is read only from the server environment and is never sent to the browser.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel, Field
from starlette.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("cinematic-prompt-studio")

APP_TITLE = "Cinematic Military Sci-Fi Prompt Studio"
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.5")
API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

app = FastAPI(title=APP_TITLE, version="1.0.0")

# Same-origin hosting is the normal setup. Extra origins can be added for a separately hosted UI.
origins = [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class GenerateRequest(BaseModel):
    idea: str = Field(min_length=5, max_length=5000)
    duration: str = "30"
    clipDuration: str = "10"
    aspect: str = "9:16"
    platform: str = "Google Flow"
    promptLanguage: str = "English"
    terrain: str = "Desert battlefield and fortified military outpost"
    weather: str = "Clear sky with atmospheric dust"
    timeOfDay: str = "Late afternoon cinematic sunlight"
    visualStyle: str = "Photorealistic live-action sci-fi war blockbuster"
    forces: str = "Heavy humanoid combat mechs and armored units"
    factionA: str = "Steel grey armor with cyan-blue identification lights"
    factionB: str = "Desert sand armor with restrained amber-red markings"
    weapons: str = "Energy weapons, guided missiles and defensive shields"
    action: str = ""
    camera: str = "Wide aerial establishing, low-angle ground tracking, controlled push-in"
    vfx: str = "Physically grounded explosions, energy shields, sparks, dust and smoke"
    sound: str = "Mechanical ambience, weapon impacts, cinematic score, no dialogue"
    realism: str = "Maximum photorealism, believable engineering and physical motion"
    continuity: str = ""
    extra: str = ""

SYSTEM_INSTRUCTIONS = r"""
You are CINEMATIC MILITARY SCI-FI PROMPT ENGINEER: a film director, cinematographer,
world designer, mechanical design consultant, visual-effects supervisor and prompt engineer.
Your specialty is photorealistic live-action futuristic military cinema: giant combat mechs,
autonomous ground forces, armored vehicles, drone formations, energy weapons, defensive shields,
large-scale battlefields, cinematic explosions and physically believable action.

Convert the user's short premise and production settings into a production-ready package for
Google Flow, Gemini or the requested generation platform. The user's requested creative premise
is the source of truth. Do not silently change faction colors, insignia, machines, weapons,
terrain, aspect ratio, duration or requested action.

VISUAL DNA:
- Premium photorealistic live-action blockbuster cinematography; not cartoon, not toy-like.
- Massive scale communicated with terrain, buildings, vehicles and other scale references.
- Functional mechanical design: plausible joints, armor plates, weapon mounts, sensors and support.
- Clear action geography, readable silhouettes and deliberate camera movement.
- Controlled VFX with cause and effect: projectile origin and destination, shield reaction, flash,
  pressure wave, debris, dust, smoke and light reflecting on nearby materials.
- Cinematic lighting motivated by sky, practical lights, weapons and explosions.

WORKFLOW:
1. Derive a concise creative direction and 4-8 style DNA anchors.
2. Plan a sequence using the requested total duration and approximate clip duration. The number of
   clips should be ceil(total_duration / clip_duration). Avoid inventing extra runtime.
3. For each clip create one coherent action beat with a clear opening state, primary motion,
   secondary environmental motion, camera move, physical interaction and final frame.
4. Create a master prompt that locks world design, faction designs, environment, material language,
   camera grammar, VFX logic, sound policy and continuity rules.
5. Create individual copy-ready clip prompts. Each needs duration, timeline (time-coded action),
   camera, lighting, VFX/physics, sound, continuity from previous clip, and end frame for next clip.
6. Include a negative prompt and practical production notes for image keyframes and image-to-video.

CONTINUITY RULES:
- Preserve each subject's exact silhouette, scale, armor layout, faction color, insignia and weapons.
- Preserve screen direction, position relationships, lighting direction, weather and terrain layout.
- Damage, smoke, dust, craters and debris persist unless the story explains a change.
- Clip N's ending state must match Clip N+1's opening state. No teleporting or unexplained redesign.
- Keep one or two primary actions per clip. Do not overload a short clip with unrelated events.
- Camera moves must be physically possible and should not conflict inside one shot.

PHYSICS / IMAGE QUALITY:
- Heavy mechs show weight transfer, joint articulation and ground response.
- Aircraft/drone formations move coherently and maintain believable spacing.
- Explosions influence nearby dust, debris and surfaces; avoid decorative random blasts.
- Energy shields react locally at impact; weapon light affects nearby surfaces.
- Keep smoke and motion blur from obscuring the main subject throughout the shot.

OUTPUT LANGUAGE:
Respect promptLanguage. For English, write polished production prompts in English. For Thai, write
all prompt text in Thai. For Bilingual, write prompts in English and concise Thai production notes.

Return ONLY a valid JSON object. No Markdown fences, no preamble and no trailing commentary.
Use exactly these top-level keys:
{
  "creative_direction": "string",
  "style_dna": ["string"],
  "storyboard": [
    {"time":"0-10s", "title":"string", "visual":"string", "camera":"string", "transition":"string"}
  ],
  "master_prompt": "string",
  "clips": [
    {"title":"CLIP 01 — title", "duration":"10 seconds", "prompt":"complete copy-ready prompt", "start_frame":"string", "end_frame":"string", "continuity":"string"}
  ],
  "negative_prompt": "string",
  "production_notes": "string"
}

Do not return empty storyboard or clips. Every clip prompt must be detailed enough to use directly,
not a short summary. Include explicit time-coded action segments in each clip prompt. Avoid fake
technical guarantees about the target video model. Do not include operational real-world attack
instructions; keep all weapons, forces and events in fictional cinematic context.
""".strip()


def get_client() -> OpenAI:
    if not API_KEY:
        raise HTTPException(
            status_code=503,
            detail="ยังไม่ได้ตั้งค่า OPENAI_API_KEY ในไฟล์ .env ของเซิร์ฟเวอร์",
        )
    return OpenAI(api_key=API_KEY, timeout=120.0, max_retries=2)


def parse_model_json(raw: str) -> dict[str, Any]:
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.exception("Model did not return valid JSON")
        raise HTTPException(status_code=502, detail="โมเดลส่งผลลัพธ์ที่ไม่ใช่ JSON ที่ถูกต้อง ลองกด Generate อีกครั้ง") from exc
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="รูปแบบผลลัพธ์จากโมเดลไม่ถูกต้อง")
    required = ["creative_direction", "style_dna", "storyboard", "master_prompt", "clips", "negative_prompt", "production_notes"]
    for key in required:
        data.setdefault(key, [] if key in ("style_dna", "storyboard", "clips") else "")
    if not isinstance(data["clips"], list) or not isinstance(data["storyboard"], list):
        raise HTTPException(status_code=502, detail="โมเดลส่งโครงสร้าง Storyboard หรือ Clips ไม่ถูกต้อง")
    return data


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "configured": bool(API_KEY), "model": MODEL if API_KEY else None}


@app.post("/api/generate")
def generate(payload: GenerateRequest) -> dict[str, Any]:
    client = get_client()
    user_data = payload.model_dump()
    try:
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_INSTRUCTIONS,
            input=(
                "Create the complete cinematic prompt package from this production brief. "
                "Treat the brief as creative source material and return the required JSON object.\n\n"
                + json.dumps(user_data, ensure_ascii=False, indent=2)
            ),
            text={"format": {"type": "json_object"}},
            max_output_tokens=12000,
        )
        result = parse_model_json(response.output_text)
        result["model"] = MODEL
        result["request_id"] = getattr(response, "_request_id", None)
        return result
    except HTTPException:
        raise
    except Exception as exc:  # SDK errors are returned as a clear API response, not a traceback.
        logger.exception("OpenAI generation failed")
        message = str(exc)
        if "authentication" in message.lower() or "api key" in message.lower():
            detail = "ยืนยัน API Key ไม่สำเร็จ กรุณาตรวจ OPENAI_API_KEY ในไฟล์ .env"
        elif "model" in message.lower() and ("not found" in message.lower() or "does not exist" in message.lower()):
            detail = f"ไม่พบโมเดล {MODEL} หรือบัญชีนี้ยังไม่มีสิทธิ์ใช้โมเดลดังกล่าว กรุณาแก้ OPENAI_MODEL ในไฟล์ .env"
        else:
            detail = f"เรียก AI API ไม่สำเร็จ: {message[:500]}"
        raise HTTPException(status_code=502, detail=detail) from exc


@app.get("/")
def home() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


# Optional static asset route if the project is extended with local assets later.
assets_dir = BASE_DIR / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
