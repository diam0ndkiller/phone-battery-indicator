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

BATTERY_STATES_BY_DESCRIPTION = {"unavailable": "-1", "charging": "2", "discharging": "3", "halted": "4", "full": "5"}
BATTERY_STATES_BY_ID = {v: k for k, v in BATTERY_STATES_BY_DESCRIPTION.items()}
BATTERY_ICONS = {"empty": "assets/battery_empty.png",
				 "red": "assets/battery_red.png",
				 "yellow": "assets/battery_yellow.png",
				 "green": "assets/battery_green.png",
				 "red_charging": "assets/battery_red_charging.png",
				 "yellow_charging": "assets/battery_yellow_charging.png",
				 "green_charging": "assets/battery_green_charging.png",
				 "green_halted": "assets/battery_green_halted.png",
				 "full": "assets/battery_full.png"}


def get_battery_info(): return subprocess.getoutput(["./get_phone_battery_adb.py"])
def full_asset_path(path: str): return f"{workdir}/{path}"


def battery_icon_path(state: str, percentage: int):
	if state == BATTERY_STATES_BY_DESCRIPTION["full"]:
		return BATTERY_ICONS["full"]
	
	elif state == BATTERY_STATES_BY_DESCRIPTION["halted"]:
		return BATTERY_ICONS["green_halted"]
	
	elif state == BATTERY_STATES_BY_DESCRIPTION["charging"]:
		if percentage > 75: return BATTERY_ICONS["green_charging"]
		elif percentage > 30: return BATTERY_ICONS["yellow_charging"]
		elif percentage > 0: return BATTERY_ICONS["red_charging"]

	elif state == BATTERY_STATES_BY_DESCRIPTION["discharging"]:
		if percentage > 75: return BATTERY_ICONS["green"]
		elif percentage > 30: return BATTERY_ICONS["yellow"]
		elif percentage > 0: return BATTERY_ICONS["red"]
	
	return BATTERY_ICONS["empty"]


def update_indicator(event_src):
	global INDICATOR

	INDICATOR.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

	percentage = -1
	state = "-1"
	ip = "unavailable"

	battery_info = get_battery_info()
	
	if battery_info:
		ip = battery_info.split("\n")[0]
		for line in battery_info.split("\n"):
			if "  level:" in line: percentage = int(line.split("level:")[1].strip())
			if "  status:" in line: state = line.split("status:")[1].strip()

	if percentage < 0: tooltip = "Phone battery: N/A"
	else: tooltip = f"Phone battery @{ip}: \n{percentage}% ({BATTERY_STATES_BY_ID[state]})"

	INDICATOR.set_icon_full(full_asset_path(battery_icon_path(state, percentage)), tooltip)

	INDICATOR.set_menu(build_menu(tooltip))

	handle_warnings(percentage, state)


def handle_warnings(percentage_int: int, state: str):
	global warning5, warning10, warning20, warning80, warning90

	charging = state == BATTERY_STATES_BY_DESCRIPTION["charging"];

	if percentage_int > 5 and charging and warning5: warning5 = False
	if percentage_int > 10 and charging and warning10: warning10 = False
	if percentage_int > 20 and charging and warning20: warning20 = False

	if percentage_int < 80 and not charging and warning80: warning80 = False
	if percentage_int < 90 and not charging and warning90: warning90 = False

	if 0 <= percentage_int <= 5 and not charging and not warning5:
		notification.notify(title="Phone Power Critical", message="5% power left, connect charger", app_name="phone_battery_indicator", app_icon=full_asset_path(BATTERY_ICONS["empty"]))
		warning5 = True
	elif 5 <= percentage_int <= 10 and not charging and not warning10:
		notification.notify(title="Phone Power Low", message="10% power left, connect charger", app_name="phone_battery_indicator", app_icon=full_asset_path(BATTERY_ICONS["red"]))
		warning10 = True
	elif 10 <= percentage_int <= 20 and not charging and not warning20:
		notification.notify(title="Phone Power Low", message="20% power, charge to reduce battery stress", app_name="phone_battery_indicator", app_icon=full_asset_path(BATTERY_ICONS["red"]))
		warning20 = True
	elif 89 >= percentage_int >= 80 and charging and not warning80:
		notification.notify(title="Phone Power High", message="80% power, disconnect to reduce battery stress", app_name="phone_battery_indicator", app_icon=full_asset_path(BATTERY_ICONS["green"]))
		warning80 = True
	elif 100 >= percentage_int >= 90 and charging and not warning90:
		notification.notify(title="Phone Power Very High", message="90% power, disconnect to reduce battery stress", app_name="phone_battery_indicator", app_icon=full_asset_path(BATTERY_ICONS["full"]))
		warning90 = True


def handle_update_button(event_src): update_indicator(event_src)
def handle_quit_button(event_src):	Gtk.main_quit()


def auto_update():
	update_indicator(None)
	GLib.timeout_add(30000, auto_update)


def build_menu(tooltip):
	menu = Gtk.Menu()

	item_title = Gtk.ImageMenuItem(label=tooltip)
	menu.append(item_title)

	menu.append(Gtk.SeparatorMenuItem())

	item_update = Gtk.MenuItem(label="Update")
	item_update.connect("activate", handle_update_button)
	menu.append(item_update)

	item_quit = Gtk.MenuItem(label="Quit")
	item_quit.connect("activate", handle_quit_button)
	menu.append(item_quit)

	menu.show_all()
	return menu


if __name__ == "__main__":
	APPINDICATOR_ID = "phone-battery-indicator"
	INDICATOR = AppIndicator3.Indicator.new(APPINDICATOR_ID, full_asset_path(BATTERY_ICONS["empty"]), AppIndicator3.IndicatorCategory.HARDWARE)
	INDICATOR.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
	INDICATOR.set_title("Phone Battery Indicator")
	auto_update()

	Gtk.main()

