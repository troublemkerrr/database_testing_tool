import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QDialog, QFormLayout, QTextEdit, QCompleter
from PyQt5.QtCore import Qt
import sqlite3
from add_test_case_dialog import AddTestCaseDialog

class TestCaseManager(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化窗口
        self.setWindowTitle("Test Case Manager")
        self.setGeometry(100, 100, 600, 400)

        # 创建布局
        layout = QVBoxLayout()

        # 创建输入字段（支持查找/过滤）
        self.test_case_name = QLineEdit(self)
        self.test_case_name.setPlaceholderText("Search Test Case by Name")
        self.test_case_name.textChanged.connect(self.filter_test_cases)  # 文本变化时过滤
        self.test_case_name.returnPressed.connect(self.on_return_pressed)  # 监听回车键
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
        self.add_button.clicked.connect(self.show_add_test_case_dialog)

        self.setLayout(layout)
        self.show()

        # 初始化数据库
        self.conn = sqlite3.connect('test_cases.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS test_cases (id INTEGER PRIMARY KEY, name TEXT, description TEXT)''')
        self.conn.commit()

        self.load_test_cases()

        # 使用QCompleter实现自动补全
        self.create_autocomplete()

    def load_test_cases(self):
        self.cursor.execute('SELECT * FROM test_cases')
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row[1]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[2]))

    def show_add_test_case_dialog(self):
        dialog = AddTestCaseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 如果对话框返回 Accept（即点击了确认按钮），则刷新表格
            self.load_test_cases()

    def add_test_case_to_db(self, name, description):
        # 将数据插入数据库
        self.cursor.execute('INSERT INTO test_cases (name, description) VALUES (?, ?)', (name, description))
        self.conn.commit()

    def filter_test_cases(self):
        # 根据输入框内容进行模糊匹配（实时过滤）
        search_text = self.test_case_name.text()
        self.cursor.execute("SELECT * FROM test_cases WHERE name LIKE ?", ('%' + search_text + '%',))
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row[1]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[2]))

    def on_return_pressed(self):
        # 用户按下回车键后进行精确匹配
        search_text = self.test_case_name.text()
        self.cursor.execute("SELECT * FROM test_cases WHERE name = ?", (search_text,))
        rows = self.cursor.fetchall()

        if not rows:  # 如果没有精确匹配的项，进行模糊匹配
            self.filter_test_cases()
        else:
            self.table.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(row[1]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(row[2]))

    def create_autocomplete(self):
        # 获取所有测试用例名称
        self.cursor.execute("SELECT name FROM test_cases")
        names = [row[0] for row in self.cursor.fetchall()]

        # 设置自动补全器
        completer = QCompleter(names, self)
        self.test_case_name.setCompleter(completer)