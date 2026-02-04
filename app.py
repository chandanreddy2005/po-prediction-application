import streamlit as st
import json
from classifier import classify_po

st.set_page_config(page_title="PO Category Classifier", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Space Grotesk', sans-serif;
    }
    .app-hero {
        background: linear-gradient(135deg, #f8f7ff 0%, #e8f0ff 60%, #fef6e4 100%);
        border: 1px solid #e8e7f0;
        border-radius: 18px;
        padding: 24px 28px;
        margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(25, 20, 60, 0.08);
    }
    .app-hero h1 {
        margin: 0 0 6px 0;
        font-size: 2.1rem;
        letter-spacing: -0.02em;
        color: #1b1a27;
    }
    .app-hero p {
        margin: 0;
        color: #46445c;
        font-size: 1rem;
    }
    .pill {
        display: inline-block;
        background: #111827;
        color: #f9fafb;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        margin-right: 6px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .card {
        background: #ffffff;
        border: 1px solid #eceaf5;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 12px 24px rgba(17, 24, 39, 0.05);
    }
    .metric {
        background: #f8fafc;
        border: 1px solid #e7e5f2;
        border-radius: 12px;
        padding: 12px 14px;
        text-align: center;
    }
    .metric h3 {
        margin: 0;
        font-size: 1.1rem;
        color: #111827;
    }
    .metric span {
        color: #6b7280;
        font-size: 0.78rem;
    }
    .stButton > button {
        background: #111827;
        color: #f9fafb;
        border-radius: 12px;
        padding: 10px 18px;
        border: 1px solid #111827;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: #1f2937;
        border-color: #1f2937;
    }
    .stTextArea textarea, .stTextInput input {
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="app-hero">
        <span class="pill">Procurement</span>
        <span class="pill">L1 · L2 · L3</span>
        <h1>PO Category Classifier</h1>
        <p>Classify purchase order descriptions into structured taxonomy in seconds.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "input_po" not in st.session_state:
    st.session_state.input_po = ""
if "input_supplier" not in st.session_state:
    st.session_state.input_supplier = ""

sidebar = st.sidebar
sidebar.header("Run Settings")
show_raw = sidebar.toggle("Show raw model output", value=False)
save_history = sidebar.toggle("Save to history", value=True)

with sidebar.expander("Tips"):
    st.markdown(
        "- Use specific item names and materials.\n"
        "- Add unit or grade where relevant.\n"
        "- Include supplier if known."
    )

col_left, col_right = st.columns([1.05, 0.95], gap="large")

with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Input")
    po_description = st.text_area(
        "PO Description",
        height=160,
        placeholder="e.g., 500 units of stainless steel bolts, grade 316",
        key="input_po",
    )
    supplier = st.text_input(
        "Supplier (optional)",
        placeholder="e.g., Fastenal",
        key="input_supplier",
    )

    action_cols = st.columns([1, 1, 1])
    with action_cols[0]:
        classify_clicked = st.button("Classify")
    with action_cols[1]:
        if st.button("Use Sample"):
            st.session_state.input_po = "CNC machining services for aluminum housings, 200 units"
            st.session_state.input_supplier = "PrecisionFab Inc"
    with action_cols[2]:
        if st.button("Clear"):
            st.session_state.input_po = ""
            st.session_state.input_supplier = ""
            st.session_state.last_result = None

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(" ")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Recent History")
    if st.session_state.history:
        for item in st.session_state.history[:5]:
            st.markdown(f"**{item['po'][:70]}**")
            st.caption(f"Supplier: {item['supplier'] or 'Not provided'}")
            st.divider()
    else:
        st.caption("No classifications yet.")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Output")
    l1_val, l2_val, l3_val = "—", "—", "—"

    if classify_clicked:
        if not po_description.strip():
            st.warning("Please enter a PO Description.")
        else:
            with st.spinner("Classifying..."):
                result = classify_po(po_description, supplier)
            st.session_state.last_result = result
            if save_history:
                st.session_state.history.insert(0, {"po": po_description, "supplier": supplier})

    if st.session_state.last_result:
        try:
            parsed = json.loads(st.session_state.last_result)
            if isinstance(parsed, dict):
                l1_val = parsed.get("L1") or parsed.get("l1") or "—"
                l2_val = parsed.get("L2") or parsed.get("l2") or "—"
                l3_val = parsed.get("L3") or parsed.get("l3") or "—"
            st.json(parsed)
        except Exception:
            st.error("Invalid model response.")
            if show_raw:
                st.code(st.session_state.last_result)
    else:
        st.caption("Results will appear here once you run a classification.")

    metric_cols = st.columns(3)
    metric_cols[0].markdown(
        f'<div class="metric"><h3>{l1_val}</h3><span>L1 Category</span></div>',
        unsafe_allow_html=True,
    )
    metric_cols[1].markdown(
        f'<div class="metric"><h3>{l2_val}</h3><span>L2 Subcategory</span></div>',
        unsafe_allow_html=True,
    )
    metric_cols[2].markdown(
        f'<div class="metric"><h3>{l3_val}</h3><span>L3 Detail</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
