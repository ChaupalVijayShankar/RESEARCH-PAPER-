# 📄 Chat with Research Paper — PDF Q&A Bot

A Streamlit web app that lets you upload any research paper (PDF) and chat with it using Google Gemini AI.

## 🎯 Problem Statement (Problem 7)
**Chat with Research Paper (PDF Q&A Bot)**
- **Problem**: When reading a paper, students have doubts but can't easily find the answer inside a 15-page PDF.
- **Solution**: A chatbot where the student uploads a paper and asks questions about it.
- **Input**: Upload research paper (PDF), type question in chat.
- **Output**: Answers based only on the paper (if answer isn't in the paper, says *"⚠️ This is not mentioned in the paper."*), chat history shown on screen.
- **Tools**: Streamlit + Gemini API (`google-genai`) + `pypdf`.

---

## 🚀 Setup & Installation

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey).

### 3. Run the application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📖 How to Use
1. The app automatically loads your API key from `.env`.
2. In the sidebar, click **"Browse files"** to upload a PDF research paper.
3. Once loaded, the paper name, page count, and word count will appear.
4. Type your question in the chat box at the bottom.
5. Example questions to ask:
   - *"What problem does this paper solve?"*
   - *"What dataset did they use?"*
   - *"What is the main method / model?"*
   - *"What are the limitations?"*

---

## 🛠️ Tech Stack
- **Frontend / UI**: [Streamlit](https://streamlit.io/)
- **AI Model**: Google Gemini (`gemini-3.8-flash` via `google-genai`)
- **PDF Extraction**: [pypdf](https://pypdf.readthedocs.io/)
- **Configuration**: [python-dotenv](https://github.com/theskumar/python-dotenv)
