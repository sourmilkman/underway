#!/usr/bin/env bash
# Runs on an Android emulator in GitHub Actions.
# Opens the app (a) with no connection at all and (b) with a connection that never answers,
# and saves a screenshot of each. Runs the previous APK too, for comparison, when one is given.
set -u
OUT=shots; mkdir -p $OUT
PKG=uk.sourmilkman.underway

# A "connection" that accepts requests and never replies, like a weak signal or a Wi-Fi sign-in page.
python3 -c "
import socket,time
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind(('0.0.0.0',9999)); s.listen(200)
held=[]
while True: held.append(s.accept()[0])
" & HANG=$!

shot () { # name
  adb shell am force-stop $PKG
  adb shell am start -n $PKG/.MainActivity >/dev/null
  sleep 15
  adb exec-out screencap -p > $OUT/$1.png
  echo "saved $1"
}
online () { adb shell settings delete global http_proxy >/dev/null; adb shell cmd connectivity airplane-mode disable; sleep 3; }
nosignal () { adb shell cmd connectivity airplane-mode enable; sleep 3; }
weaksignal () { adb shell cmd connectivity airplane-mode disable; adb shell settings put global http_proxy 10.0.2.2:9999; sleep 3; }

run () { # apk label
  adb uninstall $PKG >/dev/null 2>&1
  adb install -r "$1" || { echo "install failed: $1"; return; }
  online; shot "$2-1-online-first-open"
  nosignal; shot "$2-2-no-signal"
  weaksignal; shot "$2-3-weak-signal"
  online
}

[ -f old.apk ] && run old.apk old
run Underway.apk new
kill $HANG 2>/dev/null
ls -la $OUT
