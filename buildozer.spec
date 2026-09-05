[app]

# (str) Title of your application
title = UT Kasirrr

# (str) Package name
package.name = utkasir

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Application version (WAJIB ADA)
version = 0.1

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (include db for sample data if needed)
source.include_exts = py,png,jpg,kv,atlas,db

# (list) Application requirements
# PENTING: Hapus versi spesifik dan pyjnius dari requirements.
# Biarkan p4a memuat versi pyjnius/sdl2 yang sesuai secara otomatis.
requirements = python3,kivy

# (str) Supported orientation (landscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (str) Android Build Tools version (TAMBAHKAN/SESUAIKAN BARIS INI)
android.build_tools_version = 33.0.0

# (int) Minimum API required
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b
# (list) The Android archs to build for
# PENTING: Wajib tambahkan ini agar kompatibel dengan HP Android modern (64-bit)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Enable AndroidX support
android.androidx = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = disable, 1 = enable)
warn_on_root = 1
