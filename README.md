
# 🖋️ LocalSign: Private PDF & Word Auto-Signer

> **"Because privacy shouldn't cost $20/month."** \> A 100% offline desktop tool to automate document signing, replacing cloud-dependent services with local cryptographic security.

-----

### 📺 Watch it in Action

[Drop your Video or GIF here\! Just drag the file into this spot on GitHub]

-----

### 🌟 Why I Built This (The "Problem")

My father’s business workflow required constant PDF conversion and signing. Existing tools were either expensive (Adobe) or a privacy risk (Online Signers). I built **LocalSign** to:

1.  **Protect Data:** No document ever leaves the local machine.
2.  **Save Time:** Automate the "Word → PDF → Sign" loop into a single click.
3.  **Zero Friction:** Generate professional signatures without needing a PNG.

-----

### 🛠️ The Tech Stack

| Category | Tool | Why? |
| :--- | :--- | :--- |
| **Language** | **Python** | Rapid prototyping & powerful libraries. |
| **GUI** | **Tkinter** | Lightweight, native desktop feel. |
| **PDF Engine** | **PyMuPDF** | High-speed document manipulation. |
| **Image Core** | **Pillow** | Dynamic signature rendering. |
| **Conversion** | **docx2pdf** | Bridges the gap between Word & PDF. |

-----

### ✨ Key Features (v1.0)

  * **🎨 Style Engine:** Type your name and instantly choose from 5+ professional handwritten fonts.
  * **📄 Word Integration:** Drag a `.docx` file in; it converts and signs it in the background using **Multithreading**.
  * **🔍 Selective Signing:** A visual grid preview to pick exactly which pages get the stamp.
  * **🔐 SHA-256 Security:** Every signed file gets a unique **Digital Fingerprint** (Hash). If a single comma is changed after signing, the hash won't match.

-----

### 🛡️ Security: The "SHA-256" Key

To ensure **Data Integrity**, LocalSign calculates a SHA-256 hash of the final document.

  * **What it does:** It turns your file into a 64-character code.
  * **Why it matters:** It proves the document hasn't been tampered with after you signed it.

> *Example Hash: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`*

-----

### 🚀 Roadmap: What's coming in v2.0

  * [ ] **Batch Mode:** Sign a whole folder of 50 documents at once.
  * [ ] **Drag & Drop Placement:** Move the signature anywhere on the page with your mouse.
  * [ ] **Verify Tool:** A built-in "Validator" to check if a signed file's SHA key is still valid.
  * [ ] **Dark Mode:** For those late-night business sessions.

-----

### 💻 Local Setup

1.  **Clone:** `git clone https://github.com/ritiksharma/localsign.git`
2.  **Install:** `pip install -r requirements.txt`
3.  **Run:** `python3 sign_app.py`

-----

**Built with ❤️ for my Father.** *Check out my other projects on [GitHub](https://github.com/ritiksharma33)*

-----
