"""📁 File Handler Pro + Voice File Assistant

Install: pip install streamlit SpeechRecognition
Run:     streamlit run app.py
"""

import hashlib
import io
import re
from pathlib import Path

import streamlit as st

try:
    import speech_recognition as sr
except ImportError:
    sr = None

st.set_page_config(page_title="File Handler Pro", page_icon="📁", layout="centered")

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# CSS: Hides the menu/footer but KEEPS the sidebar toggle arrow visible
st.markdown("""
<style>
#MainMenu, footer, .stDeployButton {visibility:hidden;}
[data-testid="stHeader"] {background: transparent !important; height: 0 !important;}
[data-testid="stSidebarCollapsedControl"] {visibility: visible !important; display: block !important;}
.main-title {font-size:2.3rem;font-weight:700;margin-bottom:0}
.subtitle {color:#888;margin-top:0;margin-bottom:1.5rem}
.stButton>button {width:100%;border-radius:8px;font-weight:600;padding:.5rem 1rem}
.result-box {padding:.9rem 1.1rem;border-radius:10px;margin-top:1rem}
</style>
""", unsafe_allow_html=True)


def safe_name(value: str) -> str:
    name = value.strip().strip('"').strip("'")
    if (not name or name in {".", ".."} or Path(name).name != name
            or "/" in name or "\\" in name or "\x00" in name):
        raise ValueError("Use a single file or folder name without a path.")
    return name


def safe_path(value: str, *, must_exist: bool = False, folder: bool = False) -> Path:
    name = safe_name(value)
    candidate = STORAGE_DIR / name
    resolved = candidate.resolve()
    if resolved.parent != STORAGE_DIR.resolve():
        raise ValueError("That name is not allowed inside storage.")
    if must_exist and (not candidate.exists() or (folder and not candidate.is_dir())
                       or (not folder and not candidate.is_file())):
        raise FileNotFoundError(f"No such {'folder' if folder else 'file'}: {name}")
    return candidate


def all_files():
    return sorted((p for p in STORAGE_DIR.rglob("*") if p.is_file()), key=lambda p: str(p).lower())


def file_by_name(value: str) -> Path:
    name = safe_name(value)
    matches = [p for p in all_files() if p.name.casefold() == name.casefold()]
    if len(matches) == 0:
        raise FileNotFoundError(f"No such file in storage: {name}")
    if len(matches) > 1:
        raise ValueError(f"More than one file is named {name}; use the CRUD screen.")
    return matches[0]


def success(msg): st.success(msg)
def error(msg): st.error(msg)
def info(msg): st.info(msg)

def display_files(files):
    if not files:
        info("No matching files found in storage.")
        return
    for p in files:
        st.write(f"📄 **{p.relative_to(STORAGE_DIR).as_posix()}** · {p.stat().st_size:,} bytes")


# --- Voice Command Helpers ---
CMD_PATTERNS = [
    ("folder", r"^(?:please\s+)?(?:create|make|add|new)\s+(?:a\s+|an\s+|the\s+)?(?:new\s+)?"
               r"(?:folder|directory)\s*(?:called|named|with\s+name)?\s*(.+)$"),
    ("create", r"^(?:please\s+)?(?:create|make|add|new)\s+(?:a\s+|an\s+|the\s+)?(?:new\s+)?"
               r"(?:text\s+|empty\s+)?file\s*(?:called|named|with\s+name)?\s*(.+)$"),
    ("rename", r"^(?:please\s+)?rename\s+(?:the\s+)?(?:file\s+)?(?:called\s+|named\s+)?"
               r"(.+?)\s+(?:to|as)\s+(.+)$"),
    ("delete", r"^(?:please\s+)?(?:delete|remove|erase)\s+(?:the\s+)?(?:file\s+)?"
               r"(?:called\s+|named\s+)?(.+)$"),
]

def normalize_command(text: str) -> str:
    cmd = re.sub(r"\s+", " ", text.strip().lower())
    cmd = re.sub(r"[.!?,;]+$", "", cmd)
    cmd = re.sub(r"\s+dot\s+", ".", cmd)
    cmd = re.sub(r"\s+underscore\s+", "_", cmd)
    return cmd.strip()

