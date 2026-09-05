# Arsitektur UniversalPOS

## Data
SQLite lokal menyimpan:
- `products`: katalog + stok + path foto
- `sales`: header transaksi
- `sale_items`: detail transaksi
- `settings`: konfigurasi toko dan struk

## Workflow kasir
1. Kasir membuka menu Kasir.
2. Cari produk berdasarkan nama/SKU/kategori.
3. Tap produk untuk masuk keranjang.
4. Ubah qty jika diperlukan.
5. Isi diskon dan pajak.
6. Pilih metode pembayaran.
7. Untuk Tunai, masukkan uang pelanggan dan aplikasi menghitung kembalian.
8. Tekan Selesaikan & Cetak.
9. Transaksi disimpan ke SQLite.
10. Printer Bluetooth dapat dipilih dan menerima ESC/POS.
11. Stok dikurangi otomatis.

## Workflow produk
1. Menu Produk → + Produk.
2. Isi nama, SKU/barcode, kategori, harga jual, modal, stok.
3. Pilih foto.
4. Foto disalin ke folder aplikasi sehingga tidak bergantung pada lokasi file asli.

## Workflow printer
Android Settings → Bluetooth → Pair printer → UniversalPOS → Kasir → Selesaikan & Cetak → Bluetooth → pilih printer.

## Batasan MVP
- Barcode scanner kamera belum diaktifkan.
- Printer BLE-only tidak ditangani; implementasi memakai Bluetooth Classic SPP/RFCOMM.
- Belum ada cloud sync/multi-device.
- Editing/deleting produk dan varian belum ditambahkan pada MVP.
