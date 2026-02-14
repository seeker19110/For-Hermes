#!/bin/bash
# Monitor Chromecast UI dump; press ENTER when "Skip Intro" appears
DEVICE="192.168.4.64:34159"
while true; do
  adb -s "$DEVICE" shell uiautomator dump /sdcard/window_dump.xml >/dev/null 2>&1
  adb -s "$DEVICE" shell cat /sdcard/window_dump.xml 2>/dev/null | grep -qi "Skip Intro"
  if [ $? -eq 0 ]; then
    adb -s "$DEVICE" shell input keyevent KEYCODE_ENTER
    sleep 5
  fi
  sleep 8
done
