import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QDialog, QFormLayout, QTextEdit
from PyQt5.QtCore import Qt
import sqlite3

class AddTestCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置对话框标题和大小
        self.setWindowTitle("Add New Test Case")
        self.setGeometry(200, 200, 400, 300)

        # 创建表单布局
        layout = QFormLayout()

        # 创建输入字段
        self.test_case_name = QLineEdit(self)
        self.test_case_name.setPlaceholderText("Test Case Name")
        layout.addRow("Test Case Name:", self.test_case_name)

        self.test_case_description = QTextEdit(self)
        self.test_case_description.setPlaceholderText("Test Case Description")
        layout.addRow("Test Case Description:", self.test_case_description)

        self.test_case_code = QTextEdit(self)
        self.test_case_code.setPlaceholderText("Test Case Code")
        layout.addRow("Test Case Code:", self.test_case_code)

        # 添加按钮
        self.add_button = QPushButton("Add Test Case", self)
        layout.addWidget(self.add_button)

        # 绑定按钮
        self.add_button.clicked.connect(self.add_test_case)

        self.setLayout(layout)

    def add_test_case(self):
        # 获取输入的测试用例名称和代码
        name = self.test_case_name.text()
        description = self.test_case_description.toPlainText()

        if name and description:
            self.accept()  # 关闭对话框并返回
            self.parent().add_test_case_to_db(name, description)  # 把数据传递给父窗口

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
        self.add_button.clicked.connect(self.show_add_test_case_dialog)

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

    def show_add_test_case_dialog(self):
        dialog = AddTestCaseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 如果对话框返回 Accept（即点击了确认按钮），则刷新表格
            self.load_test_cases()

    def add_test_case_to_db(self, name, description):
        # 将数据插入数据库
        self.cursor.execute('INSERT INTO test_cases (name, description) VALUES (?, ?)', (name, description))
        self.conn.commit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestCaseManager()
    sys.exit(app.exec_())
