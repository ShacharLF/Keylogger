# Keylogger

Keylogger for Windows - Learning project with stealth mode and optional AES encryption.
For educational purposes only.

A simple educational keylogger written in Python for learning purposes.  
It records keystrokes, active window titles, and saves the output in an encrypted format.

**Educational Use Only**  
This tool is intended **for educational and research purposes only**.  
Using it on computers without explicit permission may violate privacy laws (including Israel's Privacy Protection Law and Computer Law).

---

## Features

- Keystroke logging (Keylogger)
- Records active window titles
- Clean and readable English output
- Stealth mode (runs without console window)
- Periodic saving + immediate save on Enter
- Easy stop with hotkey: `Ctrl + Alt + Q`
- Encrypted log (AES-256) - optional version available
- Separate decryptor tool

---

## Files

- `Keylogger.py` — Main keylogger (English output)
- `decryptor.py` — Tool to decrypt the log

---

## How to Compile to EXE

## 1. Install dependencies
cmd
python -m pip install pynput cryptography pyinstaller

Compile (Recommended command)

"python -m PyInstaller --onefile --noconsole --clean --hidden-import=pynput.keyboard._win32 --hidden-import=pynput.keyboard.win32 --hidden-import=pynput._util.win32 Keylogger.py"

Usage

Copy the .exe file to the target machine
Run the executable (double click)
The program will run silently in the background (no window)
All keystrokes will be logged to:

"C:\Users\<Username>\AppData\Roaming\Microsoft\Windows\Templates\update_history.log"

To stop the keylogger — press Ctrl + Alt + Q

Decryption (If Encrypted Version Used)

Run decryptor.py or the compiled decryptor
Enter the path to the encrypted log file
Enter the encryption key
Choose where to save the decrypted log (optional)


##Important Notes

This project was created for educational purposes only
Do not use on computers without proper authorization
Recommended to test only in virtual machines (VMs)
The author is not responsible for any misuse of this code


###License
This project is for educational purposes only.
Use at your own risk and responsibility.
