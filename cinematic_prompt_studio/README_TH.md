# CINEMATIC MILITARY SCI-FI PROMPT STUDIO

โปรแกรม Prompt Builder สำหรับสร้าง Prompt ภาพยนตร์ไซไฟสงคราม และ Python API สำหรับให้โมเดล AI สร้าง Creative Direction, Storyboard, Master Prompt และ Prompt แยกคลิป

## ภายในชุดนี้

- `index.html` — หน้าเว็บ HTML + JavaScript เปิดในเบราว์เซอร์ได้ มี Local Prompt Builder, แท็บผลลัพธ์, Copy และ Export
- `app.py` — FastAPI backend เชื่อม OpenAI Responses API โดยเรียก API จากฝั่งเซิร์ฟเวอร์
- `requirements.txt` — Python dependencies
- `.env.example` — ตัวอย่างการตั้งค่าคีย์และโมเดล

## วิธีใช้งานบน Windows

1. ติดตั้ง Python 3.10 หรือใหม่กว่า
2. แตก ZIP ไปยังโฟลเดอร์ที่ต้องการ
3. เปิด Command Prompt หรือ PowerShell ในโฟลเดอร์โปรเจกต์
4. สร้าง virtual environment และติดตั้ง dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

5. คัดลอก `.env.example` เป็น `.env`:

```powershell
copy .env.example .env
```

6. เปิดไฟล์ `.env` แล้วใส่ OpenAI API Key ของคุณใน `OPENAI_API_KEY`
7. เริ่มระบบ:

```powershell
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

8. เปิดเบราว์เซอร์ที่ `http://127.0.0.1:8000`
9. กรอกไอเดีย แล้วกด **AI Generate Storyboard + Prompts**

## วิธีใช้งานแบบไม่เชื่อม API

ดับเบิลคลิก `index.html` เพื่อเปิดในเบราว์เซอร์ แล้วกด **สร้าง Prompt ทันที** ระบบจะประกอบ Master Prompt จากค่าที่เลือกโดยไม่ต้องใช้ API

การกด AI Generate ต้องเปิดหน้าเว็บผ่าน Python Server ตามขั้นตอนด้านบน เพราะเบราว์เซอร์ต้องเรียก `/api/generate`

## การเลือกโมเดล

ค่าเริ่มต้นคือ `OPENAI_MODEL=gpt-5.5` หากบัญชี API ของคุณไม่มีสิทธิ์ใช้โมเดลนี้ ให้เปลี่ยนเป็น model ID ที่บัญชีของคุณรองรับใน `.env` แล้ว restart server

## ความปลอดภัย

- เก็บ API Key ใน `.env` บนเครื่องเซิร์ฟเวอร์เท่านั้น
- ห้ามใส่ API Key ใน JavaScript หรือ HTML
- อย่าอัปโหลด `.env` ขึ้น GitHub หรือส่งให้บุคคลอื่น
- ไฟล์ `.env` ไม่ควรถูก commit เข้า repository

## API endpoints

- `GET /api/health` — ตรวจสอบสถานะเซิร์ฟเวอร์และการตั้งค่า API
- `POST /api/generate` — ส่ง brief เพื่อสร้าง Prompt package

## การแก้ปัญหาเบื้องต้น

- `OPENAI_API_KEY` error: ตรวจว่าใส่คีย์ถูกต้องใน `.env`
- model not found / access denied: เปลี่ยน `OPENAI_MODEL` เป็นโมเดลที่บัญชี API ใช้งานได้
- AI Generate ใช้ไม่ได้เมื่อเปิด `index.html` โดยตรง: เปิด `uvicorn` แล้วเข้า `http://127.0.0.1:8000`
- หากแก้ `.env` ต้อง restart server ทุกครั้ง
