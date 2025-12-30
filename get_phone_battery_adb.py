#!/bin/python3
import os
import subprocess

with open("phone_ips.txt", "r") as file: phone_ips = file.read().split("\n")

o=""
for ip in phone_ips:
	try:
		if ip != "" and not "failed" in subprocess.check_output(f"adb connect {ip}:5542", shell=True).decode("utf-8"):
			o = subprocess.check_output(f"echo {ip} && adb -s {ip}:5542 shell dumpsys battery", shell=True).decode("utf-8")
			break
	except: continue
print(o)
with open("battery_data.txt", "w") as file: file.write(o)
