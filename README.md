# PDFCraft - Pro Image to PDF Converter & Editor

An attractive, fast, and secure web application to convert images to PDF and edit PDF files.

## Features

- **Image to PDF**: Convert any image format (JPG, PNG, WEBP, GIF, BMP, TIFF) to a professional PDF.
- **PDF Merging**: Combine multiple PDF files into a single document.
- **Beautiful UI**: Modern, responsive design with glassmorphism and smooth animations.
- **Fast Processing**: Optimized backend for quick conversions.
- **Privacy Focused**: Files are processed locally and can be deleted after use.

## Folder Structure

```
/pdf-converter/
├── backend/
│   ├── app.py                 # Flask Server
│   ├── requirements.txt       # Dependencies
│   ├── utils/                 # Core logic
│   └── uploads/               # Temp storage
├── frontend/
│   ├── index.html            # UI Structure
│   ├── css/style.css         # Visuals
│   └── js/app.js             # Interaction
└── README.md                 # This file
```

## How to Run

### 1. Start the Backend
Navigate to the `backend` folder and run the Flask server:
```bash
cd backend
pip3 install -r requirements.txt
python3 app.py
```
Default port: `5001`

### 2. Open the Frontend
Simply open `frontend/index.html` in your web browser.

## Tech Stack
- **Backend**: Python, Flask, Pillow, img2pdf, PyPDF2
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+), Bootstrap 5, Font Awesome
