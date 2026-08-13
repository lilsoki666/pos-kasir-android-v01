[app]
title = POS Kasir
package.name = poskasir
package.domain = org.tokosaya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,csv
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# Android
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
