import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox
import sqlite3
from add_test_case_dialog import AddTestCaseDialog  # 导入 AddTestCaseDialog 类

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

        # 创建添加按钮
        self.add_button = QPushButton("Add Test Case", self)
        layout.addWidget(self.add_button)

        # 创建表格
        self.table = QTableWidget(self)
        self.table.setRowCount(0)
        self.table.setColumnCount(4)  # 添加第四列用于删除按钮
        self.table.setHorizontalHeaderLabels(["Test Case ID", "Test Case Name", "Description", "Action"])
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
        # 从数据库中加载所有测试用例并显示在表格中
        self.cursor.execute('SELECT * FROM test_cases')
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row[1]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[2]))

            # 添加删除按钮
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, row_idx=row_idx: self.delete_test_case(row_idx))
            self.table.setCellWidget(row_idx, 3, delete_button)

    def show_add_test_case_dialog(self):
        dialog = AddTestCaseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 如果对话框返回 Accept（即点击了确认按钮），则刷新表格
            self.load_test_cases()

    def add_test_case_to_db(self, name, description):
        # 将数据插入数据库
        self.cursor.execute('INSERT INTO test_cases (name, description) VALUES (?, ?)', (name, description))
        self.conn.commit()

    def delete_test_case(self, row_idx):
        # 获取当前行的 Test Case ID
        test_case_id = self.table.item(row_idx, 0).text()

        # 确认删除操作
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Test Case ID {test_case_id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 从数据库中删除记录
            self.cursor.execute('DELETE FROM test_cases WHERE id = ?', (test_case_id,))
            self.conn.commit()
            self.load_test_cases()  # 刷新表格


