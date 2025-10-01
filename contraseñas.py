#!/usr/bin/env python3
# creador_contras_gui_50_validado.py
# GUI Tkinter: genera 50 contraseñas (8 chars) a partir de Nombre, Mascota, DNI.
# Validaciones:
#  - Nombre: solo letras y espacios (incluye acentos y ñ)
#  - DNI: máximo 9 caracteres y debe ser exactamente 9 para generar

import random
import re
import secrets
import string
import tkinter as tk
from tkinter import messagebox

# --- Config ---
SYMBOLS = "!@#$%&*"
LEET_MAP = {
    'a': ['@', '4'],
    'e': ['3'],
    'i': ['1', '!'],
    'o': ['0'],
    's': ['$', '5'],
    't': ['7']
}
TOTAL_TO_GENERATE = 50
PW_LENGTH = 8

# --- Utilidades de generación ---
def leet_transform(word, intensity=0.45):
    out = []
    for ch in word:
        low = ch.lower()
        if low in LEET_MAP and secrets.randbelow(100) < int(100 * intensity):
            out.append(secrets.choice(LEET_MAP[low]))
        else:
            out.append(ch)
    return ''.join(out)

def random_case_mix(word):
    return ''.join(ch.upper() if secrets.choice([True, False]) else ch.lower() for ch in word)

def insert_random_digits_symbols(s, n=3):
    charset = string.digits + SYMBOLS
    for _ in range(n):
        pos = secrets.randbelow(len(s) + 1)
        s = s[:pos] + secrets.choice(charset) + s[pos:]
    return s

def shuffle_and_trim(s, length=PW_LENGTH):
    lst = list(s)
    random.shuffle(lst)
    out = ''.join(lst)[:length]
    while len(out) < length:
        out += secrets.choice(string.ascii_letters + string.digits + SYMBOLS)
    return out

def generate_passwords_from_inputs(name, pet, dni, count=TOTAL_TO_GENERATE, length=PW_LENGTH):
    name = (name or "").strip()
    pet = (pet or "").strip()
    dni = (dni or "").strip()
    raw_bases = []
    if name: raw_bases.append(name)
    if pet: raw_bases.append(pet)
    if dni: raw_bases.append(dni)
    if name and pet: raw_bases.append(name + pet)
    if pet and dni: raw_bases.append(pet + dni)
    if name and dni: raw_bases.append(name + dni)
    for w in list(raw_bases):
        raw_bases.append(w[::-1])
        raw_bases.append(random_case_mix(w))
        raw_bases.append(leet_transform(w))
    bases = list(dict.fromkeys([b for b in raw_bases if b]))
    results = []
    tries = 0
    max_tries = count * 60
    while len(results) < count and tries < max_tries:
        tries += 1
        k = secrets.choice([1,2,3])
        parts = [secrets.choice(bases) for _ in range(k)] if bases else ['']
        for i in range(len(parts)):
            r = secrets.randbelow(100)
            if r < 30:
                parts[i] = leet_transform(parts[i])
            elif r < 60:
                parts[i] = random_case_mix(parts[i])
        candidate = ''.join(parts)
        if secrets.randbelow(100) < 75:
            candidate = insert_random_digits_symbols(candidate, n=3)
        pw = shuffle_and_trim(candidate, length=length)
        if pw not in results:
            results.append(pw)
    alphabet = string.ascii_letters + string.digits + SYMBOLS
    while len(results) < count:
        pw = ''.join(secrets.choice(alphabet) for _ in range(length))
        if pw not in results:
            results.append(pw)
    return results

# --- Validaciones para entradas ---
def is_name_valid(s: str) -> bool:
    # Acepta letras (incluye acentos y ñ) y espacios. Rechaza vacío.
    if not s or not s.strip():
        return False
    # comprobar caracter por caracter usando .isalpha() o espacio
    for ch in s:
        if ch.isspace():  # Usar isspace() en lugar de comparar con ' '
            continue
        if not ch.isalpha():   # isalpha acepta letras acentuadas y ñ
            return False
    return True

def is_dni_valid(s: str) -> bool:
    # DNI: longitud exacta 9 para aceptar (pero permitimos letras y dígitos)
    return len(s) == 9 and all(ch.isalnum() for ch in s)

