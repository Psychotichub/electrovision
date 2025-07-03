# ⚡ ElectroVision AI  
**AI-Powered Electrical Plan Interpreter (PDF & AutoCAD)**

---

## 🎯 Objective

ElectroVision AI is a smart system that can read and analyze **electrical plans** from **PDF**, **DWG**, and **DXF** files. It extracts electrical components, wiring paths, and annotations and performs advanced tasks such as:

- Plan summarization  
- Component detection  
- Compliance checking  
- Smart natural language querying  

---

## 🧱 System Modules

| Module          | Description                                                |
|-----------------|------------------------------------------------------------|
| 1. File Uploader | Accepts `.pdf`, `.dwg`, and `.dxf` files                   |
| 2. File Converter | Converts DWG → DXF and PDF → image/text                   |
| 3. Data Extractor | Detects components, wires, text, symbols from input files |
| 4. Preprocessor   | Structures data into JSON/XML format                      |
| 5. AI Analyzer    | Performs AI-based detection and rule checking             |
| 6. Query Engine   | Accepts natural language questions from user              |
| 7. Dashboard      | Visualizes the extracted data and analysis                |

---

## 💻 Tech Stack

### Frontend
- React / Vue.js  
- Responsive file uploader  
- Result visualizer (SVG/CAD/JSON)

### Backend
- Node.js / Flask (Python APIs)  
- File parsing, AI logic, database connection

### File Parsers
- `ezdxf` – DXF file handler  
- `PyMuPDF`, `pdfplumber` – PDF parser  
- `Tesseract` – OCR for scanned PDFs

### AI/ML
- **YOLOv8 / Detectron2** – Component detection in images  
- **Transformer-based NLP** – For Q&A over extracted text  
- **Graph algorithms** – Wiring path analysis

### Database
- MongoDB – for structured storage of component and analysis data  
- PostgreSQL – optional, for relational structures

---

## 🧠 AI Use Cases

| Task                | Method                            |
|---------------------|-----------------------------------|
| Component Detection | CV with YOLOv8 or Detectron2      |
| OCR Text Extraction | Tesseract OCR                     |
| Entity Mapping      | Rule-based/NLP tagging            |
| Wire Path Analysis  | Vector-to-graph with pathfinding  |
| Compliance Check    | Rules engine + ML-based scoring   |
| Smart Queries       | Fine-tuned LLM + data retrieval   |

---

## 🔍 Sample Output Format

```json
{
  "components": [
    { "type": "switch", "coordinates": [212, 430], "label": "S1", "room": "Kitchen" },
    { "type": "light", "coordinates": [500, 320], "label": "L1", "room": "Living Room" }
  ],
  "wires": [
    { "from": "S1", "to": "L1", "type": "phase" }
  ],
  "compliance_issues": [
    { "message": "Too many sockets in one circuit", "location": "Bedroom" }
  ]
}
```

---

## 🔄 System Workflow

1. Upload PDF / DWG / DXF  
2. File conversion and text/image extraction  
3. Component & wiring detection (AI + logic)  
4. Data preprocessing into structured format  
5. AI-driven analysis and compliance validation  
6. Dashboard display  
7. Smart Q&A or report generation

---

## 🧪 Example Use Cases

- Upload an electrical PDF → extract all symbols and wiring  
- Ask: “How many sockets are in Bedroom 2?”  
- Highlight compliance issues (e.g., overloaded circuits)  
- Visualize plan with highlighted components and paths

---

## 📦 Required Data & Tools

- 100+ Electrical drawings in PDF and DWG formats  
- Annotated datasets for training object detection models  
- Annotation tools: LabelImg, CVAT

---

## 📅 Project Timeline

| Week     | Tasks                                                  |
|----------|--------------------------------------------------------|
| 1–2      | Collect files and build dataset                        |
| 3–4      | File parsers and basic converter                       |
| 5–6      | Train object detection model                           |
| 7–8      | Develop wiring path analyzer and compliance checker    |
| 9–10     | Backend APIs and data storage                          |
| 11–12    | Frontend dashboard development                         |
| 13–14    | Integrate NLP Q&A and search                           |
| 15–16    | Final testing, optimization, documentation             |

---

## 🔐 Optional Features

- 3D layout viewer using Three.js  
- BOM (Bill of Materials) Generator  
- Compliance export (e.g., NEC/IEC reports)  
- Multi-language plan support  
- SCADA/BIM integration

---

## 🛠 Tools and Libraries

| Category        | Tools/Libraries                            |
|-----------------|--------------------------------------------|
| File Parsing     | `ezdxf`, `PyMuPDF`, `pdfplumber`           |
| OCR              | `Tesseract`, `EasyOCR`                     |
| AI/ML            | `YOLOv8`, `Detectron2`, `Transformers`     |
| Frontend         | React, Tailwind, Plotly/D3.js              |
| Backend/API      | Flask, FastAPI, Node.js                    |
| Database         | MongoDB, PostgreSQL                        |
| Annotation Tool  | LabelImg, CVAT                             |

---

## 👨‍💻 Maintainer

- Project by: **Psychotic**  
- AI/Software Development by: *ChatGPT + Psychotic*  
- Purpose: Empower smart electrical plan understanding via AI

---

## 📬 Want Help?

Need code scaffolding, model training scripts, or a GitHub boilerplate?  
Ask ChatGPT: _“Generate starter code for ElectroVision AI backend”_

---
