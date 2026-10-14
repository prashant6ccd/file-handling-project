"""
📁 File Handler Pro
A clean Streamlit UI for basic file operations: Create, Read, Update, Delete.
Run with:  streamlit run file_manager_app.py
"""

import streamlit as st
from pathlib import Path
import os

# ---------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="File Handler Pro",
    page_icon="📁",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------
# STYLING
# ---------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Hide Streamlit's default chrome: hamburger menu, Deploy button, header, footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    /* Hide the little anchor/link icons that appear next to headers on hover */
    [data-testid="stHeaderActionElements"] {display: none;}

    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0px;
    }
    .subtitle {
        color: #888;
        margin-top: 0px;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    .result-box {
        padding: 0.9rem 1.1rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------------
st.sidebar.title("📁 File Handler Pro")
st.sidebar.caption("A simple CRUD tool for local files")

operation = st.sidebar.radio(
    "Choose an operation",
    ["Create", "Read", "Update", "Delete"],
    format_func=lambda x: {
        "Create": "📝 Create File",
        "Read": "📖 Read File",
        "Update": "✏️ Update File",
        "Delete": "🗑️ Delete File",
    }[x],
)

st.sidebar.markdown("---")

# ---------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------
st.markdown('<p class="main-title">📁 File Handler Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Create, read, update, and delete files — right from your browser.</p>', unsafe_allow_html=True)
st.divider()


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------
def success(msg):
    st.markdown(f'<div class="result-box" style="background:#d4edda;color:#155724;">✅ {msg}</div>', unsafe_allow_html=True)

def error(msg):
    st.markdown(f'<div class="result-box" style="background:#f8d7da;color:#721c24;">❌ {msg}</div>', unsafe_allow_html=True)

def info(msg):
    st.markdown(f'<div class="result-box" style="background:#d1ecf1;color:#0c5460;">ℹ️ {msg}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------
if operation == "Create":
    st.subheader("📝 Create a New File")
    name = st.text_input("File name", placeholder="e.g. notes.txt")
    data = st.text_area("File content", placeholder="Type what you want to write...", height=150)

    if st.button("Create File", type="primary"):
        if not name.strip():
            error("Please enter a file name.")
        else:
            try:
                path = Path(name)
                if path.exists():
                    error(f"A file named **{name}** already exists.")
                else:
                    path.write_text(data)
                    success(f"File **{name}** created successfully!")
            except Exception as err:
                error(f"An error occurred: {err}")


# ---------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------
elif operation == "Read":
    st.subheader("📖 Read a File")
    name = st.text_input("File name", placeholder="e.g. notes.txt")

    if st.button("Read File", type="primary"):
        if not name.strip():
            error("Please enter a file name.")
        else:
            try:
                path = Path(name)
                if path.exists():
                    content = path.read_text()
                    success(f"Loaded **{name}**")
                    st.code(content, language=None)
                    st.download_button(
                        "⬇️ Download file", data=content, file_name=path.name
                    )
                else:
                    error(f"No such file: **{name}**")
            except Exception as err:
                error(f"An error occurred: {err}")


# ---------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------
elif operation == "Update":
    st.subheader("✏️ Update a File")
    name = st.text_input("File name", placeholder="e.g. notes.txt")

    action = st.radio(
        "What would you like to do?",
        ["Rename file", "Append content", "Overwrite content"],
        horizontal=False,
    )

    if action == "Rename file":
        new_name = st.text_input("New file name")
        if st.button("Rename", type="primary"):
            try:
                path = Path(name)
                new_path = Path(new_name)
                if not path.exists():
                    error(f"No such file: **{name}**")
                elif new_path.exists():
                    error(f"A file named **{new_name}** already exists.")
                else:
                    path.rename(new_path)
                    success(f"Renamed **{name}** → **{new_name}**")
            except Exception as err:
                error(f"An error occurred: {err}")

    elif action == "Append content":
        data = st.text_area("Content to append", height=120)
        if st.button("Append", type="primary"):
            try:
                path = Path(name)
                if not path.exists():
                    error(f"No such file: **{name}**")
                else:
                    with open(path, "a") as fs:
                        fs.write("\n" + data)
                    success(f"Content appended to **{name}**")
            except Exception as err:
                error(f"An error occurred: {err}")

    elif action == "Overwrite content":
        data = st.text_area("New content (replaces existing content)", height=120)
        if st.button("Overwrite", type="primary"):
            try:
                path = Path(name)
                if not path.exists():
                    error(f"No such file: **{name}**")
                else:
                    path.write_text(data)
                    success(f"**{name}** overwritten successfully")
            except Exception as err:
                error(f"An error occurred: {err}")


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
elif operation == "Delete":
    st.subheader("🗑️ Delete a File")
    name = st.text_input("File name", placeholder="e.g. notes.txt")

    confirm = st.checkbox("I understand this action cannot be undone")

    if st.button("Delete File", type="primary", disabled=not confirm):
        try:
            path = Path(name)
            if path.exists():
                path.unlink()
                success(f"File **{name}** deleted successfully.")
            else:
                error(f"No such file: **{name}**")
        except Exception as err:
            error(f"An error occurred: {err}")

    if not confirm:
        info("Check the confirmation box to enable deletion.")