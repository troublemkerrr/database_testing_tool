from test_case_manager import TestCaseManager
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QDialog, QFormLayout, QTextEdit, QCompleter
from PyQt5.QtCore import Qt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestCaseManager()
    sys.exit(app.exec_())