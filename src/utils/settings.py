# src/utils/settings.py
import json
import os

SETTINGS_FILE = "user_settings.json"

def save_settings(settings):
    """Save settings dictionary to JSON file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def load_settings():
    """Load settings from JSON file, return empty dict if not found."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_stay_connected(email, password):
    """Save credentials and flag for auto-login."""
    settings = load_settings()
    settings['stay_connected'] = True
    settings['email'] = email
    settings['password'] = password
    save_settings(settings)

def clear_stay_connected():
    """Remove auto-login credentials and flag."""
    settings = load_settings()
    settings.pop('stay_connected', None)
    settings.pop('email', None)
    settings.pop('password', None)
    save_settings(settings)

def get_stay_connected():
    """Return (stay_connected_flag, email, password) or (False, None, None)."""
    settings = load_settings()
    if settings.get('stay_connected', False):
        return True, settings.get('email'), settings.get('password')
    return False, None, None