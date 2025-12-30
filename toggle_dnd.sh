#!/bin/bash
current_mode=$(adb shell settings get global zen_mode)

if [[ "$current_mode" == *"0"* ]]; then
    adb shell cmd notification set_dnd priority
    #notify-send "🔕 DND Enabled"
else
    adb shell cmd notification set_dnd off
    #notify-send "🔔 DND Disabled"
fi
