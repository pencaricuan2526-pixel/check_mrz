#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalkulator MRZ Paspor Indonesia
================================

Fitur:
1. Kalkulator check digit MRZ umum.
2. Kalkulator nomor paspor Indonesia:
   - nomor paspor 8 karakter otomatis menjadi 9 karakter MRZ dengan filler "<".
   - contoh: E1234567 -> E1234567<
3. Kalkulator tanggal lahir:
   - input DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD, DDMMYYYY, atau YYMMDD.
   - output YYMMDD + check digit.
4. Kalkulator tanggal kedaluwarsa:
   - output YYMMDD + check digit.
5. Generator MRZ baris 2 paspor Indonesia.
6. Validator MRZ baris 2 paspor.

Cara menjalankan:
    python kalkulator_mrz_paspor_indonesia.py

Aplikasi ini hanya menggunakan library bawaan Python: tkinter, datetime, re.
"""

import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from datetime import datetime


WEIGHTS = (7, 3, 1)


# ============================================================
# LOGIKA UTAMA MRZ
# ============================================================

def clean_mrz_text(text: str) -> str:
    """Membersihkan teks MRZ tanpa mengubah filler '<'."""
    return str(text or "").strip().upper().replace(" ", "").replace("-", "")


def mrz_char_value(ch: str) -> int:
    """
    Konversi karakter MRZ ke nilai angka:
    0-9 = 0-9
    A-Z = 10-35
    <   = 0
    """
    ch = ch.upper()

    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    if "A" <= ch <= "Z":
        return ord(ch) - ord("A") + 10

    raise ValueError(f"Karakter tidak valid untuk MRZ: {ch!r}")


def mrz_check_digit(data: str) -> int:
    """
    Rumus check digit MRZ:
    SUM(nilai_karakter × bobot 7-3-1 berulang) MOD 10
    """
    data = clean_mrz_text(data)

    if not data:
        raise ValueError("Data MRZ tidak boleh kosong.")

    total = 0
    for index, ch in enumerate(data):
        total += mrz_char_value(ch) * WEIGHTS[index % 3]

    return total % 10


def mrz_calculation_rows(data: str):
    """Membuat rincian per karakter untuk ditampilkan di tabel."""
    data = clean_mrz_text(data)
    rows = []

    for index, ch in enumerate(data):
        value = mrz_char_value(ch)
        weight = WEIGHTS[index % 3]
        rows.append((index + 1, ch, value, weight, value * weight))

    return rows


def normalize_indonesian_passport_number(passport_number: str) -> str:
    """
    Menyesuaikan nomor paspor Indonesia menjadi field nomor dokumen MRZ 9 karakter.

    Field nomor dokumen pada MRZ paspor TD3 panjangnya 9 karakter.
    Banyak nomor paspor Indonesia hanya 8 karakter, sehingga perlu ditambah filler "<".
    """
    value = clean_mrz_text(passport_number)

    if not value:
        raise ValueError("Nomor paspor tidak boleh kosong.")

    for ch in value:
        mrz_char_value(ch)

    if len(value) > 9:
        raise ValueError("Nomor paspor maksimal 9 karakter untuk field nomor dokumen MRZ.")

    return value.ljust(9, "<")


def indonesian_passport_mrz_number(passport_number: str) -> tuple[str, str, str]:
    """
    Output:
    - input bersih
    - field 9 karakter
    - field 9 karakter + check digit
    """
    raw = clean_mrz_text(passport_number)
    field_9 = normalize_indonesian_passport_number(raw)
    cd = str(mrz_check_digit(field_9))
    return raw, field_9, field_9 + cd


def parse_date_to_yymmdd(date_text: str) -> str:
    """
    Mengubah tanggal ke format MRZ YYMMDD.

    Format input yang diterima:
    - DD/MM/YYYY
    - DD-MM-YYYY
    - YYYY-MM-DD
    - YYYY/MM/DD
    - DDMMYYYY
    - YYMMDD
    """
    s = str(date_text or "").strip()

    if not s:
        raise ValueError("Tanggal tidak boleh kosong.")

    if re.fullmatch(r"\d{6}", s):
        yy = int(s[0:2])
        mm = int(s[2:4])
        dd = int(s[4:6])

        if not (1 <= mm <= 12):
            raise ValueError("Bulan pada format YYMMDD tidak valid.")
        if not (1 <= dd <= 31):
            raise ValueError("Hari pada format YYMMDD tidak valid.")

        return s

    date_formats = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d%m%Y",
    )

    for fmt in date_formats:
        try:
            parsed = datetime.strptime(s, fmt)
            return parsed.strftime("%y%m%d")
        except ValueError:
            continue

    raise ValueError(
        "Format tanggal tidak dikenali. Gunakan DD/MM/YYYY, DD-MM-YYYY, "
        "YYYY-MM-DD, YYYY/MM/DD, DDMMYYYY, atau YYMMDD."
    )


def mrz_date_with_check_digit(date_text: str) -> tuple[str, str]:
    """Menghasilkan YYMMDD dan YYMMDD + check digit."""
    yymmdd = parse_date_to_yymmdd(date_text)
    cd = str(mrz_check_digit(yymmdd))
    return yymmdd, yymmdd + cd


def normalize_optional_data(optional_data: str) -> str:
    """Optional data MRZ baris 2 paspor TD3: 14 karakter."""
    value = clean_mrz_text(optional_data)

    for ch in value:
        mrz_char_value(ch)

    if len(value) > 14:
        raise ValueError("Optional data maksimal 14 karakter.")

    return value.ljust(14, "<")


def generate_mrz_line2_indonesia(
    passport_number: str,
    nationality: str,
    birth_date: str,
    sex: str,
    expiry_date: str,
    optional_data: str = "",
) -> dict:
    """
    Membuat MRZ baris 2 paspor TD3 sepanjang 44 karakter.

    Struktur:
    01-09 = nomor paspor/dokumen
    10    = check digit nomor paspor
    11-13 = kewarganegaraan, contoh IDN
    14-19 = tanggal lahir YYMMDD
    20    = check digit tanggal lahir
    21    = jenis kelamin M/F/<
    22-27 = tanggal kedaluwarsa YYMMDD
    28    = check digit tanggal kedaluwarsa
    29-42 = optional data
    43    = check digit optional data
    44    = composite check digit
    """
    doc_field = normalize_indonesian_passport_number(passport_number)
    doc_cd = str(mrz_check_digit(doc_field))

    nat = clean_mrz_text(nationality or "IDN")
    if len(nat) != 3:
        raise ValueError("Kode kewarganegaraan harus 3 karakter, contoh: IDN.")
    for ch in nat:
        if not ("A" <= ch <= "Z" or ch == "<"):
            raise ValueError("Kode kewarganegaraan hanya boleh huruf A-Z atau filler <.")

    birth_field = parse_date_to_yymmdd(birth_date)
    birth_cd = str(mrz_check_digit(birth_field))

    sex_value = clean_mrz_text(sex or "<")
    if sex_value not in ("M", "F", "<"):
        raise ValueError("Jenis kelamin harus M, F, atau <.")

    expiry_field = parse_date_to_yymmdd(expiry_date)
    expiry_cd = str(mrz_check_digit(expiry_field))

    optional_field = normalize_optional_data(optional_data)
    optional_cd = str(mrz_check_digit(optional_field))

    composite_data = (
        doc_field + doc_cd
        + birth_field + birth_cd
        + expiry_field + expiry_cd
        + optional_field + optional_cd
    )
    composite_cd = str(mrz_check_digit(composite_data))

    line2 = (
        doc_field + doc_cd
        + nat
        + birth_field + birth_cd
        + sex_value
        + expiry_field + expiry_cd
        + optional_field + optional_cd
        + composite_cd
    )

    return {
        "line2": line2,
        "document_number": doc_field,
        "document_cd": doc_cd,
        "nationality": nat,
        "birth": birth_field,
        "birth_cd": birth_cd,
        "sex": sex_value,
        "expiry": expiry_field,
        "expiry_cd": expiry_cd,
        "optional": optional_field,
        "optional_cd": optional_cd,
        "composite_cd": composite_cd,
        "length": len(line2),
    }


def validate_mrz_line2(line2: str) -> dict:
    """Memvalidasi semua check digit pada MRZ baris 2 paspor TD3."""
    s = clean_mrz_text(line2)

    if len(s) != 44:
        raise ValueError(f"MRZ baris 2 harus 44 karakter. Input saat ini {len(s)} karakter.")

    document_number = s[0:9]
    document_cd_actual = s[9]

    nationality = s[10:13]

    birth = s[13:19]
    birth_cd_actual = s[19]

    sex = s[20]

    expiry = s[21:27]
    expiry_cd_actual = s[27]

    optional = s[28:42]
    optional_cd_actual = s[42]

    composite_cd_actual = s[43]

    document_cd_calc = str(mrz_check_digit(document_number))
    birth_cd_calc = str(mrz_check_digit(birth))
    expiry_cd_calc = str(mrz_check_digit(expiry))
    optional_cd_calc = str(mrz_check_digit(optional))

    composite_data = s[0:10] + s[13:20] + s[21:43]
    composite_cd_calc = str(mrz_check_digit(composite_data))

    return {
        "line2": s,
        "document_number": document_number,
        "document_cd_actual": document_cd_actual,
        "document_cd_calc": document_cd_calc,
        "document_valid": document_cd_actual == document_cd_calc,
        "nationality": nationality,
        "birth": birth,
        "birth_cd_actual": birth_cd_actual,
        "birth_cd_calc": birth_cd_calc,
        "birth_valid": birth_cd_actual == birth_cd_calc,
        "sex": sex,
        "expiry": expiry,
        "expiry_cd_actual": expiry_cd_actual,
        "expiry_cd_calc": expiry_cd_calc,
        "expiry_valid": expiry_cd_actual == expiry_cd_calc,
        "optional": optional,
        "optional_cd_actual": optional_cd_actual,
        "optional_cd_calc": optional_cd_calc,
        "optional_valid": optional_cd_actual == optional_cd_calc,
        "composite_cd_actual": composite_cd_actual,
        "composite_cd_calc": composite_cd_calc,
        "composite_valid": composite_cd_actual == composite_cd_calc,
    }


# ============================================================
# DESAIN INTERFACE
# ============================================================

class MRZApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Kalkulator MRZ Paspor Indonesia")
        self.geometry("1080x760")
        self.minsize(980, 680)

        self.bg = "#F3F6FB"
        self.card_bg = "#FFFFFF"
        self.primary = "#1F4E79"
        self.primary_dark = "#143653"
        self.success = "#198754"
        self.danger = "#B42318"
        self.text = "#1F2937"
        self.muted = "#64748B"

        self.configure(bg=self.bg)

        self.setup_style()
        self.build_header()
        self.build_tabs()
        self.build_footer()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=self.bg)
        style.configure("TLabel", background=self.bg, foreground=self.text, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(12, 8))
        style.configure("Primary.TButton", background=self.primary, foreground="#FFFFFF")
        style.configure("Success.TButton", background=self.success, foreground="#FFFFFF")
        style.configure("Danger.TButton", background=self.danger, foreground="#FFFFFF")
        style.map("Primary.TButton", background=[("active", self.primary_dark)])
        style.map("Success.TButton", background=[("active", "#146C43")])
        style.map("Danger.TButton", background=[("active", "#912018")])

        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            font=("Segoe UI", 10, "bold"),
            padding=(16, 9),
            background="#E2E8F0",
            foreground=self.text,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#FFFFFF")],
            foreground=[("selected", self.primary)],
        )

        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#EAF0F8")

    def build_header(self):
        header = tk.Frame(self, bg=self.primary)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="Kalkulator MRZ Paspor Indonesia",
            bg=self.primary,
            fg="#FFFFFF",
            font=("Segoe UI", 20, "bold"),
        )
        title.pack(anchor="w", padx=22, pady=(16, 0))

        subtitle = tk.Label(
            header,
            text="Hitung nomor paspor, tanggal lahir, tanggal kedaluwarsa, generator MRZ baris 2, dan validasi check digit.",
            bg=self.primary,
            fg="#DDEBFF",
            font=("Segoe UI", 10),
        )
        subtitle.pack(anchor="w", padx=22, pady=(3, 16))

    def build_tabs(self):
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=16)

        self.tab_general = ttk.Frame(self.tabs)
        self.tab_passport = ttk.Frame(self.tabs)
        self.tab_dates = ttk.Frame(self.tabs)
        self.tab_generator = ttk.Frame(self.tabs)
        self.tab_validator = ttk.Frame(self.tabs)
        self.tab_guide = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_general, text="Check Digit Umum")
        self.tabs.add(self.tab_passport, text="Nomor Paspor")
        self.tabs.add(self.tab_dates, text="Tanggal MRZ")
        self.tabs.add(self.tab_generator, text="Generator Baris 2")
        self.tabs.add(self.tab_validator, text="Validasi Baris 2")
        self.tabs.add(self.tab_guide, text="Panduan")

        self.build_general_tab()
        self.build_passport_tab()
        self.build_dates_tab()
        self.build_generator_tab()
        self.build_validator_tab()
        self.build_guide_tab()

    def build_footer(self):
        footer = tk.Label(
            self,
            text="Rumus MRZ: SUM(nilai karakter × bobot 7-3-1) MOD 10  |  A=10 ... Z=35  |  < = 0",
            bg=self.bg,
            fg=self.muted,
            font=("Segoe UI", 9),
        )
        footer.pack(fill="x", pady=(0, 10))

    # ---------- komponen UI ----------
    def make_card(self, parent):
        outer = tk.Frame(parent, bg="#D8E0EA")
        outer.pack(fill="both", expand=True, padx=8, pady=8)

        inner = tk.Frame(outer, bg=self.card_bg)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        content = tk.Frame(inner, bg=self.card_bg)
        content.pack(fill="both", expand=True, padx=18, pady=18)
        return content

    def heading(self, parent, title, subtitle=None):
        tk.Label(
            parent,
            text=title,
            bg=self.card_bg,
            fg=self.text,
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")

        if subtitle:
            tk.Label(
                parent,
                text=subtitle,
                bg=self.card_bg,
                fg=self.muted,
                font=("Segoe UI", 10),
                wraplength=950,
                justify="left",
            ).pack(anchor="w", pady=(3, 14))

    def label(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            bg=self.card_bg,
            fg=self.text,
            font=("Segoe UI", 10),
            anchor="w",
        )

    def entry(self, parent, width=35):
        return tk.Entry(
            parent,
            width=width,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground="#CBD5E1",
        )

    def output_box(self, parent, height=8):
        box = ScrolledText(
            parent,
            height=height,
            font=("Consolas", 10),
            bg="#F8FAFC",
            fg="#111827",
            relief="solid",
            bd=1,
            wrap="word",
        )
        box.configure(state="disabled")
        return box

    def set_output(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("1.0", text)
        box.configure(state="disabled")

    def copy_text(self, text):
        if not text:
            messagebox.showwarning("Belum ada hasil", "Belum ada hasil yang bisa disalin.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Berhasil", "Hasil sudah disalin ke clipboard.")

    # ---------- Tab 1: check digit umum ----------
    def build_general_tab(self):
        card = self.make_card(self.tab_general)
        self.heading(
            card,
            "Kalkulator Check Digit MRZ Umum",
            "Masukkan field MRZ apa pun untuk menghitung check digit dan melihat rincian perkalian per karakter.",
        )

        form = tk.Frame(card, bg=self.card_bg)
        form.pack(fill="x", pady=(2, 12))

        self.label(form, "Data MRZ").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)

        self.general_input = self.entry(form, width=62)
        self.general_input.grid(row=0, column=1, sticky="we", pady=6)
        self.general_input.insert(0, "L898902C3")

        ttk.Button(
            form,
            text="Hitung",
            style="Primary.TButton",
            command=self.on_general_calculate,
        ).grid(row=0, column=2, padx=(12, 0), pady=6)

        form.columnconfigure(1, weight=1)

        self.general_output = self.output_box(card, height=5)
        self.general_output.pack(fill="x", pady=(0, 12))

        columns = ("position", "char", "value", "weight", "result")
        self.general_table = ttk.Treeview(card, columns=columns, show="headings", height=12)

        headings = {
            "position": ("Posisi", 80),
            "char": ("Karakter", 110),
            "value": ("Nilai", 100),
            "weight": ("Bobot", 100),
            "result": ("Hasil", 130),
        }

        for col, (text, width) in headings.items():
            self.general_table.heading(col, text=text)
            self.general_table.column(col, width=width, anchor="center")

        self.general_table.pack(fill="both", expand=True)

    def on_general_calculate(self):
        try:
            data = clean_mrz_text(self.general_input.get())
            rows = mrz_calculation_rows(data)
            total = sum(row[4] for row in rows)
            cd = mrz_check_digit(data)

            self.set_output(
                self.general_output,
                f"Data MRZ    : {data}\n"
                f"Total       : {total}\n"
                f"Check digit : {cd}\n"
                f"Rumus akhir : {total} MOD 10 = {cd}",
            )

            for item in self.general_table.get_children():
                self.general_table.delete(item)

            for row in rows:
                self.general_table.insert("", "end", values=row)

        except Exception as err:
            messagebox.showerror("Input tidak valid", str(err))

    # ---------- Tab 2: nomor paspor ----------
    def build_passport_tab(self):
        card = self.make_card(self.tab_passport)
        self.heading(
            card,
            "Kalkulator Nomor Paspor Indonesia",
            "Nomor paspor Indonesia yang 8 karakter otomatis diubah menjadi field MRZ 9 karakter dengan menambahkan filler <.",
        )

        form = tk.Frame(card, bg=self.card_bg)
        form.pack(fill="x", pady=(2, 12))

        self.label(form, "Nomor Paspor").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)

        self.passport_input = self.entry(form, width=40)
        self.passport_input.grid(row=0, column=1, sticky="we", pady=6)
        self.passport_input.insert(0, "E1234567")

        ttk.Button(
            form,
            text="Hitung",
            style="Primary.TButton",
            command=self.on_passport_calculate,
        ).grid(row=0, column=2, padx=(12, 0), pady=6)

        form.columnconfigure(1, weight=1)

        self.passport_output = self.output_box(card, height=11)
        self.passport_output.pack(fill="x", pady=(0, 12))

        ttk.Button(
            card,
            text="Salin Hasil Nomor MRZ",
            style="Success.TButton",
            command=lambda: self.copy_text(getattr(self, "passport_result_text", "")),
        ).pack(anchor="e")

        self.passport_result_text = ""

    def on_passport_calculate(self):
        try:
            raw, field_9, full = indonesian_passport_mrz_number(self.passport_input.get())
            cd = full[-1]
            self.passport_result_text = full

            self.set_output(
                self.passport_output,
                f"Input nomor paspor          : {raw}\n"
                f"Field nomor dokumen MRZ     : {field_9}\n"
                f"Check digit                 : {cd}\n"
                f"Hasil nomor MRZ             : {full}\n\n"
                f"Catatan:\n"
                f"- Field nomor dokumen pada MRZ paspor TD3 adalah 9 karakter.\n"
                f"- Jika input nomor paspor hanya 8 karakter, aplikasi menambahkan filler < di belakang.\n"
                f"- Contoh: E1234567 menjadi E1234567< lalu dihitung check digit-nya.",
            )

        except Exception as err:
            messagebox.showerror("Input tidak valid", str(err))

    # ---------- Tab 3: tanggal ----------
    def build_dates_tab(self):
        card = self.make_card(self.tab_dates)
        self.heading(
            card,
            "Kalkulator Tanggal Lahir dan Tanggal Kedaluwarsa",
            "Tanggal pada MRZ ditulis dengan format YYMMDD lalu ditambah check digit.",
        )

        form = tk.Frame(card, bg=self.card_bg)
        form.pack(fill="x", pady=(2, 12))

        self.label(form, "Tanggal Lahir").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)
        self.birth_input = self.entry(form, width=30)
        self.birth_input.grid(row=0, column=1, sticky="we", pady=6)
        self.birth_input.insert(0, "12/08/1974")

        ttk.Button(
            form,
            text="Hitung Tanggal Lahir",
            style="Primary.TButton",
            command=lambda: self.on_date_calculate("Tanggal lahir", self.birth_input.get()),
        ).grid(row=0, column=2, padx=(12, 0), pady=6)

        self.label(form, "Tanggal Kedaluwarsa").grid(row=1, column=0, sticky="w", padx=(0, 12), pady=6)
        self.expiry_input = self.entry(form, width=30)
        self.expiry_input.grid(row=1, column=1, sticky="we", pady=6)
        self.expiry_input.insert(0, "15/04/2034")

        ttk.Button(
            form,
            text="Hitung Tanggal Kedaluwarsa",
            style="Primary.TButton",
            command=lambda: self.on_date_calculate("Tanggal kedaluwarsa", self.expiry_input.get()),
        ).grid(row=1, column=2, padx=(12, 0), pady=6)

        form.columnconfigure(1, weight=1)

        self.date_output = self.output_box(card, height=13)
        self.date_output.pack(fill="x", pady=(0, 12))

    def on_date_calculate(self, title, date_text):
        try:
            yymmdd, full = mrz_date_with_check_digit(date_text)
            cd = full[-1]

            self.set_output(
                self.date_output,
                f"{title}\n"
                f"Input tanggal          : {date_text}\n"
                f"Format MRZ YYMMDD      : {yymmdd}\n"
                f"Check digit            : {cd}\n"
                f"Hasil MRZ              : {full}\n\n"
                f"Format yang diterima:\n"
                f"- DD/MM/YYYY, contoh 12/08/1974\n"
                f"- DD-MM-YYYY, contoh 12-08-1974\n"
                f"- YYYY-MM-DD, contoh 1974-08-12\n"
                f"- YYYY/MM/DD, contoh 1974/08/12\n"
                f"- DDMMYYYY, contoh 12081974\n"
                f"- YYMMDD, contoh 740812",
            )

        except Exception as err:
            messagebox.showerror("Input tidak valid", str(err))

    # ---------- Tab 4: generator ----------
    def build_generator_tab(self):
        card = self.make_card(self.tab_generator)
        self.heading(
            card,
            "Generator MRZ Baris 2 Paspor Indonesia",
            "Aplikasi akan menyusun MRZ baris 2 sepanjang 44 karakter sesuai struktur paspor TD3.",
        )

        form = tk.Frame(card, bg=self.card_bg)
        form.pack(fill="x", pady=(2, 12))

        labels = [
            "Nomor Paspor",
            "Kewarganegaraan",
            "Tanggal Lahir",
            "Jenis Kelamin",
            "Tanggal Kedaluwarsa",
            "Optional Data",
        ]

        for row, label_text in enumerate(labels):
            self.label(form, label_text).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=6)

        self.gen_passport = self.entry(form, width=35)
        self.gen_nationality = self.entry(form, width=10)
        self.gen_birth = self.entry(form, width=25)
        self.gen_sex = tk.StringVar(value="M")
        self.gen_sex_combo = ttk.Combobox(
            form,
            textvariable=self.gen_sex,
            values=("M", "F", "<"),
            state="readonly",
            width=8,
        )
        self.gen_expiry = self.entry(form, width=25)
        self.gen_optional = self.entry(form, width=35)

        self.gen_passport.grid(row=0, column=1, sticky="we", pady=6)
        self.gen_nationality.grid(row=1, column=1, sticky="w", pady=6)
        self.gen_birth.grid(row=2, column=1, sticky="we", pady=6)
        self.gen_sex_combo.grid(row=3, column=1, sticky="w", pady=6)
        self.gen_expiry.grid(row=4, column=1, sticky="we", pady=6)
        self.gen_optional.grid(row=5, column=1, sticky="we", pady=6)

        self.gen_passport.insert(0, "E1234567")
        self.gen_nationality.insert(0, "IDN")
        self.gen_birth.insert(0, "12/08/1974")
        self.gen_expiry.insert(0, "15/04/2034")

        form.columnconfigure(1, weight=1)

        btns = tk.Frame(card, bg=self.card_bg)
        btns.pack(fill="x", pady=(0, 12))

        ttk.Button(
            btns,
            text="Buat MRZ Baris 2",
            style="Primary.TButton",
            command=self.on_generate_line2,
        ).pack(side="left")

        ttk.Button(
            btns,
            text="Salin MRZ Baris 2",
            style="Success.TButton",
            command=lambda: self.copy_text(getattr(self, "generated_line2", "")),
        ).pack(side="left", padx=10)

        self.generator_output = self.output_box(card, height=14)
        self.generator_output.pack(fill="both", expand=True)

        self.generated_line2 = ""

    def on_generate_line2(self):
        try:
            result = generate_mrz_line2_indonesia(
                passport_number=self.gen_passport.get(),
                nationality=self.gen_nationality.get(),
                birth_date=self.gen_birth.get(),
                sex=self.gen_sex.get(),
                expiry_date=self.gen_expiry.get(),
                optional_data=self.gen_optional.get(),
            )
            self.generated_line2 = result["line2"]

            self.set_output(
                self.generator_output,
                f"MRZ Baris 2:\n"
                f"{result['line2']}\n\n"
                f"Panjang karakter     : {result['length']}\n\n"
                f"Rincian field:\n"
                f"Nomor paspor         : {result['document_number']} | CD: {result['document_cd']}\n"
                f"Kewarganegaraan      : {result['nationality']}\n"
                f"Tanggal lahir        : {result['birth']} | CD: {result['birth_cd']}\n"
                f"Jenis kelamin        : {result['sex']}\n"
                f"Tanggal kedaluwarsa  : {result['expiry']} | CD: {result['expiry_cd']}\n"
                f"Optional data        : {result['optional']} | CD: {result['optional_cd']}\n"
                f"Composite CD         : {result['composite_cd']}",
            )

        except Exception as err:
            messagebox.showerror("Input tidak valid", str(err))

    # ---------- Tab 5: validator ----------
    def build_validator_tab(self):
        card = self.make_card(self.tab_validator)
        self.heading(
            card,
            "Validasi MRZ Baris 2",
            "Masukkan MRZ baris 2 sepanjang 44 karakter untuk mengecek validitas setiap check digit.",
        )

        form = tk.Frame(card, bg=self.card_bg)
        form.pack(fill="x", pady=(2, 12))

        self.label(form, "MRZ Baris 2").grid(row=0, column=0, sticky="w", padx=(0, 12), pady=6)

        self.validator_input = self.entry(form, width=85)
        self.validator_input.grid(row=0, column=1, sticky="we", pady=6)

        ttk.Button(
            form,
            text="Validasi",
            style="Primary.TButton",
            command=self.on_validate_line2,
        ).grid(row=0, column=2, padx=(12, 0), pady=6)

        form.columnconfigure(1, weight=1)

        self.validator_output = self.output_box(card, height=18)
        self.validator_output.pack(fill="both", expand=True)

    def on_validate_line2(self):
        try:
            result = validate_mrz_line2(self.validator_input.get())

            valid_items = (
                result["document_valid"],
                result["birth_valid"],
                result["expiry_valid"],
                result["optional_valid"],
                result["composite_valid"],
            )
            overall = all(valid_items)

            def status(flag):
                return "VALID" if flag else "TIDAK VALID"

            self.set_output(
                self.validator_output,
                f"Status keseluruhan: {status(overall)}\n"
                f"MRZ Baris 2       : {result['line2']}\n"
                f"Panjang karakter  : {len(result['line2'])}\n\n"

                f"1. Nomor Paspor\n"
                f"   Data      : {result['document_number']}\n"
                f"   CD MRZ    : {result['document_cd_actual']}\n"
                f"   CD Hitung : {result['document_cd_calc']}\n"
                f"   Status    : {status(result['document_valid'])}\n\n"

                f"2. Tanggal Lahir\n"
                f"   Data      : {result['birth']}\n"
                f"   CD MRZ    : {result['birth_cd_actual']}\n"
                f"   CD Hitung : {result['birth_cd_calc']}\n"
                f"   Status    : {status(result['birth_valid'])}\n\n"

                f"3. Tanggal Kedaluwarsa\n"
                f"   Data      : {result['expiry']}\n"
                f"   CD MRZ    : {result['expiry_cd_actual']}\n"
                f"   CD Hitung : {result['expiry_cd_calc']}\n"
                f"   Status    : {status(result['expiry_valid'])}\n\n"

                f"4. Optional Data\n"
                f"   Data      : {result['optional']}\n"
                f"   CD MRZ    : {result['optional_cd_actual']}\n"
                f"   CD Hitung : {result['optional_cd_calc']}\n"
                f"   Status    : {status(result['optional_valid'])}\n\n"

                f"5. Composite Check Digit\n"
                f"   CD MRZ    : {result['composite_cd_actual']}\n"
                f"   CD Hitung : {result['composite_cd_calc']}\n"
                f"   Status    : {status(result['composite_valid'])}",
            )

        except Exception as err:
            messagebox.showerror("Input tidak valid", str(err))

    # ---------- Tab 6: panduan ----------
    def build_guide_tab(self):
        card = self.make_card(self.tab_guide)
        self.heading(
            card,
            "Panduan Singkat",
            "Ringkasan rumus dan struktur MRZ baris 2 paspor.",
        )

        guide = self.output_box(card, height=26)
        guide.pack(fill="both", expand=True)

        self.set_output(
            guide,
            "RUMUS CHECK DIGIT MRZ\n"
            "======================\n\n"
            "Check Digit = SUM(nilai karakter × bobot) MOD 10\n\n"
            "Bobot berulang dari kiri ke kanan:\n"
            "7, 3, 1, 7, 3, 1, dan seterusnya.\n\n"
            "Nilai karakter:\n"
            "- Angka 0 sampai 9 = sesuai angka tersebut.\n"
            "- Huruf A sampai Z = A=10, B=11, C=12, ..., Z=35.\n"
            "- Filler < = 0.\n\n\n"

            "NOMOR PASPOR INDONESIA\n"
            "======================\n\n"
            "Pada MRZ paspor TD3, field nomor dokumen berisi 9 karakter.\n"
            "Jika nomor paspor Indonesia hanya 8 karakter, tambahkan filler < di belakang.\n\n"
            "Contoh:\n"
            "E1234567 -> E1234567< -> hitung check digit.\n\n\n"

            "FORMAT TANGGAL MRZ\n"
            "==================\n\n"
            "Tanggal lahir dan tanggal kedaluwarsa ditulis dalam format YYMMDD.\n"
            "Setelah itu dihitung check digit-nya.\n\n"
            "Contoh:\n"
            "12/08/1974 -> 740812 -> hitung check digit.\n\n\n"

            "STRUKTUR MRZ BARIS 2 PASPOR TD3\n"
            "===============================\n\n"
            "Posisi 01-09 : nomor paspor/dokumen\n"
            "Posisi 10    : check digit nomor paspor\n"
            "Posisi 11-13 : kewarganegaraan, contoh IDN\n"
            "Posisi 14-19 : tanggal lahir YYMMDD\n"
            "Posisi 20    : check digit tanggal lahir\n"
            "Posisi 21    : jenis kelamin M/F/<\n"
            "Posisi 22-27 : tanggal kedaluwarsa YYMMDD\n"
            "Posisi 28    : check digit tanggal kedaluwarsa\n"
            "Posisi 29-42 : optional data\n"
            "Posisi 43    : check digit optional data\n"
            "Posisi 44    : composite check digit\n\n"
            "Composite check digit dihitung dari gabungan:\n"
            "posisi 1-10 + posisi 14-20 + posisi 22-43.\n"
        )


if __name__ == "__main__":
    app = MRZApp()
    app.mainloop()
