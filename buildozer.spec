[app]

title = UniversalPOS

package.name = universalpos

package.domain = org.universalpos

version = 1.0.0

source.dir = .

source.include_exts = py,png,jpg,jpeg,kv,atlas,json,txt,svg,ttf,db

source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__,venv,.venv,tests

requirements = python3,kivy,pyjnius

orientation = portrait

fullscreen = 0

icon.filename = %(source.dir)s/assets/icon.png

android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_SCAN,BLUETOOTH_CONNECT,READ_MEDIA_IMAGES

android.api = 35

android.minapi = 24

android.ndk_version = 27c

android.archs = arm64-v8a

android.enable_androidx = True

android.enable_jetifier = True

android.accept_sdk_license = True

android.allow_backup = True

android.add_src = android_src

p4a.branch = develop


[buildozer]

log_level = 2

warn_on_root = 1
