# ייבוא כל הספריות הנדרשות
from cryptography.fernet import Fernet, InvalidToken  # Fernet להצפנה/פענוח AES-256

def decrypt_log(file_path, key):
    """
    מפענח את קובץ הלוג המוצפן שורה אחר שורה.
    מחזיר את התוכן המפוענח כמחרוזת אחת.
    """
    # יוצר אובייקט פענוח עם המפתח שסופק
    cipher = Fernet(key.encode('utf-8'))
    
    # רשימה לשמירת כל השורות המפוענחות בהצלחה
    decrypted_lines = []
    
    try:
        # פותח את קובץ הלוג המוצפן לקריאה
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return ""
    except Exception as e:
        print(f"Error opening file: {e}")
        return ""

    # עובר על כל שורה בקובץ
    for i, line in enumerate(lines, 1):
        line = line.strip()  # מנקה רווחים, שורות חדשות וכו'
        if not line:         # אם השורה ריקה – מדלג
            continue
        
        try:
            # מפענח את השורה (Fernet מצפה לבייטים)
            decrypted = cipher.decrypt(line.encode('utf-8')).decode('utf-8')
            decrypted_lines.append(decrypted)
        except InvalidToken:
            # השורה לא תקינה (לא מוצפנת או פגומה)
            print(f"Line {i} is invalid (not a valid Fernet token) - skipping: {line[:20]}...")
        except Exception as e:
            # כל שגיאת פענוח אחרת
            print(f"Decryption error on line {i}: {e} - skipping")

    # אם לא הצלחנו לפענח אף שורה
    if not decrypted_lines:
        print("No valid lines could be decrypted.")
        return ""

    # מחבר את כל השורות המפוענחות עם שורה חדשה
    return "\n".join(decrypted_lines)

if __name__ == "__main__":
    print("Encrypted Log Decryptor (AES)\n")
    
    # בקשת נתיב לקובץ הלוג המוצפן
    log_file = input("Path to encrypted log file: ").strip().strip('"').strip("'")
    
    # בקשת מפתח ההצפנה
    key = input("Encryption key (copy exactly): ").strip()
    
    # בקשת נתיב לשמירת הפלט המפוענח (אופציונלי)
    output_file = input("Path to save decrypted output (e.g. D:\\decoded_log.txt) or press Enter to skip: ").strip().strip('"').strip("'")    
    # מבצע את הפענוח
    decrypted = decrypt_log(log_file, key)
    
    if decrypted:
        # מציג את הלוג המפוענח על המסך
        print("\nDecrypted log:\n" + "-"*60)
        print(decrypted)
        print("-"*60)
        
        # שומר לקובץ אם ניתן נתיב
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(decrypted)
                print(f"\nDecrypted output successfully saved to: {output_file}")
            except Exception as e:
                print(f"Error saving to file: {e}")
        else:
            print("\nOutput not saved to file (no path provided).")
    else:
        print("Decryption failed - check path and key.")