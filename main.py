from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from rembg import remove
from PIL import Image
import pytesseract
import numpy as np
import cv2
import re
import io
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from fastapi.responses import StreamingResponse
import base64

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Date formatting utilities
# ========================
def format_date(ymd):
    return f"{ymd[4:6]}-{ymd[2:4]}-{ymd[0:2]}"

def fix_century(date_str):
    dd, mm, yy = date_str.split('-')
    yy = int(yy)
    yyyy = 2000 + yy if yy < 50 else 1900 + yy
    return f"{dd}-{mm}-{yyyy}"

# ========================
# MRZ Parsing
# ========================
def is_possible_mrz_line(line):
    return bool(re.fullmatch(r'[A-Z0-9<]{20,}', line))

def parse_mrz(text):
    # Normalize and clean lines
    lines = [line.strip().replace(' ', '').replace('K', '<').replace('k', '<') for line in text.splitlines() if line.strip()]

    # Find MRZ triplets
    candidates = []
    for i in range(len(lines) - 2):
        l1, l2, l3 = lines[i:i+3]
        if all(is_possible_mrz_line(l) for l in [l1, l2, l3]):
            candidates.append((l1, l2, l3))

    if not candidates:
        return {"error": "Valid MRZ block not found"}

    # Take the first candidate
    l1, l2, l3 = candidates[0]

    # ID extraction
    id_match = re.search(r'[A-Z]{3}([0-9]{8})<', l1)
    id_number = id_match.group(1) if id_match else None

    # Line 2: DOB, Gender, Expiry
    dob_raw = l2[0:6]
    gender = l2[7]
    expiry_raw = l2[8:14]

    try:
        dob = fix_century(format_date(dob_raw))
        expiry = fix_century(format_date(expiry_raw))
    except Exception:
        dob = expiry = "Invalid"

    # Line 3: Name
    name_parts = l3.split('<', 1)
    first_name = name_parts[0].replace('<', '')
    last_name = name_parts[1].replace('<', '') if len(name_parts) > 1 else ''

    return {
        "ID Number": id_number,
        "Date of Birth": dob,
        "Gender": gender,
        "Expiry Date": expiry,
        "First Name": first_name[:25],
        "Last Name": last_name[:25]
    }

# ========================
# MRZ Extraction Route
# ========================
@app.post("/extract-mrz/")
async def extract_mrz(file: UploadFile = File(...)):
    try:
        # Read image
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents)).convert("RGBA")

        # Remove background
        output_image = remove(input_image)

        # Crop non-transparent content
        np_img = np.array(output_image)
        if np_img.shape[2] == 4:
            alpha = np_img[:, :, 3]
            non_empty_cols = np.where(np.max(alpha, axis=0) > 0)[0]
            non_empty_rows = np.where(np.max(alpha, axis=1) > 0)[0]

            if non_empty_cols.size and non_empty_rows.size:
                crop_box = (
                    non_empty_cols[0],  # left
                    non_empty_rows[0],  # top
                    non_empty_cols[-1], # right
                    non_empty_rows[-1]  # bottom
                )
                cropped_image = output_image.crop(crop_box)
            else:
                return JSONResponse(content={"error": "No visible content found in image."})
        else:
            return JSONResponse(content={"error": "Image does not have alpha channel."})

        # Resize for OCR clarity
        cropped_image = cropped_image.resize((300, int(cropped_image.height * 300 / cropped_image.width)))
        image_np = np.array(cropped_image.convert("RGB"))
        image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        # Preprocess for OCR
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # OCR using MRZ configuration
        config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'
        raw_text = pytesseract.image_to_string(gray, config=config)

        # Fix common OCR issues
        raw_text = re.sub(r'(?<=[A-Z0-9])K(?=[A-Z0-9<])', '<', raw_text)

        # Parse
        result = parse_mrz(raw_text)

        return JSONResponse(content=result)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)})
@app.post("/remove-bg/")
async def remove_bg(front_file: UploadFile = File(...), back_file: UploadFile = File(...)):
    try:
        # Process front image
        front_bytes = await front_file.read()
        front_img = Image.open(io.BytesIO(front_bytes)).convert("RGBA")
        front_no_bg = remove(front_img)

        # Process back image
        back_bytes = await back_file.read()
        back_img = Image.open(io.BytesIO(back_bytes)).convert("RGBA")
        back_no_bg = remove(back_img)

        # Convert both images to base64 strings for sending to frontend
        def pil_to_base64(img: Image.Image):
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode()

        front_base64 = pil_to_base64(front_no_bg)
        back_base64 = pil_to_base64(back_no_bg)

        return {
            "front_image": f"data:image/png;base64,{front_base64}",
            "back_image": f"data:image/png;base64,{back_base64}"
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)})
