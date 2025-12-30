#!/usr/bin/env python3
import os
import subprocess
import sys
from plyer import notification

import gi
gi.require_version('Gtk', '3.0')
try:
	gi.require_version('AppIndicator3', '0.1')
	from gi.repository import AppIndicator3
except ValueError:
	gi.require_version('AyatanaAppIndicator3', '0.1')
	from gi.repository import AyatanaAppIndicator3 as AppIndicator3
from gi.repository import Gtk, GLib

workdir=os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(workdir)
warning20 = False
warning10 = False
warning5 = False
warning80 = False
warning90 = False
BATTERY_STATES = {"-1": "unavailable", "2": "charging", "3": "discharging", "5": "charged", }


def get_battery_info():
	os.system("/home/diam0ndkiller/scripts/phone/get_phone_battery_adb.py")
	with open("battery_data.txt", "r") as file: return file.read()


def update_indicator(src):
	global warning5, warning10, warning20, warning80, warning90, last_time_stamp, previous_last_time_stamp

	indicator.set_icon(f"{workdir}/battery_0.png")
	indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

	battery_info = get_battery_info()

	if battery_info == "":
		percentage = "-1"
		state = "-1"
		ip = "unavailable"
	else:
		for line in battery_info.split("\n"):
			if "  level:" in line: percentage = line.split("level:")[1].strip()
			if "  status:" in line: state = line.split("status:")[1].strip()
		try:
			percentage
			ip = battery_info.split("\n")[0]
		except:
			percentage = "-1"
			state = "-1"
			ip = "unavailable"

	percentage_int = int(percentage)
	charging = state == "2"

	if state == "5":
		icon_path = "assets/battery_full.png"
	elif charging:
		if percentage_int > 75: icon_path = "assets/battery_charging_100.png"
		elif percentage_int > 30: icon_path = "assets/battery_charging_60.png"
		elif percentage_int > 0: icon_path = "assets/battery_charging_30.png"
		else: icon_path = "assets/battery_empty.png"
	else:
		if percentage_int > 75: icon_path = "assets/battery_100.png"
		elif percentage_int > 30: icon_path = "assets/battery_60.png"
		elif percentage_int > 0: icon_path = "assets/battery_30.png"
		else: icon_path = "assets/battery_empty.png"

	print(icon_path)

	indicator.set_icon(f"{workdir}/{icon_path}")

	if percentage_int > 5 and charging and warning5: warning5 = False
	if percentage_int > 10 and charging and warning10: warning10 = False
	if percentage_int > 20 and charging and warning20: warning20 = False

	if percentage_int < 80 and not charging and warning80: warning80 = False
	if percentage_int < 90 and not charging and warning90: warning90 = False

	if 0 <= percentage_int <= 5 and not charging and not warning5:
		notification.notify(title="Phone Power Critical", message="5% power left, connect charger", app_name="phone_battery_indicator", app_icon=f"{workdir}/battery_0.png")
		warning5 = True
	elif 5 <= percentage_int <= 10 and not charging and not warning10:
		notification.notify(title="Phone Power Low", message="10% power left, connect charger", app_name="phone_battery_indicator", app_icon=f"{workdir}/battery_30.png")
		warning10 = True
	elif 10 <= percentage_int <= 20 and not charging and not warning20:
		notification.notify(title="Phone Power Low", message="20% power, charge to reduce battery stress", app_name="phone_battery_indicator", app_icon=f"{workdir}/battery_30.png")
		warning20 = True
	elif 89 >= percentage_int >= 80 and charging and not warning80:
		notification.notify(title="Phone Power High", message="80% power, disconnect to reduce battery stress", app_name="phone_battery_indicator", app_icon=f"{workdir}/battery_100.png")
		warning80 = True
	elif 100 >= percentage_int >= 90 and charging and not warning90:
		notification.notify(title="Phone Power Very High", message="90% power, disconnect to reduce battery stress", app_name="phone_battery_indicator", app_icon=f"{workdir}/battery_full.png")
		warning90 = True

	if percentage_int < 0: percentage = "N/A"
	percentage += f"% ({BATTERY_STATES[state]})"

	print(ip, percentage)

	indicator.set_menu(build_menu(percentage, icon_path, ip))


def update_click(src):
	update_indicator(src)


def auto_update():
	update_indicator(indicator)
	GLib.timeout_add(30000, auto_update)


def build_menu(percentage, icon, ip):
	menu = Gtk.Menu()

	item_title = Gtk.ImageMenuItem.new_with_label(f"Phone battery @{ip}: \n{percentage}")
	icon = Gtk.Image.new_from_file(icon)
	icon.set_size_request(24, 24)
	item_title.set_image(icon)
	item_title.set_sensitive(False)
	menu.append(item_title)

	menu.append(Gtk.SeparatorMenuItem())

	item_update = Gtk.MenuItem(label="Update")
	item_update.connect("activate", update_click)
	menu.append(item_update)

	item_quit = Gtk.MenuItem(label="Quit")
	item_quit.connect("activate", quit)
	menu.append(item_quit)

	menu.show_all()
	return menu


def quit(source):
	Gtk.main_quit()


if __name__ == "__main__":
	APPINDICATOR_ID = "battery-indicator"
	indicator = AppIndicator3.Indicator.new(APPINDICATOR_ID, "", AppIndicator3.IndicatorCategory.HARDWARE)
	indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
	indicator.set_icon("battery_0.png")
	indicator.set_label("Phone Battery", "")
	auto_update()

	Gtk.main()

