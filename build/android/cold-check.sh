#!/usr/bin/env bash
# Check: app opened for the first time in days (saved web files expired) on a connection that never answers.
set -u
OUT=shots; mkdir -p $OUT; PKG=uk.sourmilkman.underway
python3 -c "
import socket
s=socket.socket(); s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind(('0.0.0.0',9999)); s.listen(200)
held=[]
while True: held.append(s.accept()[0])
" & HANG=$!
for v in old new; do
  adb uninstall $PKG >/dev/null 2>&1; adb install -r $v.apk
  adb shell cmd connectivity airplane-mode disable
  adb shell settings put global http_proxy 10.0.2.2:9999; sleep 3
  adb shell am start -n $PKG/.MainActivity >/dev/null; sleep 20
  adb exec-out screencap -p > $OUT/cold-$v-weak-signal.png; echo "saved $v"
  adb shell settings delete global http_proxy
done
kill $HANG
