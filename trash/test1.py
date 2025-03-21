import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel
from PyQt5.QtCore import Qt
import sqlite3

class TestCaseManager(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化窗口
        self.setWindowTitle("Test Case Manager")
        self.setGeometry(100, 100, 600, 400)

        # 创建布局
        layout = QVBoxLayout()

        # 创建输入字段
        self.test_case_name = QLineEdit(self)
        self.test_case_name.setPlaceholderText("Test Case Name")
        layout.addWidget(self.test_case_name)

        self.add_button = QPushButton("Add Test Case", self)
        layout.addWidget(self.add_button)

        # 创建表格
        self.table = QTableWidget(self)
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Test Case ID", "Test Case Name", "Description"])
        layout.addWidget(self.table)

        # 绑定按钮
        self.add_button.clicked.connect(self.add_test_case)

        self.setLayout(layout)
        self.show()

        # 初始化数据库
        self.conn = sqlite3.connect('test_cases.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS test_cases (id INTEGER PRIMARY KEY, name TEXT, description TEXT)''')
        self.conn.commit()
        self.load_test_cases()

    def load_test_cases(self):
        self.cursor.execute('SELECT * FROM test_cases')
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row[1]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[2]))

    def add_test_case(self):
        name = self.test_case_name.text()
        if name:
            self.cursor.execute('INSERT INTO test_cases (name, description) VALUES (?, ?)', (name, "Test description"))
            self.conn.commit()
            self.load_test_cases()
            self.test_case_name.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestCaseManager()
    sys.exit(app.exec_())
