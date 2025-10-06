# 🧾 fastapi-streamlit-template

An advanced **Interactive Resume Builder** built with **FastAPI** (backend) and **Streamlit** (frontend).  
It generates elegant, two-column resumes with full **Arabic (RTL)** support, dynamic themes, and modular sections.

---

## 🧠 Project Concept

**fastapi-streamlit-template** is an interactive web system designed to help users create, customize, and export professional resumes as PDF files.  
It seamlessly combines a **FastAPI-powered backend** for PDF generation with a **Streamlit-based frontend** for real-time editing and customization.

Users can:
- Fill in personal and professional data using an intuitive interface.
- Choose from multiple modern themes.
- Generate a resume instantly in PDF format.
- Support Arabic, English, and German text.
- Save and reuse profile data anytime.

---

## ⚙️ Technical Overview

### **1. Backend (FastAPI)**
- Generates dynamic PDFs using **ReportLab**.
- Modular structure of “blocks” (e.g., header, projects, skills, education, languages).
- Full **RTL and Arabic font rendering**.
- Customizable themes and color palettes.
- Local asset system for fonts and icons (no external dependencies).

### **2. Frontend (Streamlit)**
- Multi-tab interface for editing sections:  
  *Basic Info, Skills, Projects, Education, Languages, Headshot, etc.*
- Interactive preview and instant generation.
- Communicates directly with FastAPI through REST endpoints.

### **3. Themes System**
- Configurable `.json` files defining colors, borders, fonts, and layout.
- Predefined themes: `default`, `modern`, `clean-white`, `bold-header`, `bold-panel`.

### **4. Profiles & Outputs**
- Automatically saves user profiles in `profiles/`.
- Stores generated PDF files in `outputs/`.

---

## ✨ Key Competitive Features

| Feature | Description |
|----------|--------------|
| 🎨 **Two-column Layout** | Professional balance between information and design. |
| 🌍 **Multilingual Support** | Arabic (RTL), English, and German text rendering. |
| 🧱 **Modular PDF Blocks** | Easily add or modify sections like Projects, Skills, or Contact Info. |
| 🖼️ **Icons & Images Support** | Uses local assets for reliability and customization. |
| 💾 **Profile Persistence** | Save and load user data with JSON profiles. |
| 🔧 **FastAPI × Streamlit Integration** | Real-time editing with seamless backend generation. |

---

## 🚀 Quick Start

```bash
# 1️⃣ Install dependencies
pip install -r requirements.txt

# 2️⃣ Run backend (FastAPI)
uvicorn api.main:app --reload

# 3️⃣ Run frontend (Streamlit)
streamlit run streamlit/app.py
```

- FastAPI docs → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- Streamlit UI → [http://localhost:8501](http://localhost:8501)

---

## 💡 Potential Use Cases

- 🎓 **Students & Job Seekers** — Create multilingual, modern resumes.  
- 🏢 **Recruitment Agencies** — Internal resume generator for applicants.  
- 🧑‍🏫 **Educational Platforms** — Help students build their first CVs.  
- 💻 **Developers & Freelancers** — Professional templates for portfolio resumes.

---

## 🧮 Economic & Feasibility Analysis

| Aspect | Assessment |
|---------|-------------|
| 💰 **Development Cost** | Low to medium — Python-based stack. |
| ⚙️ **Operational Cost** | Very low — deployable on Render, Hugging Face, or local servers. |
| 📈 **Monetization Potential** | High — can be turned into a SaaS platform (custom themes, premium exports). |
| 👥 **Target Audience** | Job seekers, universities, HR platforms, and freelancers. |

---

## 🚀 Future Development Opportunities

1. Add **user authentication** and PostgreSQL-based persistence.  
2. Create a **dashboard** to manage multiple resumes.  
3. Implement a **real-time visual editor (WYSIWYG)**.  
4. Allow **company branding and digital signatures** in PDFs.  
5. Build a **React or Flutter** frontend alternative.  
6. Integrate with **LinkedIn API** to auto-import profile data.  
7. Add **AI-based resume analysis** and improvement suggestions.

---

## 🧩 Evaluation Summary

| Criteria | Score | Notes |
|-----------|--------|-------|
| 💡 Innovation | ⭐⭐⭐⭐☆ | Unique integration of FastAPI and Streamlit for resume creation. |
| 💼 Feasibility | ⭐⭐⭐⭐⭐ | Highly achievable and scalable. |
| ⚙️ Technical Stability | ⭐⭐⭐⭐⭐ | Well-structured modular codebase. |
| 🖥️ Usability | ⭐⭐⭐⭐☆ | Simple and intuitive UI. |
| 🚀 Scalability | ⭐⭐⭐⭐⭐ | Easily extendable to a multi-user SaaS model. |

---

## 📂 Project Structure

```
fastapi-streamlit-template/
├── api/                 # FastAPI backend (PDF generation)
│   ├── pdf_utils/       # Fonts, icons, blocks, and themes loader
│   ├── routes/          # API endpoints
│   └── utils/           # Helper parsers
├── streamlit/           # Frontend tabs & UI logic
├── themes/              # Theme configuration files (.json)
├── outputs/             # Generated PDFs
├── profiles/            # Saved user profiles
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 📜 License

Licensed under the [MIT License](LICENSE) — © 2025 **Tamer Hamad Faour**
