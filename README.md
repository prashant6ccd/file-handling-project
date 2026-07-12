# 📁 File Handler Pro

A simple Python project for performing basic file operations — **Create, Read, Update, and Delete (CRUD)** — available in two versions:

- **`main.py`** — a command-line (terminal) version
- **`app.py`** — a web-based version built with [Streamlit](https://streamlit.io/), featuring a clean UI with icons and styled result messages

---

## ✨ Features

- 📝 **Create** a new file with custom content
- 📖 **Read** an existing file's content (with download option in the web version)
- ✏️ **Update** a file by:
  - Renaming it
  - Appending new content
  - Overwriting existing content
- 🗑️ **Delete** a file (with confirmation step in the web version)
- ✅ Error handling for missing files, duplicate names, and invalid input

---

## 🛠️ Tech Stack

- Python 3
- [Streamlit](https://streamlit.io/) (for the web UI in `app.py`)
- `pathlib` and `os` (standard library, for file handling)

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/prashant6ccd/file-handling-project.git
cd file-handling-project
```

### 2. Install dependencies
```bash
pip install streamlit
```

### 3. Run the project

**Command-line version:**
```bash
python main.py
```

**Web (Streamlit) version:**
```bash
streamlit run app.py
```

---

## 📂 Project Structure

```
file-handling-project/
│
├── app.py      # Streamlit web app (UI version)
├── main.py     # Command-line version
└── README.md   # Project documentation
```

---

## 📌 Notes

- All file operations work on files in the current working directory.
- The web version includes safety features like a confirmation checkbox before deletion.

---

## 🙋 Author

Made by **prashant6ccd**
