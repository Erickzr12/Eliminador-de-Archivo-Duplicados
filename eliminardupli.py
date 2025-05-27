# Eliminador de Fotos Duplicadas Profesional con Funciones Avanzadas
# Autor: Erick Manuel Zapata Reque
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import hashlib
import shutil
import threading
from PIL import Image, ImageTk
import datetime
import smtplib
from email.message import EmailMessage
import schedule
import time
import pystray
from pystray import MenuItem as item
from PIL import Image as PILImage
import subprocess  # Para abrir videos con el reproductor predeterminado (nuevo)

# --- Configuración ---
config = {
    "backup_folder": "./RespaldoDuplicados",
    "password": "123",
    "email": "kakuzoxd123@gmail.com",
    "email_password": "biev zuqh rrdc mrui",
    "recipient_email": "erick.zapatar12@gmail.com"
}

# Temas predefinidos para la interfaz
themes = {
    "Oscuro": {
        "background": "#1e1e1e",
        "foreground": "white",
        "tree_bg": "#2e2e2e",
        "tree_fg": "white",
        "button_bg": "#444",
        "button_fg": "white",
        "highlight": "#3e3e3e",
    },
    "Claro": {
        "background": "white",
        "foreground": "black",
        "tree_bg": "white",
        "tree_fg": "black",
        "button_bg": "#e0e0e0",
        "button_fg": "black",
        "highlight": "#cccccc",
    },
    "Azul Profesional": {
        "background": "#0b3d91",
        "foreground": "white",
        "tree_bg": "#105cb6",
        "tree_fg": "white",
        "button_bg": "#074a8c",
        "button_fg": "white",
        "highlight": "#133e75",
    }
}

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔎 Eliminador de Fotos Duplicadas Profesional - Erick Manuel Zapata Reque")
        self.root.geometry("950x650")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.duplicates = []
        self.current_folder = ""

        self.setup_ui()

        # Aplicar tema inicial (Oscuro)
        self.apply_theme("Oscuro") 

        
    def setup_ui(self):
        top_frame = ttk.LabelFrame(self.root, text="Seleccionar Carpeta")
        top_frame.pack(fill="x", padx=15, pady=10)

        self.folder_label = ttk.Label(top_frame, text="Carpeta actual: Ninguna")
        self.folder_label.pack(side="left", padx=10, pady=5)

        self.btn_select = ttk.Button(top_frame, text="📁 Elegir Carpeta", command=self.select_folder)
        self.btn_select.pack(side="right", padx=10)

        # Selector de tema
        self.theme_var = tk.StringVar(value="Oscuro")
        theme_label = ttk.Label(top_frame, text="Tema:")
        theme_label.pack(side="left", padx=(10, 0))
        self.theme_combo = ttk.Combobox(top_frame, values=list(themes.keys()), textvariable=self.theme_var, state="readonly", width=18)
        self.theme_combo.pack(side="left", padx=5)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)

        ttk.Separator(self.root).pack(fill="x", padx=10, pady=5)

        self.tree = ttk.Treeview(self.root, columns=("Archivo", "Tamaño"), show="headings", height=18)
        self.tree.heading("Archivo", text="Ruta del Archivo")
        self.tree.heading("Tamaño", text="Tamaño (KB)")
        self.tree.column("Archivo", width=700)
        self.tree.column("Tamaño", width=100, anchor="center")
        self.tree.pack(padx=15, pady=10, fill="both", expand=True)

        ttk.Separator(self.root).pack(fill="x", padx=10, pady=5)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        self.btn_buscar = ttk.Button(button_frame, text="🔍 Buscar Duplicados", command=self.start_scan)
        self.btn_buscar.grid(row=0, column=0, padx=10)

        self.btn_ver = ttk.Button(button_frame, text="🖼️ Ver Imagen", command=self.view_image)
        self.btn_ver.grid(row=0, column=1, padx=10)

        self.btn_eliminar = ttk.Button(button_frame, text="🗑️ Eliminar Seleccionados", command=self.confirm_delete)
        self.btn_eliminar.grid(row=0, column=2, padx=10)

        # Nuevos botones profesionales
        self.btn_ver_video = ttk.Button(button_frame, text="▶️ Ver Video", command=self.view_video)
        self.btn_ver_video.grid(row=0, column=3, padx=10)

        self.btn_crear_carpeta = ttk.Button(button_frame, text="📂 Crear Carpeta Respaldo", command=self.create_backup_folder)
        self.btn_crear_carpeta.grid(row=0, column=4, padx=10)

        self.btn_seleccionar_todo = ttk.Button(button_frame, text="✅ Seleccionar Todo", command=self.select_all)
        self.btn_seleccionar_todo.grid(row=0, column=5, padx=10)

        self.btn_deseleccionar = ttk.Button(button_frame, text="❌ Deseleccionar Todo", command=self.deselect_all)
        self.btn_deseleccionar.grid(row=0, column=6, padx=10)


        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=20, pady=5)

        self.status_label = ttk.Label(self.root, text="Estado: Esperando acción del usuario")
        self.status_label.pack(pady=5)
    

    def select_all(self):
        for item in self.tree.get_children():
            self.tree.selection_add(item)

    def deselect_all(self):
        self.tree.selection_remove(self.tree.selection())

    def apply_theme(self, theme_name):
        theme = themes.get(theme_name)
        if not theme:
            return
        self.root.configure(bg=theme["background"])
        self.style.configure("TFrame", background=theme["background"])
        self.style.configure("TLabel", background=theme["background"], foreground=theme["foreground"])
        self.style.configure("TButton", background=theme["button_bg"], foreground=theme["button_fg"])
        self.style.configure("Treeview", background=theme["tree_bg"], foreground=theme["tree_fg"], fieldbackground=theme["tree_bg"])
        self.style.configure("Treeview.Heading", background=theme["highlight"], foreground=theme["foreground"])

        # Cambiar colores específicos de widgets que no actualizan automáticamente
        self.folder_label.configure(background=theme["background"], foreground=theme["foreground"])
        self.status_label.configure(background=theme["background"], foreground=theme["foreground"])

        # Cambiar fondo y texto del LabelFrame
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                widget.configure(style="TFrame")

    def on_theme_change(self, event):
        selected_theme = self.theme_var.get()
        self.apply_theme(selected_theme)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.current_folder = path
            self.folder_label.config(text=f"Carpeta actual: {path}")

    def start_scan(self):
        if not self.current_folder:
            messagebox.showwarning("Advertencia", "Seleccione una carpeta primero.")
            return
        threading.Thread(target=self.scan_duplicates).start()

    def scan_duplicates(self):
        self.status_label.config(text="Buscando duplicados...")
        self.tree.delete(*self.tree.get_children())
        self.duplicates.clear()
        hashes = {}

        total_files = sum(len(files) for _, _, files in os.walk(self.current_folder))
        self.progress["maximum"] = total_files
        progress_count = 0

        for root, _, files in os.walk(self.current_folder):
            for file in files:
                try:
                    path = os.path.join(root, file)
                    with open(path, 'rb') as f:
                        filehash = hashlib.md5(f.read()).hexdigest()
                    size_kb = os.path.getsize(path) // 1024
                    if filehash in hashes:
                        self.duplicates.append((path, size_kb))
                        self.tree.insert('', 'end', values=(path, size_kb))
                    else:
                        hashes[filehash] = path
                except:
                    continue
                progress_count += 1
                self.progress["value"] = progress_count

        self.status_label.config(text=f"Duplicados encontrados: {len(self.duplicates)}")
        self.send_email_report()
        self.show_notification("Escaneo completo", f"Duplicados encontrados: {len(self.duplicates)}")

    def view_image(self):
        selected = self.tree.selection()
        if selected:
            path = self.tree.item(selected[0])['values'][0]
            try:
                img = Image.open(path)
                img.show()
            except:
                messagebox.showerror("Error", "No se pudo abrir la imagen.")

    # Nuevo método para abrir video con reproductor predeterminado
    def view_video(self):
        selected = self.tree.selection()
        if selected:
            path = self.tree.item(selected[0])['values'][0]
            if os.path.isfile(path) and path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(path)
                    elif os.name == 'posix':  # MacOS o Linux
                        subprocess.run(['xdg-open', path], check=False)
                    else:
                        messagebox.showinfo("Info", "No se soporta abrir videos en esta plataforma.")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo abrir el video: {e}")
            else:
                messagebox.showwarning("Advertencia", "Seleccione un archivo de video válido.")

    # Nuevo método para crear carpeta respaldo manualmente
    def create_backup_folder(self):
        try:
            os.makedirs(config["backup_folder"], exist_ok=True)
            messagebox.showinfo("Éxito", f"Carpeta de respaldo creada o ya existente en:\n{config['backup_folder']}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta de respaldo:\n{e}")

    def confirm_delete(self):
        if not self.authenticate():
            return
        if messagebox.askyesno("Confirmación", "¿Desea eliminar los duplicados seleccionados?"):
            for item in self.tree.selection():
                path = self.tree.item(item)['values'][0]
                self.backup_file(path)
                try:
                    os.remove(path)
                except:
                    continue
                self.tree.delete(item)
            messagebox.showinfo("Éxito", "Archivos eliminados y respaldados.")

    def backup_file(self, path):
        os.makedirs(config["backup_folder"], exist_ok=True)
        shutil.copy(path, config["backup_folder"])

    def authenticate(self):
        password = simpledialog.askstring("contraseña", "Ingrese la contraseña de seguridad:", show="*")
        return password == config["password"]

    def show_notification(self, title, message):
        icon = PILImage.new('RGB', (64, 64), color='black')
        tray_icon = pystray.Icon("notifier", icon, title, menu=pystray.Menu(item(message, lambda: None)))
        threading.Thread(target=tray_icon.run).start()
        threading.Timer(4, tray_icon.stop).start()

    def send_email_report(self):
        msg = EmailMessage()
        msg['Subject'] = "📄 Reporte de Escaneo de Duplicados"
        msg['From'] = config['email']
        msg['To'] = config['recipient_email']
        msg.set_content(
            f"📁 Carpeta escaneada: {self.current_folder}\n"
            f"🔎 Duplicados encontrados: {len(self.duplicates)}\n"
            f"🕒 Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            "Este es un reporte automático generado por la herramienta profesional de detección de duplicados."
        )

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(config['email'], config['email_password'])
                smtp.send_message(msg)
        except Exception as e:
            print("Error al enviar email:", e)


def programar_escaneo(app):
    schedule.every().day.at("10:00").do(app.start_scan)

    def ejecutar():
        while True:
            schedule.run_pending
            time.sleep(60)

    threading.Thread(target=ejecutar, daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    programar_escaneo(app)
    root.mainloop()