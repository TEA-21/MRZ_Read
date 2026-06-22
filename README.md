# MRZ_Read

A web-based application for extracting Machine-Readable Zone (MRZ) data from identity documents using OCR and computer vision. This project provides both backend API services and a frontend interface for processing ID document images.

## 🎯 Project Overview

MRZ_Read is designed to:
- Extract MRZ data from the back side of identity documents (passports, visas, ID cards)
- Remove backgrounds from document images for cleaner processing
- Parse OCR results to extract structured information including:
  - ID Number
  - Date of Birth
  - Gender
  - Expiry Date
  - First Name
  - Last Name

The application uses a **FastAPI** backend with **Tesseract OCR** and **computer vision** tools, complemented by a simple HTML/JavaScript frontend for user interaction.

## 🛠️ Technology Stack

### Backend
- **FastAPI** 0.115.14 - Modern Python web framework for building APIs
- **Uvicorn** 0.35.0 - ASGI web server
- **Tesseract OCR** - Optical character recognition engine
- **rembg** 2.0.66 - AI-powered background removal
- **OpenCV** 4.11.0.86 - Computer vision library
- **Pillow** 11.3.0 - Image processing library
- **NumPy** 2.2.6 - Numerical computing library

### Frontend
- **HTML5** - Structure and interface
- **Vanilla JavaScript** - Client-side logic and API interactions

### Deployment & Environment
- **Docker** - Containerization for deployment
- **Python** 3.11.4 - Runtime environment

## 📋 Language Composition

- **Python**: 56% - Core backend logic
- **HTML**: 37.4% - Web interface
- **Dockerfile**: 5.3% - Container configuration
- **Shell**: 1.3% - Startup scripts

## 🚀 Features

### 1. Background Removal (`/remove-bg/`)
- Accepts front and back side images of identity documents
- Uses AI-powered background removal (rembg)
- Returns base64-encoded PNG images without backgrounds
- Supports RGBA format with alpha channel processing

