# Kalkulator MRZ Paspor Indonesia

Aplikasi desktop sederhana berbasis Python Tkinter untuk menghitung dan memvalidasi **Machine Readable Zone (MRZ)** pada paspor, dengan penyesuaian untuk contoh paspor Indonesia.

## Fitur

- Kalkulator check digit MRZ umum
- Kalkulator nomor paspor Indonesia
  - nomor paspor 8 karakter otomatis menjadi 9 karakter MRZ dengan filler `<`
  - contoh: `E1234567` menjadi `E1234567<`
- Kalkulator tanggal lahir MRZ
  - format `YYMMDD + check digit`
- Kalkulator tanggal kedaluwarsa MRZ
  - format `YYMMDD + check digit`
- Generator MRZ baris 2 paspor Indonesia
- Validator MRZ baris 2 sepanjang 44 karakter
- Tampilan GUI menggunakan Tkinter

## Rumus Check Digit MRZ

Rumus dasar:

```text
Check Digit = SUM(nilai karakter × bobot) MOD 10
```

Bobot karakter dari kiri ke kanan berulang:

```text
7, 3, 1, 7, 3, 1, ...
```

Nilai karakter:

```text
0-9 = sesuai angka
A-Z = A=10, B=11, C=12, ..., Z=35
<   = 0
```

## Struktur MRZ Baris 2 Paspor TD3

```text
Posisi 01-09 : Nomor paspor/dokumen
Posisi 10    : Check digit nomor paspor
Posisi 11-13 : Kewarganegaraan, contoh IDN
Posisi 14-19 : Tanggal lahir YYMMDD
Posisi 20    : Check digit tanggal lahir
Posisi 21    : Jenis kelamin M/F/<
Posisi 22-27 : Tanggal kedaluwarsa YYMMDD
Posisi 28    : Check digit tanggal kedaluwarsa
Posisi 29-42 : Optional data
Posisi 43    : Check digit optional data
Posisi 44    : Composite check digit
```

Composite check digit dihitung dari gabungan:

```text
posisi 1-10 + posisi 14-20 + posisi 22-43
```

## Cara Menjalankan

Pastikan Python sudah terinstal.

Jalankan perintah berikut:

```bash
python kalkulator_mrz_paspor_indonesia.py
```

Jika menggunakan macOS atau Linux:

```bash
python3 kalkulator_mrz_paspor_indonesia.py
```

## Dependensi

Aplikasi ini tidak membutuhkan library tambahan.

Library yang digunakan adalah library bawaan Python:

- `tkinter`
- `datetime`
- `re`

## Struktur Folder

```text
kalkulator-mrz-paspor-indonesia/
├── kalkulator_mrz_paspor_indonesia.py
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Catatan

Aplikasi ini dibuat untuk membantu perhitungan dan validasi check digit MRZ paspor. Validitas administratif dokumen tetap harus mengacu pada sistem dan ketentuan resmi yang berlaku.
