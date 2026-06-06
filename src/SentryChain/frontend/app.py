import os
import requests
import streamlit as st


st.set_page_config(
    page_title="SentryChain AI",
    page_icon="SC",
    layout="centered",
)

st.markdown(
    """
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
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
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")
    default_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    api_url = st.text_input("API Base URL", value=default_url)
    st.markdown("---")
    st.markdown(
        "**SentryChain AI** monitors vendor contracts and alerts you when an SLA violation may have occurred."
    )
    st.markdown("---")
    st.caption("Made by Gourav - v0.1")

BASE_URL = api_url.rstrip("/")


def api_get(path):
    try:
        response = requests.get(f"{BASE_URL}{path}", timeout=300)
        if not response.ok:
            try:
                return None, response.json().get("detail", response.text)
            except ValueError:
                return None, response.text
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the API. Make sure the FastAPI server is running."
    except Exception as e:
        return None, str(e)


def api_post(path, payload=None, files=None):
    try:
        if files:
            response = requests.post(f"{BASE_URL}{path}", files=files, timeout=1200)
        else:
            response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=1200)

        if not response.ok:
            try:
                return None, response.json().get("detail", response.text)
            except ValueError:
                return None, response.text
        return response.json(), None
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to the API. Make sure the FastAPI server is running."
    except Exception as e:
        return None, str(e)


def api_post_stream(path, payload):
    response = requests.post(
        f"{BASE_URL}{path}",
        json=payload,
        stream=True,
        timeout=1200,
    )
    response.raise_for_status()

    for chunk in response.iter_content(chunk_size=64, decode_unicode=True):
        if chunk:
            yield chunk


st.markdown('<div class="main-title">SentryChain AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Automated SLA Violation Detection - Powered by RAG + Knowledge Graphs</div>',
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs(["Contracts", "Upload", "Query", "Monitor"])


with tab1:
    st.subheader("Loaded Contracts")
    st.caption("These are the contracts currently stored in the system.")

    if st.button("Refresh Contracts"):
        data, err = api_get("/contracts")
        if err:
            st.error(err)
        else:
            contracts = data.get("Contracts", [])
            if not contracts:
                st.info("No contracts found. Upload one in the Upload tab.")
            else:
                for contract in contracts:
                    with st.expander(
                        f"{contract['supplier_name']} - `{contract['Contract_id']}`"
                    ):
                        detail, detail_error = api_get(
                            f"/contracts/{contract['Contract_id']}"
                        )
                        if detail_error:
                            st.error(detail_error)
                        else:
                            st.json(detail.get("Metadata", {}))


with tab2:
    st.subheader("Upload a New Contract")
    st.caption("Upload a PDF SLA contract. The system will parse, embed, and store it automatically.")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.info(
            f"Selected: **{uploaded_file.name}** ({round(uploaded_file.size / 1024, 1)} KB)"
        )

        if st.button("Ingest Contract"):
            with st.spinner("Parsing and embedding contract... this may take a minute."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                }
                result, err = api_post("/ingest", files=files)
            if err:
                st.error(f"Ingestion failed: {err}")
            else:
                st.success(result.get("message", "Contract ingested successfully!"))


with tab3:
    st.subheader("Ask a Question About a Contract")
    st.caption("Type a natural language question and pick the contract you want to query.")

    contract_id_q = st.text_input("Contract ID", placeholder="e.g. microsoft_sla")
    question = st.text_area(
        "Your Question",
        placeholder="What is the uptime guarantee? What happens if they breach it?",
        height=100,
    )

    if st.button("Ask"):
        if not contract_id_q or not question:
            st.warning("Please fill in both the contract ID and the question.")
        else:
            st.markdown("**Answer:**")
            answer_box = st.empty()
            full_answer = ""

            try:
                with st.spinner("Searching contract..."):
                    stream = api_post_stream(
                        "/query/stream",
                        {"question": question, "contract_id": contract_id_q},
                    )
                    for token in stream:
                        full_answer += token
                        answer_box.markdown(
                            f'<div class="verdict-box">{full_answer}</div>',
                            unsafe_allow_html=True,
                        )

                if not full_answer:
                    answer_box.markdown(
                        '<div class="verdict-box">No answer returned.</div>',
                        unsafe_allow_html=True,
                    )
            except requests.exceptions.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    result, err = api_post(
                        "/query",
                        payload={"question": question, "contract_id": contract_id_q},
                    )
                    if err:
                        st.error(f"Query failed: {err}")
                    else:
                        answer_box.markdown(
                            f'<div class="verdict-box">{result.get("answer", "No answer returned.")}</div>',
                            unsafe_allow_html=True,
                        )
                    st.info(
                        "Streaming endpoint was not found on this backend, so the app used the normal query endpoint."
                    )
                else:
                    try:
                        error_detail = e.response.json().get("detail", e.response.text)
                    except ValueError:
                        error_detail = e.response.text
                    st.error(f"Query failed: {error_detail}")
            except Exception as e:
                st.error(f"Query failed: {e}")


with tab4:
    st.subheader("SLA Violation Monitor")
    st.caption("Enter a contract ID to scan the latest news for potential SLA breaches.")

    contract_id_m = st.text_input(
        "Contract ID to Monitor", placeholder="e.g. microsoft_sla"
    )

    if st.button("Run Monitor"):
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

                verified = result.get("is_verified")
                if verified:
                    st.success("Verdict is grounded. No hallucinations detected.")
                elif verified is False:
                    st.warning(
                        f"Possible hallucinations: {result.get('hallucinations', [])}"
                    )
                else:
                    st.info("Verification status unknown.")

                st.markdown("**Verdict:**")
                st.markdown(
                    f'<div class="verdict-box">{result.get("verdict", "")}</div>',
                    unsafe_allow_html=True,
                )

                with st.expander("News Articles Used"):
                    news = result.get("news_used", [])
                    if news:
                        for article_title in news:
                            st.markdown(f"- {article_title}")
                    else:
                        st.caption("No articles listed.")