# --- Interfaz gráfica ---
class App:
    def __init__(self, root):
        self.root = root
        root.title("Creador de Contraseñas - 50 (8 car.)")
        root.geometry("480x340")
        root.resizable(False, False)

        header = tk.Label(root, text="Creador de contraseñas (50) — 8 caracteres", font=("Segoe UI", 12, "bold"))
        header.pack(pady=(10,6))

        frame_inputs = tk.Frame(root)
        frame_inputs.pack(pady=4)

        # Validadores Tkinter: registrar funciones que controlan cada cambio
        vcmd_name = (root.register(self._validate_name_char), '%P')   # %P = valor propuesto
        vcmd_dni  = (root.register(self._validate_dni_char), '%P')

        tk.Label(frame_inputs, text="Nombre:", anchor="w", width=10).grid(row=0, column=0, padx=4, pady=2)
        self.entry_name = tk.Entry(frame_inputs, width=30, validate='key', validatecommand=vcmd_name)
        self.entry_name.grid(row=0, column=1, padx=4, pady=2)

        tk.Label(frame_inputs, text="Mascota:", anchor="w", width=10).grid(row=1, column=0, padx=4, pady=2)
        self.entry_pet = tk.Entry(frame_inputs, width=30)
        self.entry_pet.grid(row=1, column=1, padx=4, pady=2)

        tk.Label(frame_inputs, text="DNI:", anchor="w", width=10).grid(row=2, column=0, padx=4, pady=2)
        # DNI oculto mientras escribe, validación de longitud máxima 9 y alfanumérico
        self.entry_dni = tk.Entry(frame_inputs, width=30, show="*", validate='key', validatecommand=vcmd_dni)
        self.entry_dni.grid(row=2, column=1, padx=4, pady=2)

        self.btn_generate = tk.Button(root, text="Generar 50 contraseñas", command=self.generate_passwords, bg="#1976D2", fg="white", font=("Segoe UI", 10, "bold"))
        self.btn_generate.pack(pady=8)

        result_frame = tk.Frame(root)
        result_frame.pack(pady=6)

        self.lbl_index = tk.Label(result_frame, text="0 / 50", font=("Segoe UI", 9))
        self.lbl_index.grid(row=0, column=0, padx=6, sticky="w")

        self.lbl_password = tk.Label(result_frame, text="", font=("Courier", 18, "bold"), bg="#F1F1F1", width=18, relief="sunken")
        self.lbl_password.grid(row=1, column=0, columnspan=3, padx=6, pady=6)

        self.btn_next = tk.Button(result_frame, text="Otra contraseña", state="disabled", command=self.show_next, width=15)
        self.btn_next.grid(row=2, column=0, padx=6, pady=4)

        self.btn_copy = tk.Button(result_frame, text="Copiar", state="disabled", command=self.copy_current, width=10)
        self.btn_copy.grid(row=2, column=1, padx=6, pady=4)

        self.btn_reset = tk.Button(result_frame, text="Reiniciar", command=self.reset, width=10)
        self.btn_reset.grid(row=2, column=2, padx=6, pady=4)

        self.passwords = []
        self.current_index = -1

    # --- Funciones de validación usadas por Tkinter validatecommand ---
    def _validate_name_char(self, proposed: str) -> bool:
        # Permitir vacío (para borrar). Para contenido, comprobar todos los caracteres son letras o espacio.
        if proposed == "":
            return True
        # Verificar longitud máxima
        if len(proposed) > 40:
            return False
        # Verificar cada caracter
        for ch in proposed:
            if ch.isspace():  # Usar isspace() para cualquier espacio en blanco
                continue
            if not ch.isalpha():  # isalpha acepta letras acentuadas y ñ
                return False
        return True

    def _validate_dni_char(self, proposed: str) -> bool:
        # permitir vacío; máximo 9 caracteres; solo alfanuméricos
        if proposed == "":
            return True
        if len(proposed) > 9:
            return False
        for ch in proposed:
            if not ch.isalnum():
                return False
        return True

    # --- Generación y control ---
    def generate_passwords(self):
        name = self.entry_name.get().strip()
        pet = self.entry_pet.get().strip()
        dni = self.entry_dni.get().strip()

        # Validaciones finales antes de generar
        if not name:
            messagebox.showwarning("Nombre inválido", "El campo Nombre no puede estar vacío y sólo puede contener letras y espacios.")
            return
        if not is_name_valid(name):
            messagebox.showwarning("Nombre inválido", "El Nombre solo puede contener letras y espacios.")
            return
        if not pet:
            messagebox.showwarning("Mascota vacía", "Introduce el nombre de la mascota.")
            return
        if not dni:
            messagebox.showwarning("DNI vacío", "Introduce el DNI (9 caracteres).")
            return
        if not is_dni_valid(dni):
            messagebox.showwarning("DNI inválido", "El DNI debe tener exactamente 9 caracteres alfanuméricos.")
            return

        self.passwords = generate_passwords_from_inputs(name, pet, dni, count=TOTAL_TO_GENERATE, length=PW_LENGTH)
        self.current_index = -1
        self.btn_next.config(state="normal")
        self.btn_copy.config(state="normal")
        self.show_next()

    def show_next(self):
        if not self.passwords:
            return
        self.current_index += 1
        if self.current_index >= len(self.passwords):
            self.current_index = len(self.passwords) - 1
            messagebox.showinfo("Fin", "Se han mostrado todas las contraseñas generadas.")
            self.btn_next.config(state="disabled")
            return
        pw = self.passwords[self.current_index]
        self.lbl_password.config(text=pw)
        self.lbl_index.config(text=f"{self.current_index + 1} / {len(self.passwords)}")
        if self.current_index + 1 >= len(self.passwords):
            self.btn_next.config(state="disabled")

    def copy_current(self):
        if self.current_index < 0 or not self.passwords:
            return
        pw = self.passwords[self.current_index]
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(pw)
            messagebox.showinfo("Copiado", "Contraseña copiada al portapapeles.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar: {e}")

    def reset(self):
        self.entry_name.delete(0, tk.END)
        self.entry_pet.delete(0, tk.END)
        self.entry_dni.delete(0, tk.END)
        self.passwords = []
        self.current_index = -1
        self.lbl_password.config(text="")
        self.lbl_index.config(text=f"0 / {TOTAL_TO_GENERATE}")
        self.btn_next.config(state="disabled")
        self.btn_copy.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    
    # Pausa al cerrar la ventana - OPCIÓN 2 IMPLEMENTADA
    input("Presiona Enter para salir...")