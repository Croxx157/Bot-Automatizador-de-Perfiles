import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import threading

from principal import ejecutar_automatizacion  # Importa la función principal

perfiles_usados_path = os.path.expanduser("~/perfiles_usados.json")
excel_path = None

# Configuración global
config_path = os.path.join(os.path.dirname(__file__), "config.json")
default_chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

def cargar_config():
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"chrome_path": default_chrome_path}

def guardar_config(config):
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

config = cargar_config()

def seleccionar_excel():
    global excel_path
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    if archivo:
        excel_path = archivo
        lbl_archivo.config(text=f"Seleccionado: {os.path.basename(excel_path)}", fg="white")
    else:
        lbl_archivo.config(text="No se ha seleccionado ningún archivo", fg="yellow")

def configurar_chrome():
    ruta = filedialog.askopenfilename(
        title="Seleccionar ejecutable de Chrome",
        filetypes=[("Chrome", "chrome.exe")]
    )
    if ruta and os.path.exists(ruta):
        config["chrome_path"] = ruta
        guardar_config(config)
        messagebox.showinfo("Configuración", f"Ruta de Chrome actualizada:\n{ruta}")
    else:
        messagebox.showerror("Error", "Ruta inválida. Selecciona el ejecutable correcto.")

def iniciar():
    global excel_path
    if not excel_path:
        messagebox.showwarning("Advertencia", "Debe seleccionar un archivo Excel antes de iniciar.")
        return
    if not os.path.exists(config.get("chrome_path", "")):
        messagebox.showerror("Error", "La ruta de Chrome no es válida. Configúrala desde el botón 'Configuración'.")
        return
    # Ejecuta la automatización en un hilo para no bloquear la interfaz
    threading.Thread(target=ejecutar_automatizacion, args=(excel_path, config["chrome_path"]), daemon=True).start()

def mostrar_historicos():
    if not os.path.exists(perfiles_usados_path):
        messagebox.showinfo("Históricos", "No hay registros todavía.")
        return
    
    try:
        with open(perfiles_usados_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not data:
            messagebox.showinfo("Históricos", "No hay registros todavía.")
            return
        
        hist_ventana = tk.Toplevel()
        hist_ventana.title("Históricos de Perfiles")
        hist_ventana.geometry("500x350")
        hist_ventana.configure(bg="#0B3D91")

        lbl_titulo_hist = tk.Label(
            hist_ventana,
            text="Históricos de Perfiles Usados",
            font=("Arial", 16, "bold"),
            bg="#0B3D91",
            fg="white"
        )
        lbl_titulo_hist.pack(pady=15)

        frame_lista = tk.Frame(hist_ventana, bg="#0B3D91")
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        lista = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=("Arial", 12),
            bg="white",
            fg="black",
            selectbackground="#0B3D91",
            selectforeground="white"
        )

        for idx, perfil in enumerate(data, start=1):
            lista.insert(tk.END, f"{idx}. {perfil}")

        lista.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=lista.yview)

        btn_cerrar_hist = tk.Button(
            hist_ventana,
            text="Cerrar",
            font=("Arial", 12, "bold"),
            bg="red",
            fg="white",
            command=hist_ventana.destroy
        )
        btn_cerrar_hist.pack(pady=10)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo de históricos:\n{e}")

