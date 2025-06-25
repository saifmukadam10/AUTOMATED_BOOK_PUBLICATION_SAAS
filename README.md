# 📚 Automated Book Publication Workflow 📚

A Python-based AI-driven system for automating the workflow of fetching, paraphrasing, reviewing, editing, and versioning book chapters — with human-in-the-loop controls and intelligent retrieval using reinforcement learning-inspired scoring.

---

## 📌 Project Objective

Build an **Automated Book Publication Software-as-a-Service (SaaS)** pipeline that:

- Scrapes chapter content and screenshots from a public web source.
- Applies AI paraphrasing (text spinning) and AI content review.
- Provides a human-in-the-loop Streamlit-based editor for final modifications.
- Stores multiple content versions in ChromaDB with metadata.
- Uses a reward scoring system (RL-inspired) to retrieve the best version.

---

## 🚀 Core Features

- 📖 **Chapter Scraping & Screenshots** — Using Playwright.
- ✍️ **AI Writing (Spin Writer)** — Using LLM APIs (Gemini / Ollama / Open Source).
- 📝 **AI Content Review** — Feedback on content quality.
- 👨‍💻 **Human-in-the-Loop Editor** — Streamlit UI for manual editing.
- 🗂️ **Version Control with ChromaDB** — Track each saved content version.
- 🏆 **Reinforcement Learning-inspired Search** — Reward scoring to pick the best version.
- 🎛️ **Modular, Scalable Python Codebase**

---

## 🛠️ Tech Stack

- **Python 3.11+**
- **Playwright** — for web scraping & screenshots
- **Gemini API / Ollama** — for AI writing (LLMs)
- **Streamlit** — human-in-the-loop UI
- **ChromaDB** — content version storage & retrieval
- **Reinforcement Learning (basic reward scoring)** — for best version selection

---

## 📦 Installation & Setup

1️⃣ Clone this repository:
```bash
git clone https://github.com/saifmukadam10/automated-book-publication.git
cd automated-book-publication
