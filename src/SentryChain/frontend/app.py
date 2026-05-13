import streamlit as st
import requests
import json

# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentryChain AI",
    page_icon="🔗",
    layout="centered",
)

# ── simple styling ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f2937;
    }
    .sub-title {
        color: #6b7280;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .verdict-box {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
        color: #1f2937; 
    }
    .warning-box {
        background: #fefce8;
        border-left: 4px solid #eab308;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
    }
    .error-box {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 6px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    import os
    default_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    api_url = st.text_input("API Base URL", value=default_url)
    st.markdown("---")
    st.markdown("**SentryChain AI** monitors your vendor contracts and alerts you when an SLA violation occurs.")
    st.markdown("---")
    st.caption("Made by Gourav · v0.1")

BASE_URL = api_url.rstrip("/")

# ── helpers ───────────────────────────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(f"{BASE_URL}{path}", timeout=300)
        if not r.ok:
            try:
                return None, r.json().get("detail", r.text)
            except:
                return None, r.text
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the API. Make sure the FastAPI server is running."
    except Exception as e:
        return None, str(e)

def api_post(path, payload=None, files=None):
    try:
        if files:
            r = requests.post(f"{BASE_URL}{path}", files=files, timeout=1200)
        else:
            r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=1200)
        
        if not r.ok:
            try:
                return None, r.json().get("detail", r.text)
            except:
                return None, r.text
        return r.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the API. Make sure the FastAPI server is running."
    except Exception as e:
        return None, str(e)

# ── header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🔗 SentryChain AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Automated SLA Violation Detection · Powered by RAG + Knowledge Graphs</div>', unsafe_allow_html=True)

# ── tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📋 Contracts", "📤 Upload", "🔍 Query", "🚨 Monitor"])


# ─── TAB 1: list contracts ────────────────────────────────────────────────────
with tab1:
    st.subheader("Loaded Contracts")
    st.caption("These are the contracts currently stored in the system.")

    if st.button("🔄 Refresh Contracts"):
        data, err = api_get("/contracts")
        if err:
            st.error(err)
        else:
            contracts = data.get("Contracts", [])
            if not contracts:
                st.info("No contracts found. Upload one in the Upload tab.")
            else:
                for c in contracts:
                    with st.expander(f"📄 {c['supplier_name']}  —  `{c['Contract_id']}`"):
                        detail, derr = api_get(f"/contracts/{c['Contract_id']}")
                        if derr:
                            st.error(derr)
                        else:
                            st.json(detail.get("Metadata", {}))


# ─── TAB 2: upload ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Upload a New Contract")
    st.caption("Upload a PDF SLA contract. The system will parse, embed, and store it automatically.")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.info(f"Selected: **{uploaded_file.name}**  ({round(uploaded_file.size / 1024, 1)} KB)")

        if st.button("🚀 Ingest Contract"):
            with st.spinner("Parsing and embedding contract... this may take a minute."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                result, err = api_post("/ingest", files=files)
            if err:
                st.error(f"Ingestion failed: {err}")
            else:
                st.success(result.get("message", "Contract ingested successfully!"))


# ─── TAB 3: query ─────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Ask a Question About a Contract")
    st.caption("Type a natural language question and pick the contract you want to query.")

    contract_id_q = st.text_input("Contract ID", placeholder="e.g. microsoft_sla_parsed")
    question = st.text_area("Your Question", placeholder="What is the uptime guarantee? What happens if they breach it?", height=100)

    if st.button("🔎 Ask"):
        if not contract_id_q or not question:
            st.warning("Please fill in both the contract ID and the question.")
        else:
            with st.spinner("Searching contract..."):
                result, err = api_post("/query", payload={"question": question, "contract_id": contract_id_q})
            if err:
                st.error(f"Query failed: {err}")
            else:
                st.markdown("**Answer:**")
                st.markdown(f'<div class="verdict-box">{result.get("answer", "No answer returned.")}</div>', unsafe_allow_html=True)
                st.caption(f"Supplier: {result.get('supplier_name')}  |  Sources: {result.get('sources', [])}")


# ─── TAB 4: monitor ───────────────────────────────────────────────────────────
with tab4:
    st.subheader("🚨 SLA Violation Monitor")
    st.caption("Enter a contract ID to scan the latest news for potential SLA breaches.")

    contract_id_m = st.text_input("Contract ID to Monitor", placeholder="e.g. microsoft_sla_parsed")

    if st.button("📡 Run Monitor"):
        if not contract_id_m:
            st.warning("Please enter a contract ID.")
        else:
            with st.spinner("Fetching news and comparing against SLA clauses..."):
                result, err = api_post("/monitor", payload={"contract_id": contract_id_m})

            if err:
                st.error(f"Monitor failed: {err}")
            elif result.get("message"):
                st.info(result["message"])
            else:
                st.markdown(f"**Supplier:** {result.get('supplier_name')}")

                # is_verified indicator
                verified = result.get("is_verified")
                if verified:
                    st.success("✅ Verdict is grounded — no hallucinations detected.")
                elif verified is False:
                    st.warning(f"⚠️ Possible hallucinations: {result.get('hallucinations', [])}")
                else:
                    st.info("Verification status unknown.")

                st.markdown("**Verdict:**")
                st.markdown(f'<div class="verdict-box">{result.get("verdict", "")}</div>', unsafe_allow_html=True)

                with st.expander("📰 News Articles Used"):
                    news = result.get("news_used", [])
                    if news:
                        for n in news:
                            st.markdown(f"- {n}")
                    else:
                        st.caption("No articles listed.")