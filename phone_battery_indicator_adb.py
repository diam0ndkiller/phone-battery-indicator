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





CONFIG = {
	"show_critical_warnings": True, # Show warnings at 10% and 5% battery
	"show_health_warnings": True, # Show reminders at 20%, 80% and 90% battery to reduce hardware battery stress
}





BATTERY_STATES_BY_DESCRIPTION = {"unavailable": "-1", "charging": "2", "discharging": "3", "halted": "4", "full": "5"}
BATTERY_STATES_BY_ID = {v: k for k, v in BATTERY_STATES_BY_DESCRIPTION.items()}
BATTERY_ICONS = {"empty": "assets/battery_empty.png",
				 "red": "assets/battery_red.png",
				 "yellow": "assets/battery_yellow.png",
				 "green": "assets/battery_green.png",
				 "red_charging": "assets/battery_red_charging.png",
				 "yellow_charging": "assets/battery_yellow_charging.png",
				 "green_charging": "assets/battery_green_charging.png",
				 "red_shield": "assets/battery_red_shield.png",
				 "green_shield": "assets/battery_green_shield.png",
				 "full": "assets/battery_full.png"}

CRITICAL_WARNINGS = [{"minimum": 0, "maximum": 5, "icon": BATTERY_ICONS["empty"], "reset": "above", "state": BATTERY_STATES_BY_DESCRIPTION["discharging"],
					  	"title": "Battery level critical.", "message": "5% power left. Connect charger.", "warned": False},
					 {"minimum": 5, "maximum": 10, "icon": BATTERY_ICONS["red"], "reset": "above", "state": BATTERY_STATES_BY_DESCRIPTION["discharging"],
	   					"title": "Battery level low.", "title": "10% power left. Connect charger.", "warned": False}]

HEALTH_WARNINGS = [{"minimum": 10, "maximum": 20, "icon": BATTERY_ICONS["red_shield"], "reset": "above", "state": BATTERY_STATES_BY_DESCRIPTION["discharging"],
						"title": "Battery level low.", "message": "20% power left. Connect charger to reduce battery stress.", "warned": False},
				   {"minimum": 80, "maximum": 90, "icon": BATTERY_ICONS["green_shield"], "reset": "below", "state": BATTERY_STATES_BY_DESCRIPTION["discharging"],
						"title": "Battery level high.", "message": "80% power. Disconnect to reduce battery stress.", "warned": False},
				   {"minimum": 90, "maximum": 100, "icon": BATTERY_ICONS["green_shield"], "reset": "below", "state": BATTERY_STATES_BY_DESCRIPTION["charging"],
						"title": "Battery level very high.", "message": "90% power. Disconnect to reduce battery stress.", "warned": False}]



def get_battery_info(): return subprocess.getoutput(["./get_phone_battery_adb.py"])
def full_asset_path(path: str): return f"{workdir}/{path}"


def battery_icon_path(state: str, percentage: int):
	if state == BATTERY_STATES_BY_DESCRIPTION["full"]:
		return BATTERY_ICONS["full"]
	
	elif state == BATTERY_STATES_BY_DESCRIPTION["halted"]:
		return BATTERY_ICONS["green_shield"]
	
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


def handle_warnings(percentage: int, state: str):
	global CRITICAL_WARNINGS, HEALTH_WARNINGS

	if CONFIG["show_critical_warnings"]:
		for warning in CRITICAL_WARNINGS:
			if not warning["warned"] and state == warning["state"] and warning["minimum"] <= percentage <= warning["maximum"]:
				post_notification(warning["icon"], warning["title"], warning["message"])
				warning["warned"] = True
				break
		
		for warning in CRITICAL_WARNINGS:
			if warning["reset"] == "above":
				if percentage > warning["maximum"]: warning["warned"] = False
			elif warning["reset"] == "below":
				if percentage < warning["minimum"]: warning["warned"] = False


	if CONFIG["show_health_warnings"]:
		for warning in HEALTH_WARNINGS:
			if not warning["warned"] and state == warning["state"] and warning["minimum"] <= percentage <= warning["maximum"]:
				post_notification(warning["icon"], warning["title"], warning["message"])
				warning["warned"] = True
				break
		
		for warning in HEALTH_WARNINGS:
			if warning["reset"] == "above":
				if percentage > warning["maximum"]: warning["warned"] = False
			elif warning["reset"] == "below":
				if percentage < warning["minimum"]: warning["warned"] = False


def post_notification(icon, title, message): notification.notify(title=title, message=message, app_name="phone_battery_indicator", app_icon=full_asset_path(icon))



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

