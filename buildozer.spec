[app]
title = Code Quest
package.name = codequest
package.domain = org.codequest
source.dir = .
source.include_exts = py,json
source.exclude_dirs = venv,dist,build,.github,__pycache__,.venv
version = 1.0
requirements = python3,pygame-ce,numpy
orientation = landscape
fullscreen = 1
android.api = 33
android.minapi = 24
android.ndk_api = 24
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
