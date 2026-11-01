import json
import os
NOTES_FOLDER = os.path.join(os.path.expanduser("~"), ".dayos")
NOTES_FILE = os.path.join(NOTES_FOLDER, "notes.json")

def load_notes():
    try:
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            notes_data = json.load(f)
        return notes_data if isinstance(notes_data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        #---- if file is damaged, keep a copy instead of overwriting it later ---
        backup = NOTES_FILE + ".corrupt"
        os.replace(NOTES_FILE, backup)
        return []

def save_notes(notes):
    os.makedirs(NOTES_FOLDER, exist_ok=True)
    temp_path = NOTES_FILE + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    os.replace(temp_path, NOTES_FILE)
