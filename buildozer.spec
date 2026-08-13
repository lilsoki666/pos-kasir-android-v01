[app]
title = POS Kasir
package.name = poskasir
package.domain = org.tokosaya
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,csv
version = 1.0
requirements = python3==3.13.7,kivy
orientation = portrait
fullscreen = 0

# Android
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.ndk = 25b
android.accept_sdk_license = True
android.additional_cflags = -D_POSIX_C_SOURCE=200809L

[buildozer]
log_level = 2
warn_on_root = 1
