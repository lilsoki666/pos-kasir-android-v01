POS KASIR ANDROID
==================

Project Kivy yang siap dibuild menjadi APK.

PENTING:
- Saya tidak dapat menghasilkan APK Android native secara langsung dari lingkungan ini karena proses build Android/SDK/NDK memerlukan toolchain Android.
- Project ini sudah disiapkan agar dapat dibuild dengan Buildozer di Linux/WSL.

Build:
1. Install Ubuntu/WSL2 di Windows.
2. Install dependensi Buildozer.
3. cd ke folder project.
4. pip install --upgrade pip
5. pip install buildozer kivy
6. buildozer android debug
7. APK akan muncul di folder bin/.

Aplikasi memiliki:
- Produk & stok
- Pencarian produk/barcode
- Keranjang
- Pembayaran & kembalian
- Penyimpanan transaksi SQLite
- Struk teks
- Laporan CSV
