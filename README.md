# UniversalPOS Android

UniversalPOS adalah aplikasi POS/kasir universal berbasis **Python + Kivy**, dirancang untuk toko retail, warung, coffee shop, distro, laundry, jasa, dan usaha lain yang membutuhkan katalog produk, transaksi, stok, pembayaran, serta cetak struk Bluetooth.

## Fitur utama
- Dashboard penjualan
- Master produk: nama, SKU/barcode, kategori, harga jual, harga modal, stok, foto produk
- Upload/pilih foto produk dari perangkat Android
- POS/kasir dengan pencarian produk dan keranjang
- Diskon transaksi dan pajak
- Pembayaran: Tunai, QRIS, Debit, Kredit, Transfer, E-Wallet
- Perhitungan kembalian otomatis untuk pembayaran tunai
- Riwayat transaksi
- Laporan penjualan sederhana
- Pengaturan nama toko, alamat, footer struk
- Pilihan struk **58mm** dan **80mm**
- Cetak ESC/POS melalui Bluetooth ke printer thermal yang sudah dipasangkan
- Simpan struk teks untuk audit/debug
- Backup database
- GitHub Actions untuk build APK
- Siap dikembangkan menjadi barcode scanner, cloud sync, multi-user, dan printer USB

## Struktur
```text
UniversalPOS/
├── main.py
├── buildozer.spec
├── requirements.txt
├── README.md
├── .gitignore
├── assets/
│   └── icon.svg
├── data/
│   └── .gitkeep
└── .github/workflows/android.yml
```

## Menjalankan di Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Build APK lokal
Pastikan Java/Android SDK/NDK dan Buildozer sudah tersedia.

```bash
pip install buildozer
buildozer android debug
```

APK biasanya berada di folder `bin/`.

## Build melalui GitHub
1. Buat repository GitHub.
2. Upload seluruh folder project.
3. Push ke branch `main`.
4. Buka tab **Actions**.
5. Jalankan workflow **Build UniversalPOS Android**.
6. APK debug akan disimpan sebagai artifact.

## Catatan Bluetooth
Printer thermal harus sudah dipairing dari pengaturan Bluetooth Android. Aplikasi mengambil daftar perangkat Bluetooth yang sudah dipasangkan, kemudian membuka koneksi RFCOMM/Serial Port Profile dan mengirim perintah ESC/POS.

Printer murah yang menggunakan Bluetooth Classic/SPP biasanya lebih cocok daripada printer BLE-only.

## Catatan Android
Pada Android 12+, permission `BLUETOOTH_SCAN` dan `BLUETOOTH_CONNECT` diperlukan. Buildozer spec sudah menyiapkan permission tersebut. Jika target perangkat tertentu membutuhkan permission tambahan, sesuaikan `buildozer.spec`.

## Lisensi
Bebas digunakan dan dimodifikasi untuk pengembangan internal maupun komersial.