### 2. MRZ Extraction (`/extract-mrz/`)
- Processes document images to extract MRZ data
- Advanced OCR preprocessing:
  - Image resizing for clarity
  - Grayscale conversion
  - Bilateral filtering
  - Binary thresholding (Otsu's method)
- Automatic date formatting and century detection
- Robust MRZ parsing with error handling

### 3. Automatic Date Handling
- Converts MRZ date format (YYMMDD) to readable format (DD-MM-YYYY)
- Intelligent century detection:
  - Years 00-49 → 2000-2049
  - Years 50-99 → 1950-1999

## 📁 Project Structure

```
MRZ_Read/
├── main.py                 # FastAPI application & core logic
├── index.html             # Frontend web interface
├── requirements.txt       # Python dependencies
├── runtime.txt            # Python runtime version specification
├── Dockerfile             # Docker container configuration
├── start.sh              # Application startup script
└── __pycache__/          # Python compiled files
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- Tesseract-OCR installed on system
- Docker (optional, for containerized deployment)

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TEA-21/MRZ_Read.git
   cd MRZ_Read
   ```

2. **Install system dependencies (Linux/Ubuntu)**
   ```bash
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr libgl1-mesa-glx libglib2.0-0
   ```

3. **Install system dependencies (macOS)**
   ```bash
   brew install tesseract
   ```

4. **Install system dependencies (Windows)**
   - Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to default location: `C:\Program Files\Tesseract-OCR\`

5. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

6. **Install Python dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Docker Installation

1. **Build the Docker image**
   ```bash
   docker build -t mrz-read .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 mrz-read
   ```

   Or with custom port (Railway-compatible):
   ```bash
   docker run -p 8000:8000 -e PORT=8000 mrz-read
   ```

## 🎮 Running the Application

### Local Development

```bash
# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- API: `http://127.0.0.1:8000`
- Web Interface: Open `index.html` in your browser

### Using the Start Script

```bash
chmod +x start.sh
./start.sh
```

The start script supports Railway-style PORT environment variable:
```bash
PORT=3000 ./start.sh
```

## 🔌 API Endpoints

### 1. Extract MRZ from Document
**POST** `/extract-mrz/`

**Request:**
- Content-Type: multipart/form-data
- Parameter: `file` (image file)

**Response:**
```json
{
  "ID Number": "12345678",
  "Date of Birth": "01-01-1990",
  "Gender": "M",
  "Expiry Date": "15-06-2030",
  "First Name": "JOHN",
  "Last Name": "SMITH"
}
```

**Error Response:**
```json
{
  "error": "Valid MRZ block not found"
}
```

### 2. Remove Background from Images
**POST** `/remove-bg/`

**Request:**
- Content-Type: multipart/form-data
- Parameters:
  - `front_file` (image file) - Front side of document
  - `back_file` (image file) - Back side of document

**Response:**
```json
{
  "front_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA...",
  "back_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAA..."
}
```

## 🎨 Frontend Usage

1. **Open the web interface** - Load `index.html` in your browser
2. **Upload Images**:
   - Select the front side image of the document
   - Select the back side image (containing MRZ)
3. **Process**:
   - Click "Upload and Extract MRZ (from Back Side)"
   - The application will:
     - Remove backgrounds from both images
     - Display the processed images
     - Extract MRZ data from the back image
     - Display the extracted information
4. **View Results** - Extracted MRZ data appears in the result panel

## ⚙️ Configuration

### CORS Settings
The application allows requests from all origins (development mode):
```python
CORSMiddleware(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, update this to specific domains.

### OCR Configuration
The Tesseract OCR configuration is optimized for MRZ text:
```
--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<
```

This restricts recognition to uppercase letters, numbers, and the angle bracket character used in MRZ format.

## 🔍 Key Algorithms

### MRZ Parsing
1. Normalizes text and removes whitespace
2. Replaces common OCR errors (K/k with <)
3. Identifies valid MRZ blocks (3 consecutive lines of 20+ alphanumeric characters)
4. Extracts information from specific character positions:
   - ID Number: Characters after first country code
   - Date of Birth: Line 2, positions 0-5
   - Gender: Line 2, position 7
   - Expiry Date: Line 2, positions 8-13
   - Name: Line 3, split by angle brackets

### Image Preprocessing for OCR
1. **Resize**: Scale image to 300px width with proportional height
2. **Grayscale**: Convert to single-channel image
3. **Upscale**: 2x upscaling for clarity
4. **Denoise**: Bilateral filtering to reduce noise while preserving edges
5. **Threshold**: Otsu's method for binary conversion

## 🐛 Error Handling

The application handles various error scenarios:
- Invalid or missing image files
- Images without alpha channel
- No visible content in image after background removal
- Invalid or undetectable MRZ blocks
- Malformed MRZ data during parsing

All errors return appropriate JSON error responses.

## 📝 Example Workflow

```
User uploads front & back images
         ↓
Remove backgrounds (rembg)
         ↓
Display processed images
         ↓
Extract MRZ from back image
         ↓
Preprocess image (resize, grayscale, filter, threshold)
         ↓
Run Tesseract OCR
         ↓
Fix common OCR errors (K→<)
         ↓
Parse MRZ block (triplet of 3 lines)
         ↓
Extract structured data (ID, DOB, Gender, Expiry, Names)
         ↓
Display results to user
```

## 🚢 Deployment

### Railway Deployment
The project is configured for Railway deployment:
- Uses `Dockerfile` for containerization
- `start.sh` supports dynamic PORT assignment
- `runtime.txt` specifies Python 3.11.4

### Environment Variables
- `PORT` - Server port (default: 8000)

## 📚 Dependencies Summary

Key dependencies:
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pytesseract** - Python wrapper for Tesseract OCR
- **rembg** - Background removal
- **opencv-python** - Computer vision
- **pillow** - Image processing
- **pydantic** - Data validation
- **python-multipart** - Form data handling

See `requirements.txt` for complete list.

## 🔒 Security Notes

- Current CORS settings allow all origins (development mode)
- For production, restrict CORS to specific domains
- Validate and sanitize image uploads
- Implement file size limits
- Consider adding authentication for API endpoints
