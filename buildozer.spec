[app]

# ------------------------------------------------------------

# BASIC APPLICATION

# ------------------------------------------------------------

title = UniversalPOS

package.name = universalpos

package.domain = com.universalpos

source.dir = .

source.main = main.py

source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json,db,svg

version = 0.1.0

# JANGAN tambahkan version.regex.

# Gunakan version SAJA untuk menghindari:

# Conflict between "version" and "version.regex"

# ------------------------------------------------------------

# REQUIREMENTS

# ------------------------------------------------------------

requirements = python3,kivy

# PyJNIus JANGAN ditulis manual di sini untuk versi stabil dasar.

# ------------------------------------------------------------

# DISPLAY

# ------------------------------------------------------------

orientation = portrait

fullscreen = 0

# ------------------------------------------------------------

# ANDROID

# ------------------------------------------------------------

android.api = 33

android.minapi = 24

android.ndk = 25b

android.build_tools_version = 33.0.2

android.archs = arm64-v8a,armeabi-v7a

android.androidx = True

# ------------------------------------------------------------

# ANDROID PERMISSIONS

# ------------------------------------------------------------

android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN

# ------------------------------------------------------------

# ICON

# ------------------------------------------------------------

icon.filename = %(source.dir)s/assets/icon.png

# ------------------------------------------------------------

# PRESPLASH

# ------------------------------------------------------------

# Aktifkan hanya jika file berikut benar-benar tersedia:

#

# presplash.filename = %(source.dir)s/assets/presplash.png

# ------------------------------------------------------------

# ANDROID BACKGROUND / LOGCAT

# ------------------------------------------------------------

android.add_src = src

android.entrypoint = org.kivy.android.PythonActivity

# ------------------------------------------------------------

# PYTHON FOR ANDROID

# ------------------------------------------------------------

p4a.bootstrap = sdl2

# ------------------------------------------------------------

# BUILD SETTINGS

# ------------------------------------------------------------

android.accept_sdk_license = True

android.release_artifact = apk

android.debug_artifact = apk

# ------------------------------------------------------------

# STORAGE / FILES

# ------------------------------------------------------------

# Database aplikasi disimpan otomatis di:

# App.user_data_dir

#

# Jangan menyimpan database aktif di:

# /sdcard

#

# sehingga aplikasi tidak membutuhkan:

# READ_EXTERNAL_STORAGE

# WRITE_EXTERNAL_STORAGE

# ------------------------------------------------------------

# LOGGING

# ------------------------------------------------------------

log_level = 2

warn_on_root = 1

[buildozer]

log_level = 2

warn_on_root = 1
