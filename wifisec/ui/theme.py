"""QSS themes."""

THEMES = {
    "dev_cyan": {
        "accent": "#00c8d7",
        "bg": "#1b1e23",
        "panel": "#232830",
        "text": "#d7e2e8",
    },
    "hacker_red": {
        "accent": "#ff3b3b",
        "bg": "#1c1416",
        "panel": "#291b1e",
        "text": "#e8d7d7",
    },
    "neon_sunset": {
        "accent": "#ff6ec7",
        "bg": "#221a24",
        "panel": "#2d2231",
        "text": "#ead7e8",
    },
}

PADDING = {"comfortable": "10px", "compact": "5px"}


def build_qss(theme_name="dev_cyan", density="comfortable"):
    t = THEMES.get(theme_name, THEMES["dev_cyan"])
    p = PADDING.get(density, PADDING["comfortable"])
    return f"""
    QWidget {{ background: {t['bg']}; color: {t['text']}; font-size: 13px; }}
    QListWidget#sidebar {{
        background: {t['panel']}; border: none; outline: none;
        font-size: 14px; min-width: 190px; max-width: 240px;
    }}
    QListWidget#sidebar::item {{ padding: {p} {p}; }}
    QListWidget#sidebar::item:selected {{
        background: {t['accent']}; color: #10151a; border-radius: 6px;
    }}
    QPushButton {{
        background: {t['panel']}; border: 1px solid {t['accent']};
        border-radius: 6px; padding: {p};
    }}
    QPushButton:hover {{ background: {t['accent']}; color: #10151a; }}
    QPushButton:disabled {{ border-color: #555; color: #777; }}
    QLineEdit, QComboBox, QSpinBox, QCheckBox {{ padding: {p}; }}
    QTableWidget {{
        background: {t['panel']}; gridline-color: #3a4048;
        alternate-background-color: {t['bg']};
    }}
    QPlainTextEdit {{
        background: {t['panel']}; border: 1px solid #3a4048;
        font-family: Consolas, monospace;
    }}
    QLabel#banner {{ background: #4a3b00; color: #ffd34d; padding: {p}; border-radius: 4px; }}
    QLabel#page_title {{ font-size: 20px; font-weight: bold; color: {t['accent']}; }}
    """