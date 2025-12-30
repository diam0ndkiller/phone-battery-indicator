# Phone Battery Indicator
This is a script that connects to a mobile device running android to display its battery level in a status indicator inside a GTK-compatible Linux desktop's status tray.

## Requirements
Install the following packages to give Python access to the required libraries and tools (list is for Ubuntu-based distros, may vary on others):
- `python3-gi`
- `gir1.2-gtk-3.0`
- `gir1.2-appindicator3-0.1` OR `gir1.2-ayatanaappindicator3-0.1` (try which one is able to install without breaking other apps)
- `google-android-platform-tools-installer` OR `adb` (choose either Google's official package or your distro's repackaged version)

Install on Ubuntu with

```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 adb
```

## Setup
Clone the repo. To use the script, either directly run `phone_battery_indicator_adb.py` or add it to your desktop's autostart setting.

This script connects to the first device from `phone_ips.txt` that has port 5542 open in adb tcpip mode. To use, enter you device's IP address into the file. To open the port, connect you phone via USB, go into developer settings and enable USB debugging. Then, on your PC, run

```bash
adb tcpip 5542
```

> [!WARNING]
> The tcpip mode will skip the modern adb pairing step and will instead fall back to allowing all devices that have been authorized to debug via USB.
