import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import urllib.request
import fitz  # PyMuPDF


class LockedSwissKnifeApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Swiss Army Knife (Free Edition)")
    self.root.geometry("950x700")

    self.notebook = ttk.Notebook(root)
    self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Bake tools directly into the closed app (No external plugin loading allowed!)
    self.init_pdf_studio()
    self.init_community_hub()

  def init_pdf_studio(self):
    frame = ttk.Frame(self.notebook, padding=15)
    self.notebook.add(frame, text="📑 PDF Studio")

    ttk.Label(
        frame,
        text="Heavy-Duty Local PDF Workstation",
        font=("Helvetica", 11, "bold"),
    ).pack(anchor="w", pady=(0, 10))

    pdf_file_frame = ttk.Frame(frame)
    pdf_file_frame.pack(fill="x", pady=5)
    ttk.Label(pdf_file_frame, text="PDF File:", width=12).pack(
        side="left", padx=(0, 5)
    )
    pdf_path_var = tk.StringVar()
    ttk.Entry(pdf_file_frame, textvariable=pdf_path_var, width=38).pack(
        side="left", padx=(0, 5), fill="x", expand=True
    )

    def browse_pdf():
      path = filedialog.askopenfilename(
          filetypes=[("PDF Documents", "*.pdf"), ("All Files", "*.*")]
      )
      if path:
        pdf_path_var.set(path)

    ttk.Button(pdf_file_frame, text="Browse...", command=browse_pdf).pack(
        side="left"
    )

    pdf_actions_frame = ttk.LabelFrame(
        frame, text=" PDF Operations ", padding=10
    )
    pdf_actions_frame.pack(fill="x", pady=10)

    pdf_action_var = tk.StringVar(value="extract_images")

    ttk.Radiobutton(
        pdf_actions_frame,
        text="Extract All Embedded Images into Folder",
        variable=pdf_action_var,
        value="extract_images",
    ).pack(anchor="w", pady=3)
    ttk.Radiobutton(
        pdf_actions_frame,
        text="Extract All Text to a .txt File",
        variable=pdf_action_var,
        value="extract_text",
    ).pack(anchor="w", pady=3)
    ttk.Radiobutton(
        pdf_actions_frame,
        text="Get PDF Metadata & Page Count Stats",
        variable=pdf_action_var,
        value="stats",
    ).pack(anchor="w", pady=3)

    pdf_status_var = tk.StringVar(value="Status: Ready")
    ttk.Label(
        frame, textvariable=pdf_status_var, font=("Consolas", 9, "italic")
    ).pack(anchor="w", pady=(10, 5))
    pdf_progress = ttk.Progressbar(
        frame, orient="horizontal", mode="indeterminate"
    )

    def run_pdf_task():
      path = pdf_path_var.get().strip()
      action = pdf_action_var.get()

      if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid PDF file!")
        return

      pdf_progress.pack(fill="x", pady=(0, 10))
      pdf_progress.start(12)
      pdf_status_var.set("Status: Processing PDF locally...")

      def background_pdf():
        try:
          doc = fitz.open(path)
          base_dir = os.path.dirname(path)
          base_name = os.path.splitext(os.path.basename(path))[0]

          if action == "extract_images":
            out_folder = os.path.join(base_dir, f"{base_name}_extracted_images")
            os.makedirs(out_folder, exist_ok=True)
            count = 0
            for i, page in enumerate(doc):
              image_list = page.get_images(full=True)
              for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = os.path.join(
                    out_folder, f"p{i+1}_img{img_index+1}.{image_ext}"
                )
                with open(image_filename, "wb") as f:
                  f.write(image_bytes)
                count += 1
            self.root.after(
                0,
                lambda: finish_pdf(
                    True,
                    f"Successfully extracted {count} images to:\n{out_folder}",
                ),
            )

          elif action == "extract_text":
            out_txt = os.path.join(base_dir, f"{base_name}_text.txt")
            full_text = ""
            for i, page in enumerate(doc):
              full_text += (
                  f"--- Page {i+1} ---\n"
                  + page.get_text()
                  + "\n\n"
              )
            with open(out_txt, "w", encoding="utf-8") as f:
              f.write(full_text)
            self.root.after(
                0,
                lambda: finish_pdf(
                    True, f"Successfully extracted text to:\n{out_txt}"
                ),
            )

          elif action == "stats":
            meta = doc.metadata
            stats_msg = (
                f"File: {os.path.basename(path)}\nPages:"
                f" {len(doc)}\nTitle: {meta.get('title', 'N/A')}\nAuthor:"
                f" {meta.get('author', 'N/A')}\nEncryption:"
                f" {'Encrypted' if doc.is_encrypted else 'None'}"
            )
            self.root.after(0, lambda: finish_pdf(True, stats_msg))

          doc.close()
        except Exception as e:
          self.root.after(
              0, lambda: finish_pdf(False, f"PDF error:\n{str(e)}")
          )

      threading.Thread(target=background_pdf, daemon=True).start()

    def finish_pdf(success, msg):
      pdf_progress.stop()
      pdf_progress.pack_forget()
      if success:
        pdf_status_var.set("Status: Complete!")
        messagebox.showinfo("PDF Studio Success", msg)
      else:
        pdf_status_var.set("Status: Failed.")
        messagebox.showerror("PDF Processing Error", msg)

    ttk.Button(
        frame, text="⚡ RUN PDF OPERATION ⚡", command=run_pdf_task
    ).pack(fill="x", pady=(10, 0))

  def init_community_hub(self):
    frame = ttk.Frame(self.notebook, padding=15)
    self.notebook.add(frame, text="🌐 Creative Foundation & Hub")

    ttk.Label(
        frame,
        text="Central Community Hub — Live Cloud Feed (Free Edition)",
        font=("Helvetica", 11, "bold"),
    ).pack(anchor="w", pady=(0, 10))

    sub_notebook = ttk.Notebook(frame)
    sub_notebook.pack(fill="both", expand=True, pady=5)

    # Tab 1: Studio
    create_tab = ttk.Frame(sub_notebook, padding=10)
    sub_notebook.add(create_tab, text="🎨 My Studio & Library")

    color_frame = ttk.LabelFrame(
        create_tab, text=" My Color Library ", padding=8
    )
    color_frame.pack(fill="x", pady=5)

    palette_display = tk.Listbox(color_frame, height=4, font=("Consolas", 9))
    palette_display.pack(fill="x", pady=5)

    for c in [
        "#1a1c2c (Deep Night)",
        "#b13e53 (Crimson)",
        "#ffcd75 (Warm Gold)",
        "#a7f070 (Mint Green)",
    ]:
      palette_display.insert(tk.END, c)

    add_c_row = ttk.Frame(color_frame)
    add_c_row.pack(fill="x", pady=2)
    hex_var = tk.StringVar(value="#")
    ttk.Entry(add_c_row, textvariable=hex_var, width=10).pack(
        side="left", padx=(0, 5)
    )
    name_var = tk.StringVar()
    ttk.Entry(add_c_row, textvariable=name_var, width=18).pack(
        side="left", padx=(0, 5), fill="x", expand=True
    )

    def add_color():
      h = hex_var.get().strip()
      n = name_var.get().strip()
      if h and h != "#":
        palette_display.insert(tk.END, f"{h} ({n if n else 'Custom'})")
        hex_var.set("#")
        name_var.set("")

    ttk.Button(add_c_row, text="Add Swatch", command=add_color).pack(
        side="left"
    )

    art_frame = ttk.LabelFrame(
        create_tab, text=" Pixel Art Post Creator ", padding=8
    )
    art_frame.pack(fill="both", expand=True, pady=5)

    ttk.Label(art_frame, text="Art Title / Description:").pack(anchor="w")
    title_var = tk.StringVar(value="My Pixel Sprite")
    ttk.Entry(art_frame, textvariable=title_var).pack(fill="x", pady=(0, 5))

    ttk.Label(art_frame, text="Pixel Pattern (ASCII / Text Art):").pack(
        anchor="w"
    )
    art_text = tk.Text(art_frame, height=4, font=("Consolas", 9))
    art_text.pack(fill="both", expand=True, pady=5)
    art_text.insert(
        "1.0", "  @@@@  \n @    @ \n @ @@ @ \n @    @ \n  @@@@  \n"
    )

    status_lbl = tk.StringVar(value="Status: Ready to publish to cloud")
    ttk.Label(
        create_tab, textvariable=status_lbl, font=("Consolas", 9, "italic")
    ).pack(anchor="w", pady=5)

    storage_file = "community_cloud_cache.json"

    def publish_to_cloud():
      try:
        status_lbl.set("Status: Pushing to cloud network...")
        posts = []
        if os.path.exists(storage_file):
          with open(storage_file, "r", encoding="utf-8") as f:
            posts = json.load(f)

        new_post = {
            "creator": "Taco (Free User)",
            "title": title_var.get().strip(),
            "pixel_art": art_text.get("1.0", tk.END).strip(),
            "color_library": list(palette_display.get(0, tk.END)),
        }
        posts.insert(0, new_post)

        with open(storage_file, "w", encoding="utf-8") as f:
          json.dump(posts, f, indent=4)

        status_lbl.set("Status: Successfully published to live feed!")
        messagebox.showinfo(
            "Success!", "Your pixel art and color library are live!"
        )
      except Exception as e:
        status_lbl.set("Status: Error.")
        messagebox.showerror("Cloud Error", str(e))

    ttk.Button(
        create_tab,
        text="☁️ PUBLISH LIVE TO CLOUD FEED ☁️",
        command=publish_to_cloud,
    ).pack(fill="x", pady=5)

    # Tab 2: Feed
    feed_tab = ttk.Frame(sub_notebook, padding=10)
    sub_notebook.add(feed_tab, text="🌍 Live Community Feed")

    ttk.Label(
        feed_tab, text="Pulling real-time posts from the cloud feed:"
    ).pack(anchor="w", pady=(0, 5))

    feed_display = tk.Text(
        feed_tab,
        wrap="word",
        font=("Consolas", 10),
        state="disabled",
        background="#f4f4f4",
    )
    feed_display.pack(fill="both", expand=True, pady=5)

    def refresh_feed():
      try:
        posts = []
        if os.path.exists(storage_file):
          with open(storage_file, "r", encoding="utf-8") as f:
            posts = json.load(f)

        feed_display.config(state="normal")
        feed_display.delete("1.0", tk.END)

        if not posts:
          feed_display.insert("1.0", "No cloud posts found yet.")
        else:
          feed_text = (
              "========================================\n🌍 LIVE CLOUD"
              " COMMUNITY FEED\n========================================\n\n"
          )
          for p in posts:
            feed_text += f"👤 Creator: {p.get('creator', 'Unknown')}\n"
            feed_text += f"🎨 Title: {p.get('title', 'Untitled')}\n"
            feed_text += "--- Pixel Art ---\n"
            feed_text += f"{p.get('pixel_art', '')}\n\n"
            feed_text += "--- Color Swatches ---\n"
            for sw in p.get("color_library", []):
              feed_text += f"• {sw}\n"
            feed_text += (
                "\n----------------------------------------\n\n"
            )

          feed_display.insert("1.0", feed_text)
        feed_display.config(state="disabled")
      except Exception as e:
        messagebox.showerror("Feed Error", str(e))

    ttk.Button(
        feed_tab, text="🔄 Refresh Live Cloud Feed", command=refresh_feed
    ).pack(fill="x", pady=5)


if __name__ == "__main__":
  root = tk.Tk()
  app = LockedSwissKnifeApp(root)
  root.mainloop()