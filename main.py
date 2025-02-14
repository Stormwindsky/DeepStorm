import sys
import json
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextBrowser, QTextEdit,
    QPushButton, QHBoxLayout, QDialog, QFormLayout, QColorDialog, QRadioButton, QButtonGroup, QLineEdit
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

# Import functions from config.py
from config import load_colors, save_colors, load_stream_mode, save_stream_mode, load_model, save_model

# URL de l'API Ollama (à adapter selon votre configuration)
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def chat_with_deepseek(prompt, stream=False, model=None):
    if model is None:
        model = load_model()  # Use the saved model if none is provided

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Debugging: Print the raw response content
        print("Raw response content:", response.content)

        if stream:
            # Handle streaming response
            response_text = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        response_text += chunk.get("response", "")
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON chunk: {e}")
            return response_text
        else:
            # Handle non-streaming response
            response_json = response.json()
            return response_json.get("response", "Pas de réponse trouvée.")
    except requests.exceptions.RequestException as e:
        return f"Erreur de requête: {e}"
    except json.JSONDecodeError as e:
        return f"Erreur de décodage JSON: {e}"

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.setGeometry(200, 200, 400, 300)

        self.colors = load_colors()
        self.stream_mode = load_stream_mode()
        self.model = load_model()

        layout = QFormLayout()

        # Boutons pour sélectionner les couleurs
        self.background_button = self.create_color_button("Fond de l'application", self.colors["background"])
        self.button_color_button = self.create_color_button("Couleur du bouton", self.colors["button"])
        self.button_text_button = self.create_color_button("Couleur du texte du bouton", self.colors["button_text"])
        self.chat_history_background_button = self.create_color_button("Fond de l'historique du chat", self.colors["chat_history_background"])
        self.chat_history_border_button = self.create_color_button("Bordure de l'historique du chat", self.colors["chat_history_border"])
        self.user_input_background_button = self.create_color_button("Fond de la zone de saisie", self.colors["user_input_background"])
        self.user_input_border_button = self.create_color_button("Bordure de la zone de saisie", self.colors["user_input_border"])

        layout.addRow("Fond de l'application:", self.background_button)
        layout.addRow("Couleur du bouton:", self.button_color_button)
        layout.addRow("Couleur du texte du bouton:", self.button_text_button)
        layout.addRow("Fond de l'historique du chat:", self.chat_history_background_button)
        layout.addRow("Bordure de l'historique du chat:", self.chat_history_border_button)
        layout.addRow("Fond de la zone de saisie:", self.user_input_background_button)
        layout.addRow("Bordure de la zone de saisie:", self.user_input_border_button)

        # Ajouter des boutons radio pour choisir entre changer les couleurs et activer/désactiver le mode stream
        self.stream_mode_group = QButtonGroup(self)
        self.stream_mode_on = QRadioButton("Activer le mode stream")
        self.stream_mode_off = QRadioButton("Désactiver le mode stream")
        self.stream_mode_group.addButton(self.stream_mode_on)
        self.stream_mode_group.addButton(self.stream_mode_off)

        if self.stream_mode:
            self.stream_mode_on.setChecked(True)
        else:
            self.stream_mode_off.setChecked(True)

        layout.addRow("Mode Stream:", self.stream_mode_on)
        layout.addRow("", self.stream_mode_off)

        # Ajouter un champ de saisie pour le modèle
        self.model_input = QLineEdit(self.model)
        layout.addRow("Modèle:", self.model_input)

        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save_settings)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def create_color_button(self, label, initial_color):
        button = QPushButton()
        button.setText("Choisir une couleur")
        button.setStyleSheet(f"background-color: {initial_color};")
        button.selected_color = initial_color  # Stocker la couleur initiale
        button.clicked.connect(lambda: self.choose_color(button))
        return button

    def choose_color(self, button):
        color = QColorDialog.getColor()
        if color.isValid():
            button.selected_color = color.name()  # Mettre à jour la couleur sélectionnée
            button.setStyleSheet(f"background-color: {color.name()};")

    def save_settings(self):
        colors = {
            "background": self.background_button.selected_color,
            "button": self.button_color_button.selected_color,
            "button_text": self.button_text_button.selected_color,
            "chat_history_background": self.chat_history_background_button.selected_color,
            "chat_history_border": self.chat_history_border_button.selected_color,
            "user_input_background": self.user_input_background_button.selected_color,
            "user_input_border": self.user_input_border_button.selected_color
        }
        save_colors(colors)

        stream_mode = self.stream_mode_on.isChecked()
        save_stream_mode(stream_mode)

        model = self.model_input.text().strip()
        save_model(model)

        self.parent().apply_colors()
        self.parent().stream_mode = stream_mode
        self.parent().model = model
        self.close()

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeepStorm")
        self.setGeometry(100, 100, 800, 600)

        # Charger les couleurs, le mode stream et le modèle
        self.colors = load_colors()
        self.stream_mode = load_stream_mode()
        self.model = load_model()

        # Layout principal
        layout = QVBoxLayout()

        # Zone d'affichage des messages (QTextBrowser gère mieux le formatage)
        self.chat_history = QTextBrowser(self)
        self.chat_history.setFont(QFont("Segoe UI Emoji", 12))
        layout.addWidget(self.chat_history)

        # Zone d'entrée de l'utilisateur
        self.user_input_box = QTextEdit(self)
        self.user_input_box.setFixedHeight(80)
        self.user_input_box.setFont(QFont("Segoe UI Emoji", 12))
        layout.addWidget(self.user_input_box)

        # Bouton d'envoi
        button_layout = QHBoxLayout()
        self.send_button = QPushButton("✨", self)
        self.send_button.setFont(QFont("Segoe UI Emoji", 14, QFont.Weight.Bold))
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)

        # Bouton de configuration
        self.settings_button = QPushButton("⚙️", self)
        self.settings_button.setFont(QFont("Segoe UI Emoji", 14, QFont.Weight.Bold))
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Appliquer les couleurs après l'initialisation des widgets
        self.apply_colors()

    def apply_colors(self):
        self.setStyleSheet(f"background-color: {self.colors['background']};")
        self.chat_history.setStyleSheet(f"background-color: {self.colors['chat_history_background']}; border: 1px solid {self.colors['chat_history_border']}; padding: 5px;")
        self.user_input_box.setStyleSheet(f"background-color: {self.colors['user_input_background']}; border: 1px solid {self.colors['user_input_border']}; padding: 5px;")
        self.send_button.setStyleSheet(f"background-color: {self.colors['button']}; color: {self.colors['button_text']}; padding: 10px; border-radius: 5px;")
        self.settings_button.setStyleSheet(f"background-color: {self.colors['button']}; color: {self.colors['button_text']}; padding: 10px; border-radius: 5px;")

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def send_message(self):
        user_input = self.user_input_box.toPlainText().strip()
        if not user_input:
            return

        self.user_input_box.clear()
        self.chat_history.append(f"<b style='color:#0078D7;'>👤:</b> {user_input}")

        response = chat_with_deepseek(user_input, self.stream_mode, self.model)
        self.chat_history.append(f"<b style='color:#4CAF50;'>🤖:</b> {response}")

# Lancement de l'application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec())