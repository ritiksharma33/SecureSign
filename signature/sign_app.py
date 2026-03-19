import fitz
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageTk
import json
import docx2pdf

# NEW IMPORTS FOR SECURITY
import hashlib
import qrcode
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes


CONFIG_FILE = "config.json"


class PDFSignerApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Local PDF Auto-Signer")
        self.root.geometry("1000x750")

        self.pdf_path = tk.StringVar()
        self.signature_path = tk.StringVar()
        self.user_name = tk.StringVar(value="Your Name")

        self.page_vars = []
        self.page_images = []
        self.generated_styles = []

        self.original_filename = ""

        # ---------- TOP ----------
        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(fill=tk.X)

        name_frame = ttk.Frame(top_frame)
        name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(name_frame, text="Signer Name:").pack(side=tk.LEFT)

        ttk.Entry(name_frame, textvariable=self.user_name, width=30).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            name_frame,
            text="Generate Signature Styles",
            command=self.generate_signature_styles
        ).pack(side=tk.LEFT, padx=10)

        pdf_frame = ttk.Frame(top_frame)
        pdf_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            pdf_frame,
            text="1. Select Word / PDF",
            command=self.select_file
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(pdf_frame, textvariable=self.pdf_path).pack(side=tk.LEFT)

        # ---------- SIGNATURE STYLE ----------
        self.style_frame = ttk.LabelFrame(root, text="2. Choose Signature Style", padding=10)
        self.style_frame.pack(fill=tk.X, padx=10, pady=5)

        self.style_canvas = tk.Canvas(self.style_frame, height=130)
        self.style_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.style_scroll = ttk.Scrollbar(self.style_frame, orient="horizontal", command=self.style_canvas.xview)
        self.style_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.style_canvas.configure(xscrollcommand=self.style_scroll.set)

        self.style_container = ttk.Frame(self.style_canvas)
        self.style_canvas.create_window((0,0), window=self.style_container, anchor="nw")

        self.style_container.bind(
            "<Configure>",
            lambda e: self.style_canvas.configure(scrollregion=self.style_canvas.bbox("all"))
        )

        # ---------- PDF PREVIEW ----------
        preview_label = ttk.Label(root, text="3. Select Pages to Sign")
        preview_label.pack(anchor=tk.W, padx=10)

        preview_container = ttk.Frame(root)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=10)

        self.canvas = tk.Canvas(preview_container)
        scrollbar = ttk.Scrollbar(preview_container, orient="vertical", command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.preview_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.preview_frame, anchor="nw")

        self.preview_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        ttk.Button(
            root,
            text="SIGN SELECTED PAGES",
            command=self.start_signing
        ).pack(fill=tk.X, padx=10, pady=10, ipady=10)

        self.status_var = tk.StringVar(value="Ready")

        ttk.Label(
            root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        ).pack(fill=tk.X, side=tk.BOTTOM)

        self.load_config()

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE,'r') as f:
                config=json.load(f)
                sig=config.get("signature_path")
                if sig and os.path.exists(sig):
                    self.signature_path.set(sig)

    def save_config(self):
        with open(CONFIG_FILE,'w') as f:
            json.dump({"signature_path":self.signature_path.get()},f)

    # -------------------------------------------------
    # SIGNATURE STYLE GENERATOR
    # -------------------------------------------------

    def generate_signature_styles(self):

        name = self.user_name.get().strip()

        if not name:
            messagebox.showwarning("Name Required","Please enter a name first.")
            return

        for w in self.style_container.winfo_children():
            w.destroy()

        self.generated_styles.clear()

        fonts = [
            "/System/Library/Fonts/Supplemental/Brush Script.ttf",
            "/System/Library/Fonts/Times.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Supplemental/Zapfino.ttf",
            "/System/Library/Fonts/Supplemental/Apple Chancery.ttf"
        ]

        for i, font_path in enumerate(fonts):

            img = Image.new("RGBA", (600,260), (255,255,255,0))
            draw = ImageDraw.Draw(img)

            try:
                font = ImageFont.truetype(font_path,80)
            except:
                font = ImageFont.truetype("arial.ttf",70)

            draw.text((30,40), name, font=font, fill=(0,0,0))

            thumb = img.copy()
            thumb.thumbnail((250,100))

            tk_img = ImageTk.PhotoImage(thumb)
            self.generated_styles.append(tk_img)

            temp_path = os.path.join(tempfile.gettempdir(),f"sig_style_{i}.png")
            img.save(temp_path)

            btn = tk.Button(
                self.style_container,
                image=tk_img,
                command=lambda p=temp_path:self.set_signature(p),
                relief="raised",
                borderwidth=2
            )

            btn.grid(row=0,column=i,padx=15,pady=5)

        self.status_var.set("Select a signature style.")

    def set_signature(self,path):

        permanent=os.path.join(os.getcwd(),"selected_signature.png")

        Image.open(path).save(permanent)

        self.signature_path.set(permanent)

        self.save_config()

        messagebox.showinfo("Signature Selected","Template selected successfully.")

    # -------------------------------------------------
    # FILE SELECT
    # -------------------------------------------------

    def select_file(self):

        path=filedialog.askopenfilename(
            filetypes=[("PDF / Word","*.pdf *.docx")]
        )

        if not path:
            return

        self.original_filename=os.path.basename(path)

        if path.endswith(".docx"):

            temp_pdf=os.path.join(tempfile.gettempdir(),"temp_convert.pdf")

            self.status_var.set("Converting Word → PDF...")

            docx2pdf.convert(path,temp_pdf)

            self.pdf_path.set(temp_pdf)

            self.load_page_previews(temp_pdf)

        else:

            self.pdf_path.set(path)

            self.load_page_previews(path)

    # -------------------------------------------------
    # PDF PREVIEW
    # -------------------------------------------------

    def load_page_previews(self,pdf_path):

        for widget in self.preview_frame.winfo_children():
            widget.destroy()

        self.page_vars.clear()
        self.page_images.clear()

        doc=fitz.open(pdf_path)

        for i in range(len(doc)):

            page=doc.load_page(i)

            pix=page.get_pixmap(dpi=120)

            img=Image.frombytes("RGB",[pix.width,pix.height],pix.samples)

            img.thumbnail((150,180))

            tk_img=ImageTk.PhotoImage(img)

            self.page_images.append(tk_img)

            var=tk.BooleanVar(value=True)
            self.page_vars.append(var)

            frame=ttk.Frame(self.preview_frame,padding=5)

            chk=ttk.Checkbutton(frame,text=f"Page {i+1}",variable=var,compound=tk.TOP)

            lbl=ttk.Label(frame,image=tk_img)

            chk.pack()
            lbl.pack()

            frame.grid(row=i//5,column=i%5,padx=10,pady=10)

        doc.close()

        self.status_var.set(f"{len(self.page_vars)} pages loaded.")

    # -------------------------------------------------
    # SIGNING (UPDATED WITH HASH + RSA + QR)
    # -------------------------------------------------

    def start_signing(self):

        pdf=self.pdf_path.get()
        sig_template=self.signature_path.get()

        if not pdf:
            messagebox.showerror("Error","Please select a PDF or Word file first.")
            return

        if not sig_template:
            messagebox.showerror("Error","Please generate and select a signature template.")
            return

        pages=[i for i,var in enumerate(self.page_vars) if var.get()]

        if not pages:
            messagebox.showwarning("No Pages","Please select at least one page.")
            return

        # ---------- HASH PDF ----------
        sha=hashlib.sha256()
        with open(pdf,"rb") as f:
            sha.update(f.read())
        pdf_hash=sha.hexdigest()

        # ---------- RSA SIGN ----------
        try:
            with open("keys/private_key.pem","rb") as f:
                private_key=serialization.load_pem_private_key(
                    f.read(),
                    password=None
                )

            signature=private_key.sign(
                bytes.fromhex(pdf_hash),
                padding.PKCS1v15(),
                hashes.SHA256()
            )

        except:
            signature=b"NO_PRIVATE_KEY"

        # ---------- QR GENERATION ----------
        qr_data={
            "signer":self.user_name.get(),
            "hash":pdf_hash
        }

        qr_path=os.path.join(tempfile.gettempdir(),"verify_qr.png")

        qr=qrcode.make(json.dumps(qr_data))
        qr.save(qr_path)

        # ---------- SIGNATURE IMAGE ----------
        now=datetime.now().astimezone()

        name_line=self.user_name.get()
        date_line=now.strftime("Date: %Y.%m.%d")

        tz=now.strftime("%z")
        time_line=f"Time: {now.strftime('%H:%M:%S')} {tz[:-2]}:{tz[-2:]}"

        base_image=Image.open(sig_template).convert("RGBA")
        draw=ImageDraw.Draw(base_image)

        font=ImageFont.load_default()

        img_w,img_h=base_image.size

        draw.text((10,img_h-70),name_line,font=font,fill=(0,0,0))
        draw.text((10,img_h-45),date_line,font=font,fill=(0,0,0))
        draw.text((10,img_h-20),time_line,font=font,fill=(0,0,0))

        qr_img=Image.open(qr_path).resize((60,60))
        base_image.paste(qr_img,(img_w-70,img_h-70))

        temp_img=tempfile.NamedTemporaryFile(suffix=".png",delete=False)
        base_image.save(temp_img.name)

        # ---------- INSERT INTO PDF ----------
        doc=fitz.open(pdf)

        for page_index in pages:

            page=doc.load_page(page_index)
            rect=page.rect

            w=180
            h=w*(base_image.height/base_image.width)

            x1=rect.width-20
            x0=x1-w

            y1=rect.height-10
            y0=y1-h

            box=fitz.Rect(x0,y0,x1,y1)

            page.insert_image(box,filename=temp_img.name)

        # ---------- SAVE ----------
        desktop=os.path.join(os.path.expanduser("~"),"Desktop")
        out_dir=os.path.join(desktop,"Signed Documents")

        os.makedirs(out_dir,exist_ok=True)

        base,_=os.path.splitext(self.original_filename)

        output=os.path.join(out_dir,f"signed_{base}.pdf")

        doc.set_metadata({
                "author": self.user_name.get(),
               "subject": "Digitally Signed Document",
                "keywords": pdf_hash,
               "creator": "PDFSignerApp",
                "producer": "Python Secure PDF Signer"
        })

        doc.save(output)
        doc.close()

        os.remove(temp_img.name)

        messagebox.showinfo("Success",f"Saved to:\n{output}")

        self.status_var.set("Signing complete")


if __name__=="__main__":

    root=tk.Tk()
    app=PDFSignerApp(root)
    root.mainloop()