import pyautogui
import pandas as pd
import time
import os
import subprocess
import sys
import json
from pynput import keyboard

def buscar_carpeta_imagenes():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(base_dir):
        if "imagenes" in dirs:
            return os.path.join(root, "imagenes")
    print("❌ No se encontró la carpeta 'imagenes'.")
    sys.exit(1)

def ejecutar_automatizacion(excel_path, chrome_path=None):
    global stop_program
    stop_program = False

    if chrome_path is None:
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    if not os.path.exists(chrome_path):
        print(f"❌ Ruta de Chrome no encontrada: {chrome_path}")
        sys.exit(1)

    imagenes_path = buscar_carpeta_imagenes()
    url_final = "https://www.facebook.com"
    perfiles_usados_path = os.path.expanduser("~/perfiles_usados.json")  # Guardar en carpeta usuario

    pyautogui.FAILSAFE = True

    # Función para manejar ESC
    def on_press(key):
        global stop_program
        try:
            if key == keyboard.Key.esc:
                stop_program = True
                print("\n🚨 Proceso detenido por el usuario (ESC presionado).")
                return False
        except:
            pass

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # --- JSON helpers ---
    def guardar_perfil_usado(nombre_perfil):
        perfiles = cargar_perfiles_usados()
        if nombre_perfil not in perfiles:
            perfiles.append(nombre_perfil)
            with open(perfiles_usados_path, "w", encoding="utf-8") as f:
                json.dump(perfiles, f, ensure_ascii=False, indent=4)
        print(f"✅ Perfil '{nombre_perfil}' guardado en {perfiles_usados_path}")

    def cargar_perfiles_usados():
        if not os.path.exists(perfiles_usados_path):
            return []
        with open(perfiles_usados_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return []

    # --- Nueva función para asegurar que la ventana esté maximizada ---
    def asegurar_maximizado():
        pyautogui.hotkey("win", "up")
        time.sleep(0.3)

    # Leer Excel
    df = pd.read_excel(excel_path)
    perfiles_usados = set(cargar_perfiles_usados())
    print(f"📂 {len(perfiles_usados)} perfiles ya registrados previamente.")

    # --- Funciones de automatización ---
    def scroll_abajo_max():
        ancho, alto = pyautogui.size()
        pyautogui.moveTo(ancho // 2, alto // 2, duration=0.3)
        time.sleep(0.2)
        for _ in range(20):
            if stop_program: return
            pyautogui.scroll(-500)
            time.sleep(0.15)

    def click_imagen(nombre_imagen, descripcion="", tiempo_espera=1, scroll_before_search=False, max_tries=40, scroll_step=1):
        if stop_program: return False
        ruta_imagen = os.path.join(imagenes_path, nombre_imagen)
        tries = 0
        while tries < max_tries and not stop_program:
            tries += 1
            try:
                location = pyautogui.locateCenterOnScreen(ruta_imagen, confidence=0.8)
            except Exception:
                location = None
            if location:
                pyautogui.click(location)
                time.sleep(tiempo_espera)
                return True
            else:
                if scroll_before_search and (tries % scroll_step == 0):
                    ancho, alto = pyautogui.size()
                    pyautogui.moveTo(ancho // 2, alto // 2, duration=0.2)
                    pyautogui.scroll(-300)
                    time.sleep(0.25)
                time.sleep(0.15)
        return False

    def cerrar_chrome_click(offset_x=10, offset_y=10):
        ancho, alto = pyautogui.size()
        x = ancho - offset_x
        y = offset_y
        pyautogui.moveTo(x, y, duration=0.25)
        time.sleep(0.15)
        pyautogui.click()
        time.sleep(0.5)
        pyautogui.moveTo(ancho // 2, alto // 2, duration=0.2)
        time.sleep(0.5)

    # --- Programa principal ---
    for _, row in df.iterrows():
        if stop_program:
            break

        perfil = str(row["perfil"]).strip()

        if perfil in perfiles_usados:
            print(f"⏩ Perfil '{perfil}' ya fue registrado antes. Saltando...")
            continue

        subprocess.Popen([chrome_path, "--new-window"])
        time.sleep(2)
        pyautogui.hotkey("win", "up")  # Asegura que se abra maximizado desde el inicio
        time.sleep(0.5)

        exito = False
        try:
            scroll_abajo_max()
            if stop_program: break

            if not click_imagen("agregar.png", "Botón agregar", 2, scroll_before_search=True, max_tries=50, scroll_step=2):
                continue
            if stop_program: break

            click_imagen("continuar_sin_cuenta.png", "Continuar sin cuenta", 2, scroll_before_search=True, max_tries=30, scroll_step=2)
            if stop_program: break

            if click_imagen("nombre.png", "Barra para añadir nombre", 1):
                pyautogui.typewrite(perfil)
                time.sleep(1)
            else:
                continue
            if stop_program: break

            if not click_imagen("hecho.png", "Botón Hecho", 1, max_tries=20):
                print("⚠ No se encontró el botón 'Hecho'. Intentando continuar...")

            pyautogui.hotkey("ctrl", "l")
            pyautogui.typewrite(url_final)
            pyautogui.press("enter")
            time.sleep(3)
            if stop_program: break

            exito = True

        finally:
            asegurar_maximizado()
            cerrar_chrome_click(offset_x=10, offset_y=10)
            time.sleep(2)
            if exito and not stop_program:
                guardar_perfil_usado(perfil)
                perfiles_usados.add(perfil)

    if stop_program:
        from tkinter import messagebox
        messagebox.showinfo("Proceso detenido", "🚨 Proceso detenido por el usuario.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ No se recibió el archivo Excel. Ejecútalo desde la interfaz o pasando la ruta.")
        sys.exit(1)
    ejecutar_automatizacion(sys.argv[1])
