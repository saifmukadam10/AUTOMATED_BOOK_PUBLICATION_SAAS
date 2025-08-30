# 📚 Automated Book Publication Workflow 📚

A Python-based AI-driven system for automating the workflow of fetching, paraphrasing, reviewing, editing, and versioning book chapters — with **human-in-the-loop controls** and **intelligent retrieval** using reinforcement learning-inspired scoring.

---

## 📌 Project Objective

The goal of this project is to build an **Automated Book Publication Software-as-a-Service (SaaS)** pipeline that:

- Scrapes chapter content and screenshots from public web sources.
- Applies AI paraphrasing (text spinning) and content review.
- Provides a **human-in-the-loop Streamlit-based editor** for final modifications.
- Stores multiple content versions in **ChromaDB** with metadata.
- Uses a **reward scoring system** (RL-inspired) to retrieve the best content version.

---

## 🚀 Core Features

- 📖 **Chapter Scraping & Screenshots** — Using Playwright for automated data extraction.  
- ✍️ **AI Writing (Spin Writer)** — Generates alternative phrasing via LLM APIs (Gemini / Ollama / Open Source).  
- 📝 **AI Content Review** — Feedback on content quality and readability.  
- 👨‍💻 **Human-in-the-Loop Editor** — Streamlit UI for manual editing and approval.  
- 🗂️ **Version Control with ChromaDB** — Track each saved content version with metadata.  
- 🏆 **Reinforcement Learning-inspired Search** — Reward scoring to pick the best version automatically.  
- 🎛️ **Modular & Scalable Python Codebase** — Easy to extend for additional features.

---

## 🖼️ Screenshots & Demo

**Dashboard Editor:**  
![Draft Editor Screenshot](images/draft_editor2.png)  

**AI Rephrase Preview:**  
![Rephrase Output Screenshot](images/rephrase_output.png)  

**Short Demo GIF (Optional):**  
![App Demo GIF](videos/demo.gif)  

---

## 🛠️ Tech Stack

- **Python 3.11+**  
- **Playwright** — for web scraping & screenshots  
- **Gemini API / Ollama** — for AI writing (LLMs)  
- **Streamlit** — human-in-the-loop UI  
- **ChromaDB** — content version storage & retrieval  
- **Reinforcement Learning-inspired Reward Scoring** — for best version selection  
- **Pandas, Matplotlib** — for data handling and visualization

---

## 📦 Installation & Local Setup

1️⃣ Clone this repository:  
```bash
git clone https://github.com/saifmukadam10/automated-book-publication.git
cd automated-book-publication
.git
cd automated-book-publication