def borrar_historicos():
    if not os.path.exists(perfiles_usados_path):
        messagebox.showinfo("Históricos", "No hay registros para borrar.")
        return
    
    confirmar = messagebox.askyesno(
        "Confirmar borrado",
        "⚠ Esta acción borrará TODOS los registros del historial.\n¿Seguro que quieres continuar?"
    )
    
    if confirmar:
        try:
            with open(perfiles_usados_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Borrado exitoso", "El historial ha sido borrado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo borrar el historial:\n{e}")

def ventana_configuracion():
    config_win = tk.Toplevel()
    config_win.title("Configuración de Chrome")
    config_win.geometry("700x400")  # Más ancho y largo
    config_win.configure(bg="#0B3D91")
    config_win.resizable(False, False)

    lbl_info = tk.Label(
        config_win,
        text="Selecciona el ejecutable de Chrome en tu equipo.\nLa ruta actual se muestra abajo.",
        font=("Arial", 14),
        bg="#0B3D91",
        fg="white"
    )
    lbl_info.pack(pady=20)

    ruta_actual = tk.StringVar(value=config.get("chrome_path", default_chrome_path))
    lbl_ruta = tk.Label(
        config_win,
        textvariable=ruta_actual,
        font=("Arial", 12),
        bg="#0B3D91",
        fg="yellow",
        width=70,  # Más ancho
        height=3   # Más alto
    )
    lbl_ruta.pack(pady=15)

    def cambiar_ruta():
        ruta = filedialog.askopenfilename(
            title="Seleccionar ejecutable de Chrome",
            filetypes=[("Chrome", "chrome.exe")]
        )
        if ruta and os.path.exists(ruta):
            config["chrome_path"] = ruta
            guardar_config(config)
            ruta_actual.set(ruta)
            messagebox.showinfo("Configuración", f"Ruta de Chrome actualizada:\n{ruta}")
        else:
            messagebox.showerror("Error", "Ruta inválida. Selecciona el ejecutable correcto.")

    btn_cambiar = tk.Button(
        config_win,
        text="Cambiar ruta de Chrome",
        font=("Arial", 12, "bold"),
        bg="#0074D9",
        fg="white",
        command=cambiar_ruta
    )
    btn_cambiar.pack(pady=10)

    btn_cerrar = tk.Button(
        config_win,
        text="Cerrar",
        font=("Arial", 12, "bold"),
        bg="red",
        fg="white",
        command=config_win.destroy
    )
    btn_cerrar.pack(pady=10)

# Ventana principal
ventana = tk.Tk()
ventana.title("Automatizador de Perfiles")
ventana.geometry("900x550")
ventana.configure(bg="#0B3D91")
ventana.resizable(False, False)  # Ventana fija

lbl_titulo = tk.Label(ventana, text="Automatizador de Perfiles", font=("Arial", 16, "bold"), bg="#0B3D91", fg="white")
lbl_titulo.pack(pady=20)

btn_excel = tk.Button(ventana, text="Seleccionar Archivo Excel", font=("Arial", 12), command=seleccionar_excel)
btn_excel.pack(pady=10)

lbl_archivo = tk.Label(ventana, text="No se ha seleccionado ningún archivo", font=("Arial", 10), bg="#0B3D91", fg="yellow")
lbl_archivo.pack(pady=5)

btn_iniciar = tk.Button(ventana, text="INICIAR", font=("Arial", 12, "bold"), bg="green", fg="white", command=iniciar)
btn_iniciar.place(relx=0.85, rely=0.85, anchor="center")

btn_salir = tk.Button(ventana, text="SALIR", font=("Arial", 12, "bold"), bg="red", fg="white", command=ventana.quit)
btn_salir.place(relx=0.15, rely=0.85, anchor="center")

btn_historicos = tk.Button(ventana, text="Históricos", font=("Arial", 12, "bold"), bg="orange", fg="white", command=mostrar_historicos)
btn_historicos.place(relx=0.35, rely=0.85, anchor="center")

btn_borrar_hist = tk.Button(ventana, text="Borrar Históricos", font=("Arial", 12, "bold"), bg="purple", fg="white", command=borrar_historicos)
btn_borrar_hist.place(relx=0.60, rely=0.85, anchor="center")

btn_config = tk.Button(
    ventana,
    text="Configuración",
    font=("Arial", 12, "bold"),
    bg="#0074D9",
    fg="white",
    command=ventana_configuracion
)
btn_config.place(x=10, y=10)  # Arriba a la izquierda

ventana.mainloop()