def transcribe(raw: bytes) -> str:
    if raw[:4] not in (b"RIFF", b"FORM", b"fLaC"):
        raise ValueError(f"Recorded audio format not supported (header {raw[:4]!r}).")
    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(raw)) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio)


# --- Layout ---
st.sidebar.title("📁 File Handler Pro")
st.sidebar.caption("Files are kept in the app's storage/ folder")

# The operation selector lives here in the sidebar
operation = st.sidebar.radio("Choose an operation", ["Create", "Read", "Update", "Delete", "Voice Assistant"],
    format_func=lambda x: {"Create":"📝 Create File", "Read":"📖 Read File", "Update":"✏️ Update File",
                           "Delete":"🗑️ Delete File", "Voice Assistant":"🎙️ Voice Assistant"}[x])

st.markdown('<p class="main-title">📁 File Handler Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Manage files in storage/ with CRUD controls or voice commands.</p>', unsafe_allow_html=True)
st.caption(f"Storage location: `{STORAGE_DIR}`")
st.info("💡 **Tip:** If the sidebar is hidden, click the **`>>` arrow** in the top-left corner or press the **`s`** key on your keyboard.")
st.divider()

if operation == "Create":
    st.subheader("📝 Create a New File")
    name = st.text_input("File name", placeholder="e.g. notes.txt")
    data = st.text_area("File content", placeholder="Type what you want to write...", height=150)
    if st.button("Create File", type="primary"):
        try:
            path = safe_path(name)
            if path.exists(): error(f"A file or folder named **{path.name}** already exists.")
            else:
                path.write_text(data, encoding="utf-8")
                success(f"File **{path.name}** created successfully in storage.")
        except Exception as exc: error(str(exc))

elif operation == "Read":
    st.subheader("📖 Read a File")
    name = st.text_input("File name", placeholder="e.g. notes.txt")
    if st.button("Read File", type="primary"):
        try:
            path = safe_path(name, must_exist=True)
            content = path.read_text(encoding="utf-8")
            success(f"Loaded **{path.name}**")
            st.code(content, language=None)
            st.download_button("⬇️ Download file", data=content, file_name=path.name)
        except Exception as exc: error(str(exc))

elif operation == "Update":
    st.subheader("✏️ Update a File")
    name = st.text_input("File name", placeholder="e.g. notes.txt")
    action = st.radio("What would you like to do?", ["Rename file", "Append content", "Overwrite content"])
    if action == "Rename file":
        new_name = st.text_input("New file name")
        if st.button("Rename", type="primary"):
            try:
                path = safe_path(name, must_exist=True)
                target = path.with_name(safe_name(new_name))
                if target.exists(): error(f"A file or folder named **{target.name}** already exists.")
                else:
                    path.rename(target)
                    success(f"Renamed **{path.name}** → **{target.name}**")
            except Exception as exc: error(str(exc))
    elif action == "Append content":
        data = st.text_area("Content to append", height=120)
        if st.button("Append", type="primary"):
            try:
                path = safe_path(name, must_exist=True)
                with path.open("a", encoding="utf-8") as fs: fs.write("\n" + data)
                success(f"Content appended to **{path.name}**")
            except Exception as exc: error(str(exc))
    else:
        data = st.text_area("New content (replaces existing content)", height=120)
        if st.button("Overwrite", type="primary"):
            try:
                path = safe_path(name, must_exist=True)
                path.write_text(data, encoding="utf-8")
                success(f"**{path.name}** overwritten successfully")
            except Exception as exc: error(str(exc))

elif operation == "Delete":
    st.subheader("🗑️ Delete a File")
    name = st.text_input("File name", placeholder="e.g. notes.txt")
    confirm = st.checkbox("I understand this action cannot be undone")
    if st.button("Delete File", type="primary", disabled=not confirm):
        try:
            path = safe_path(name, must_exist=True)
            path.unlink()
            success(f"File **{path.name}** deleted successfully.")
        except Exception as exc: error(str(exc))
    if not confirm: info("Check the confirmation box to enable deletion.")

