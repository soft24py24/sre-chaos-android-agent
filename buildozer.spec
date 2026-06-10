[app]

title = SRE Chaos Agent
package.name = srechaosagent
package.domain = org.soft24py24
version = 1.0.0
version.code = 1
icon.filename = %(source.dir)s/assets/icon.png

source.include_exts = py,png,jpg,kv,atlas,ttf,json
source.exclude_exts = spec,pyc,pyo,pyd,db,db3,so,o,dylib,zip,md,egg,gitignore,yml,txt

source.dir = %(source.dir)s
main.py = %(source.dir)s/main.py

requirements = python3,kivy==2.3.1,pyjnius

# Android
android.api = 31
android.minapi = 21
android.ndk = 23b
android.sdk = 30
android.permissions = INTERNET, READ_BATTERY_STATS, ACCESS_BATTERY_STATS
android.archs = arm64-v8a, armeabi-v7a
android.log = True
android.screen_orientation = portrait
android.gradle = True

[buildozer]
log_level = 2
cache_dir = %(user_dir)s/.buildozer/cache
build_dir = %(user_dir)s/.buildozer/build
dist_dir = %(user_dir)s/.buildozer/dist
check_requirements = True