from config import (
    COLOR_PRIMARY, COLOR_ACCENT1, COLOR_ACCENT2, 
    COLOR_TEXT, COLOR_CARD, BORDER_RADIUS
)

def get_stylesheet():
    """Return global stylesheet untuk aplikasi"""
    stylesheet = f"""
    * {{
        margin: 0;
        padding: 0;
        border: none;
    }}

    QMainWindow {{
        background-color: {COLOR_PRIMARY};
        color: {COLOR_TEXT};
    }}

    QWidget {{
        background-color: {COLOR_PRIMARY};
        color: {COLOR_TEXT};
    }}

    /* PUSH BUTTON */
    QPushButton {{
        background-color: {COLOR_ACCENT1};
        color: {COLOR_TEXT};
        border: none;
        border-radius: {BORDER_RADIUS}px;
        padding: 10px 20px;
        font-weight: bold;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background-color: {COLOR_ACCENT2};
    }}

    QPushButton:pressed {{
        background-color: {COLOR_ACCENT1};
        opacity: 0.8;
    }}

    /* LINE EDIT */
    QLineEdit {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border: 2px solid {COLOR_ACCENT1};
        border-radius: {BORDER_RADIUS}px;
        padding: 8px 12px;
        font-size: 12px;
    }}

    QLineEdit:focus {{
        border: 2px solid {COLOR_ACCENT2};
    }}

    QLineEdit::placeholder {{
        color: #666666;
    }}

    /* LABEL */
    QLabel {{
        color: {COLOR_TEXT};
        background-color: transparent;
        font-size: 12px;
    }}

    /* TABLE WIDGET */
    QTableWidget {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_ACCENT1};
        border-radius: {BORDER_RADIUS}px;
        gridline-color: {COLOR_ACCENT1};
    }}

    QTableWidget::item {{
        padding: 5px;
        border: none;
    }}

    QTableWidget::item:selected {{
        background-color: {COLOR_ACCENT1};
    }}

    QHeaderView::section {{
        background-color: {COLOR_ACCENT1};
        color: {COLOR_TEXT};
        padding: 8px;
        border: none;
        font-weight: bold;
    }}

    /* SCROLL BAR */
    QScrollBar:vertical {{
        background-color: {COLOR_CARD};
        width: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {COLOR_ACCENT1};
        border-radius: 6px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background-color: {COLOR_ACCENT2};
    }}

    QScrollBar:horizontal {{
        background-color: {COLOR_CARD};
        height: 12px;
        border-radius: 6px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {COLOR_ACCENT1};
        border-radius: 6px;
        min-width: 20px;
    }}

    QScrollBar::handle:horizontal:hover {{
        background-color: {COLOR_ACCENT2};
    }}

    /* COMBO BOX */
    QComboBox {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border: 2px solid {COLOR_ACCENT1};
        border-radius: {BORDER_RADIUS}px;
        padding: 8px 12px;
        font-size: 12px;
    }}

    QComboBox:focus {{
        border: 2px solid {COLOR_ACCENT2};
    }}

    QComboBox::drop-down {{
        border: none;
    }}

    QComboBox QAbstractItemView {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_ACCENT1};
        selection-background-color: {COLOR_ACCENT1};
    }}

    /* SPIN BOX */
    QSpinBox {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border: 2px solid {COLOR_ACCENT1};
        border-radius: {BORDER_RADIUS}px;
        padding: 5px;
        font-size: 12px;
    }}

    QSpinBox::up-button, QSpinBox::down-button {{
        background-color: {COLOR_ACCENT1};
        border: none;
        width: 20px;
    }}

    QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
        background-color: {COLOR_ACCENT2};
    }}

    /* FRAME */
    QFrame {{
        background-color: transparent;
        border: none;
    }}

    /* DIALOG */
    QDialog {{
        background-color: {COLOR_PRIMARY};
    }}

    /* MENU BAR */
    QMenuBar {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border: none;
    }}

    QMenuBar::item:selected {{
        background-color: {COLOR_ACCENT1};
    }}

    QMenu {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_ACCENT1};
    }}

    QMenu::item:selected {{
        background-color: {COLOR_ACCENT1};
    }}

    /* SPLITTER */
    QSplitter::handle {{
        background-color: {COLOR_ACCENT1};
    }}

    QSplitter::handle:hover {{
        background-color: {COLOR_ACCENT2};
    }}

    /* STATUS BAR */
    QStatusBar {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border-top: 1px solid {COLOR_ACCENT1};
    }}

    /* TEXT EDIT */
    QTextEdit {{
        background-color: {COLOR_CARD};
        color: {COLOR_TEXT};
        border: 2px solid {COLOR_ACCENT1};
        border-radius: {BORDER_RADIUS}px;
        padding: 8px;
        font-size: 11px;
    }}

    QTextEdit:focus {{
        border: 2px solid {COLOR_ACCENT2};
    }}
    """
    return stylesheet