else:
    st.subheader("🎙️ Voice File Assistant")
    st.write("Try: “Create a file called notes.txt”, “Create a folder called College”, "
             "“Show all PDF files”, or “How much storage am I using?”")

    if sr is None:
        st.error("SpeechRecognition is not installed. Install it with: pip install SpeechRecognition")
    else:
        recording = st.audio_input("Record a command")
        if recording is not None:
            raw = recording.getvalue() if hasattr(recording, "getvalue") else recording.read()
            digest = hashlib.md5(raw).hexdigest()
            if st.session_state.get("audio_digest") != digest:
                st.session_state.audio_digest = digest
                st.session_state.transcript = ""
                st.session_state.pending_delete = None
                try:
                    with st.spinner("Transcribing…"):
                        st.session_state.transcript = transcribe(raw)
                except sr.UnknownValueError:
                    error("I couldn't understand that recording. Please try again.")
                except sr.RequestError as exc:
                    error(f"Speech recognition service is unavailable: {exc}")
                except Exception as exc:
                    error(f"Could not process recording: {exc}")

        transcript = st.session_state.get("transcript", "")
        if transcript:
            st.write(f"**You said:** {transcript}")
            cmd = normalize_command(transcript)
            found = None; kind = None
            for k, pattern in CMD_PATTERNS:
                m = re.match(pattern, cmd)
                if m: found, kind = m, k; break

            try:
                if found:
                    if kind == "folder":
                        path = safe_path(found.group(1))
                        if path.exists(): error(f"A file or folder named **{path.name}** already exists.")
                        else: path.mkdir(); success(f"Folder **{path.name}** created in storage.")
                    elif kind == "create":
                        path = safe_path(found.group(1))
                        if path.exists(): error(f"A file or folder named **{path.name}** already exists.")
                        else: path.touch(); success(f"File **{path.name}** created in storage.")
                    elif kind == "rename":
                        source = file_by_name(found.group(1))
                        target = source.with_name(safe_name(found.group(2)))
                        if target.exists(): error(f"A file or folder named **{target.name}** already exists.")
                        else: source.rename(target); success(f"Renamed **{source.name}** → **{target.name}**")
                    else:
                        path = file_by_name(found.group(1))
                        st.session_state.pending_delete = str(path.relative_to(STORAGE_DIR))
                elif re.search(r"\b(show|list|find)\b.*\bpdfs?\b", cmd):
                    st.markdown("**PDF files in storage:**")
                    display_files([p for p in all_files() if p.suffix.casefold() == ".pdf"])
                elif re.search(r"\b(show|list|find)\b.*\bfiles?\b", cmd):
                    st.markdown("**Files in storage:**")
                    display_files(all_files())
                elif re.search(r"\b(largest|biggest)\b.*\bfile\b", cmd):
                    files = all_files()
                    if files:
                        p = max(files, key=lambda f: f.stat().st_size)
                        st.write(f"💾 Largest file: **{p.relative_to(STORAGE_DIR).as_posix()}** · {p.stat().st_size:,} bytes")
                    else: info("Storage is empty.")
                elif re.search(r"\b(how\s+much|how\s+many)\b.*\b(storage|space)\b", cmd) or re.search(r"\b(storage|disk)\s+(usage|used|space)\b", cmd):
                    files = all_files()
                    total = sum(p.stat().st_size for p in files)
                    st.write(f"💾 **{len(files)} files** use **{total:,} bytes** ({total / (1024 ** 2):.2f} MiB).")
                else: info("Command not recognized. Use one of the examples above.")
            except Exception as exc: error(str(exc))

    pending = st.session_state.get("pending_delete")
    if pending:
        st.warning(f"Delete **{pending}**? This cannot be undone.")
        col1, col2 = st.columns(2)
        if col1.button("Confirm Delete", type="primary"):
            try:
                path = (STORAGE_DIR / pending).resolve()
                if STORAGE_DIR.resolve() not in path.parents: raise ValueError("Invalid storage path.")
                if not path.is_file(): raise FileNotFoundError("The file no longer exists.")
                path.unlink(); success(f"Deleted **{pending}**")
            except Exception as exc: error(str(exc))
            finally: st.session_state.pop("pending_delete", None)
        if col2.button("Cancel"):
            st.session_state.pop("pending_delete", None); info("Delete cancelled.")