import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

# ----------------------------------------------------
# آف لائن AI امیج جنریٹر - حصہ 1 (GUI ڈھانچہ)
# ----------------------------------------------------

APP_TITLE = "Offline AI Image Generator (Fujitsu C710 Edition)"
# ڈیفالٹ ماڈل فولڈر کا راستہ
DEFAULT_MODEL_PATH = os.path.join(
    os.getcwd(), "models", "sdxs-512-dreamshaper-openvino"
)


class OfflineAIGeneratorApp:

  def __init__(self, root):
    self.root = root
    self.root.title(APP_TITLE)
    self.root.geometry("750x650")
    self.root.minsize(650, 500)
    self.root.configure(bg="#2c3e50")

    self.generated_image = None
    self.image_path = None

    self._build_ui()

  def _build_ui(self):
    # مین ٹائٹل
    title_lbl = tk.Label(
        self.root,
        text="آف لائن AI امیج جنریٹر",
        font=("Arial", 20, "bold"),
        fg="#ecf0f1",
        bg="#2c3e50",
    )
    title_lbl.pack(pady=10)

    info_lbl = tk.Label(
        self.root,
        text="Core i5 اور 4GB RAM کے لیے 100% آف لائن سافٹ ویئر (حصہ 1)",
        font=("Arial", 10),
        fg="#bdc3c7",
        bg="#2c3e50",
    )
    info_lbl.pack(pady=(0, 10))

    # ماڈل سلیکٹر فریم
    model_frame = tk.Frame(self.root, bg="#2c3e50")
    model_frame.pack(fill="x", padx=20, pady=5)

    model_lbl = tk.Label(
        model_frame,
        text="ماڈل فولڈر:",
        font=("Arial", 10, "bold"),
        fg="#ecf0f1",
        bg="#2c3e50",
    )
    model_lbl.pack(side="left", padx=5)

    self.model_path_entry = tk.Entry(
        model_frame, font=("Arial", 10), bg="#34495e", fg="#ffffff", bd=1
    )
    self.model_path_entry.insert(0, DEFAULT_MODEL_PATH)
    self.model_path_entry.pack(side="left", fill="x", expand=True, padx=5)

    browse_btn = tk.Button(
        model_frame,
        text="تلاش کریں",
        font=("Arial", 9),
        bg="#7f8c8d",
        fg="white",
        command=self.browse_model_folder,
    )
    browse_btn.pack(side="right", padx=5)

    # پرامپٹ ان پٹ بکس
    prompt_lbl = tk.Label(
        self.root,
        text="تصویر کی تفصیل (Prompt) لکھیں:",
        font=("Arial", 11, "bold"),
        fg="#ecf0f1",
        bg="#2c3e50",
    )
    prompt_lbl.pack(anchor="w", padx=20, pady=(10, 0))

    self.prompt_text = tk.Text(
        self.root,
        height=4,
        font=("Arial", 11),
        bg="#34495e",
        fg="#ffffff",
        wrap="word",
    )
    self.prompt_text.pack(fill="x", padx=20, pady=5)
    self.prompt_text.insert(
        "1.0", "A beautiful Pakistani village at sunset, realistic photo, 8k"
    )

    # بٹنز فریم
    btn_frame = tk.Frame(self.root, bg="#2c3e50")
    btn_frame.pack(pady=10)

    self.generate_btn = tk.Button(
        btn_frame,
        text="تصویر بنائیں (Generate)",
        font=("Arial", 11, "bold"),
        bg="#27ae60",
        fg="white",
        padx=15,
        pady=5,
        command=self.start_generation,
    )
    self.generate_btn.pack(side="left", padx=10)

    self.save_btn = tk.Button(
        btn_frame,
        text="تصویر سیو کریں (Save)",
        font=("Arial", 11, "bold"),
        bg="#2980b9",
        fg="white",
        padx=15,
        pady=5,
        state="disabled",
        command=self.save_image,
    )
    self.save_btn.pack(side="left", padx=10)

    # اسٹیٹس بار
    self.status_lbl = tk.Label(
        self.root,
        text="حالت: تیار ہے (آف لائن)",
        font=("Arial", 10),
        fg="#2ecc71",
        bg="#2c3e50",
    )
    self.status_lbl.pack(pady=5)

    # تصویر ڈسپلے باکس
    self.image_canvas = tk.Label(
        self.root,
        text="تصویر بننے کے بعد یہاں ظاہر ہوگی",
        bg="#1a252f",
        fg="#7f8c8d",
        width=60,
        height=15,
    )
    self.image_canvas.pack(fill="both", expand=True, padx=20, pady=10)

  def browse_model_folder(self):
    folder = filedialog.askdirectory(title="AI Model Folder منتخب کریں")
    if folder:
      self.model_path_entry.delete(0, tk.END)
      self.model_path_entry.insert(0, folder)

  def start_generation(self):
    prompt = self.prompt_text.get("1.0", tk.END).strip()
    model_path = self.model_path_entry.get().strip()

    if not prompt:
      messagebox.showwarning("انتباہ", "براہِ کرم تصویر کی تفصیل (Prompt) لکھیں۔")
      return

    if not os.path.exists(model_path):
      messagebox.showwarning(
          "ماڈل فائل نہیں ملی",
          f"ماڈل فولڈر موجود نہیں ہے:\n{model_path}\nبراہِ کرم صحیح فولڈر منتخب کریں۔",
      )
      return

    self.generate_btn.config(state="disabled")
    self.status_lbl.config(
        text="تصویر بنائی جا رہی ہے... (CPU پر آف لائن پروسیسنگ جاری ہے)",
        fg="#f1c40f",
    )

    # بیک گراؤنڈ تھریڈ تاکہ کمپیوٹر ہینگ نہ ہو
    thread = threading.Thread(
        target=self._run_offline_pipeline, args=(prompt, model_path)
    )
    thread.daemon = True
    thread.start()

  def _run_offline_pipeline(self, prompt, model_path):
    # یہ فنکuشن حصہ 2 اور 3 میں مکمل AI ماڈل سے جوڑا جائے گا
    pass

  def save_image(self):
    pass


if __name__ == "__main__":
  root = tk.Tk()
  app = OfflineAIGeneratorApp(root)
  root.mainloop()pillow
openvino
pyinstaller
