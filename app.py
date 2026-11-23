import streamlit as st
import os
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat with Research Paper",
    page_icon="📄",
    layout="wide",
)

# ── Load env ──────────────────────────────────────────────────────────────────
load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background: #0f1117; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #161b27;
        border-right: 1px solid #2a2f3e;
    }

    /* Title gradient */
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6c63ff, #48cfad);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        color: #8b93a7;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Status badge */
    .badge {
        display:inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-green  { background:#1a3a2a; color:#48cfad; border:1px solid #48cfad; }
    .badge-orange { background:#3a2a1a; color:#f39c12; border:1px solid #f39c12; }
    .badge-red    { background:#3a1a1a; color:#e74c3c; border:1px solid #e74c3c; }

    /* Paper info card */
    .paper-card {
        background: #1a1f2e;
        border: 1px solid #2a2f3e;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 1rem;
    }
    .paper-card h4 { color:#6c63ff; margin:0 0 6px 0; font-size:0.85rem; text-transform:uppercase; letter-spacing:1px; }
    .paper-card p  { color:#c0c8d8; margin:0; font-size:0.95rem; }

    /* Chat bubbles */
    .chat-user {
        background: linear-gradient(135deg, #6c63ff22, #6c63ff11);
        border: 1px solid #6c63ff44;
        border-radius: 12px 12px 4px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #e0e6f0;
    }
    .chat-bot {
        background: linear-gradient(135deg, #48cfad22, #48cfad11);
        border: 1px solid #48cfad44;
        border-radius: 12px 12px 12px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #e0e6f0;
    }

    /* Divider */
    hr { border-color: #2a2f3e; }

    /* Input override */
    .stTextInput input, .stTextArea textarea {
        background: #1a1f2e !important;
        color: #e0e6f0 !important;
        border: 1px solid #2a2f3e !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract all text from an uploaded PDF file."""
    reader = PdfReader(uploaded_file)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text.strip())
    return "\n\n".join(pages)


def get_gemini_response(api_key: str, paper_text: str, chat_history: list, user_question: str) -> str:
    """Send question to Gemini. Tries multiple models in order."""
    client = genai.Client(api_key=api_key)

    # Keep paper text small — 6000 chars (~4-5 pages)
    snippet = paper_text[:6000]

    full_prompt = f"""You are a research paper assistant.
Answer the question below using ONLY the paper text provided.
If the answer is not in the paper, say: "⚠️ This is not mentioned in the paper."
Keep your answer concise (3-5 sentences max).

PAPER TEXT:
{snippet}

QUESTION: {user_question}

ANSWER:"""

    # Try models in order — gemini-3.8-flash is the primary model in Google AI Studio
    models_to_try = [
        "gemini-3.8-flash",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-pro",
    ]

    last_error = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=full_prompt,
            )
            return response.text
        except Exception as e:
            last_error = e
            # If quota exceeded, don't try other models — same key won't help
            if "429" in str(e):
                raise e
            continue  # 404 = model not found, try next one

    raise last_error


# ── Session state init ────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "paper_text" not in st.session_state:
    st.session_state.paper_text = ""
if "paper_name" not in st.session_state:
    st.session_state.paper_name = ""
if "paper_pages" not in st.session_state:
    st.session_state.paper_pages = 0

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    # API key loaded silently from .env — not exposed to users
    api_key_input = API_KEY

    st.markdown("## 📄 Upload Paper")

    uploaded_file = st.file_uploader(
        "Choose a PDF research paper",
        type=["pdf"],
        help="Upload any research paper in PDF format",
    )

    if uploaded_file:
        if uploaded_file.name != st.session_state.paper_name:
            with st.spinner("📖 Reading PDF..."):
                text = extract_text_from_pdf(uploaded_file)
                if text.strip():
                    st.session_state.paper_text = text
                    st.session_state.paper_name = uploaded_file.name
                    st.session_state.paper_pages = len(PdfReader(uploaded_file).pages)
                    st.session_state.chat_history = []  # reset chat for new paper
                    st.success("✅ Paper loaded!")
                else:
                    st.error("❌ Could not extract text. Try a text-based PDF.")

    st.markdown("---")

    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    # Tips
    st.markdown("---")
    st.markdown("""
**💡 Sample questions:**
- What problem does this paper solve?
- What dataset did they use?
- What is the main method / model?
- What are the results?
- What are the limitations?
- What future work do they suggest?
""")

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">📄 Chat with Research Paper</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Upload any PDF research paper and ask questions about it — powered by Gemini AI</div>', unsafe_allow_html=True)

# Status bar
col1, col2, col3 = st.columns([2, 2, 2])
with col1:
    if api_key_input:
        st.markdown('<span class="badge badge-green">🔑 API Key Ready</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-red">🔑 No API Key</span>', unsafe_allow_html=True)
with col2:
    if st.session_state.paper_text:
        st.markdown(f'<span class="badge badge-green">📄 Paper Loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-orange">📄 No Paper</span>', unsafe_allow_html=True)
with col3:
    if st.session_state.chat_history:
        count = len([m for m in st.session_state.chat_history if m["role"] == "user"])
        st.markdown(f'<span class="badge badge-green">💬 {count} Question(s)</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-orange">💬 No Messages Yet</span>', unsafe_allow_html=True)

st.markdown("---")

# Paper info card
if st.session_state.paper_text:
    words = len(st.session_state.paper_text.split())
    st.markdown(f"""
    <div class="paper-card">
        <h4>📋 Loaded Paper</h4>
        <p><strong>{st.session_state.paper_name}</strong></p>
        <p style="color:#8b93a7; font-size:0.85rem; margin-top:4px;">
            {st.session_state.paper_pages} pages &nbsp;·&nbsp; ~{words:,} words extracted
        </p>
    </div>
    """, unsafe_allow_html=True)

# ── Chat display ──────────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#8b93a7;">
            <div style="font-size:4rem;">💬</div>
            <div style="font-size:1.2rem; margin-top:1rem;">No messages yet</div>
            <div style="font-size:0.9rem; margin-top:0.5rem;">
                Upload a research paper from the sidebar, then ask your first question below.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="🧑‍🎓"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
st.markdown("---")
user_input = st.chat_input(
    "Ask a question about the paper…",
    disabled=(not st.session_state.paper_text or not api_key_input),
)

if user_input:
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Get AI response — simple blocking call, no streaming
    with st.spinner("🤖 Thinking..."):
        try:
            answer = get_gemini_response(
                api_key=api_key_input,
                paper_text=st.session_state.paper_text,
                chat_history=st.session_state.chat_history,
                user_question=user_input,
            )
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
        except Exception as e:
            err = f"❌ **Error:** {str(e)}"
            st.session_state.chat_history.append({"role": "assistant", "content": err})

    st.rerun()
