#!/bin/python3

import subprocess

# Function to send text input to the Android phone
def send_text_input(input_text):
    adb_command = f"adb shell input text '{input_text}'"
    subprocess.run(adb_command, shell=True)

# Function to send key events to the Android phone
def send_key_event(keycode):
    adb_command = f"adb shell input keyevent {keycode}"
    subprocess.run(adb_command, shell=True)

# Main loop to continuously read and send user input
while True:
    user_input = input("Enter text, 'Enter' for Enter key, 'Backspace' for Backspace, 'Space' for Space, 'Ctrl+C' for Ctrl+C, or 'exit' to quit: ")
    if user_input.lower() == "exit":
        break
    elif user_input.lower() == "enter":
        send_key_event(66)  # Send Enter key event
    elif user_input.lower() == "backspace":
        send_key_event(67)  # Send Backspace key event
    elif user_input.lower() == "space":
        send_key_event(62)  # Send Space key event
    elif user_input.lower() == "ctrl+c":
        send_key_event(17)  # Send Ctrl+C key event
    else:
        # If not a special key, send the text as input
        send_text_input(user_input)

print("Script exited.")
