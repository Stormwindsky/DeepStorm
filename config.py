import json
import os

CONFIG_FILE = "config.json"

# Default configuration values
DEFAULT_CONFIG = {
    "colors": {
        "background": "#FFFFFF",
        "button": "#0078D7",
        "button_text": "#FFFFFF",
        "chat_history_background": "#F0F0F0",
        "chat_history_border": "#CCCCCC",
        "user_input_background": "#FFFFFF",
        "user_input_border": "#CCCCCC"
    },
    "stream_mode": False,
    "model": "deepseek-r1:1.5b"  # Default model
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            # Merge default config with loaded config to ensure all keys exist
            return {**DEFAULT_CONFIG, **config}
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

def load_colors():
    config = load_config()
    return config["colors"]

def save_colors(colors):
    config = load_config()
    config["colors"] = colors
    save_config(config)

def load_stream_mode():
    config = load_config()
    return config["stream_mode"]

def save_stream_mode(stream_mode):
    config = load_config()
    config["stream_mode"] = stream_mode
    save_config(config)

def load_model():
    config = load_config()
    return config["model"]

def save_model(model):
    config = load_config()
    config["model"] = model
    save_config(config)