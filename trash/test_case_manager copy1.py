import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QDialog, QFormLayout, QTextEdit, QHBoxLayout
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

        # 创建输入字段（支持查找/过滤）
        self.test_case_name = QLineEdit(self)
        self.test_case_name.setPlaceholderText("Search Test Case by Name")
        self.test_case_name.textChanged.connect(self.filter_test_cases)  # 文本变化时过滤
        layout.addWidget(self.test_case_name)

        # 创建添加按钮
        self.add_button = QPushButton("Add Test Case", self)
        layout.addWidget(self.add_button)

        # 创建表格
        self.table = QTableWidget(self)
        self.table.setRowCount(0)
        
        self.table.setColumnCount(4) 
        self.table.setHorizontalHeaderLabels(["Test Case ID", "Test Case Name", "Description", "Actions"])
        
        # 设置Actions列的宽度（比如设置为 200）
        self.table.setColumnWidth(3, 200)

        layout.addWidget(self.table)

        # 绑定按钮
        self.add_button.clicked.connect(self.show_add_test_case_dialog)

        self.setLayout(layout)
        self.show()

        # 初始化数据库
        self.test_case_conn = sqlite3.connect('test_cases.db')
        self.test_case_cursor = self.test_case_conn.cursor()
        self.test_case_cursor.execute('''CREATE TABLE IF NOT EXISTS test_cases (id INTEGER PRIMARY KEY, name TEXT, description TEXT, code TEXT)''')
        self.test_case_conn.commit()
        self.load_test_cases()

    def load_test_cases(self):
        # 从数据库中加载所有测试用例并显示在表格中
        self.test_case_cursor.execute('SELECT * FROM test_cases')
        rows = self.test_case_cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row[1]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[2]))

            # 添加操作按钮（查看、修改、删除）
            actions_layout = QHBoxLayout()

            # 添加查看按钮
            view_button = QPushButton("View")
            view_button.clicked.connect(lambda checked, row_idx=row_idx: self.view_test_case(row_idx))
            actions_layout.addWidget(view_button)

            # 添加修改按钮
            modify_button = QPushButton("Modify")
            modify_button.clicked.connect(lambda checked, row_idx=row_idx: self.modify_test_case(row_idx))
            actions_layout.addWidget(modify_button)

            # 添加删除按钮
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, row_idx=row_idx: self.delete_test_case(row_idx))
            actions_layout.addWidget(delete_button)

            # 将操作按钮放到同一列
            action_widget = QWidget()
            action_widget.setLayout(actions_layout)
            self.table.setCellWidget(row_idx, 3, action_widget)  # 在“Actions”列中放置操作按钮

    def show_add_test_case_dialog(self):
        dialog = AddTestCaseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # 如果对话框返回 Accept（即点击了确认按钮），则刷新表格
            self.load_test_cases()

    def add_test_case_to_db(self, name, description, code):
        # 将数据插入数据库
        self.test_case_cursor.execute('INSERT INTO test_cases (name, description, code) VALUES (?, ?, ?)', (name, description, code))
        self.test_case_conn.commit()

    def delete_test_case(self, row_idx):
        # 获取当前行的 Test Case ID
        test_case_id = self.table.item(row_idx, 0).text()

        # 确认删除操作
        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete Test Case ID {test_case_id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 从数据库中删除记录
            self.test_case_cursor.execute('DELETE FROM test_cases WHERE id = ?', (test_case_id,))
            self.test_case_conn.commit()

            search_text = self.test_case_name.text()  # 获取搜索框中的文本
            if search_text:
                self.filter_test_cases() # 根据搜索条件重新加载表格数据
            else:
                self.load_test_cases()

    def view_test_case(self, row_idx):
        # 获取当前行的 Test Case ID
        test_case_id = self.table.item(row_idx, 0).text()
        
        # 从数据库中查询该记录的详细信息
        self.test_case_cursor.execute('SELECT * FROM test_cases WHERE id = ?', (test_case_id,))
        test_case = self.test_case_cursor.fetchone()

        # 弹出对话框显示详细信息
        QMessageBox.information(self, "Test Case Details", 
                                f"Test Case ID: {test_case[0]}\n"
                                f"Name: {test_case[1]}\n"
                                f"Description: {test_case[2]}\n"
                                f"Code: {test_case[3]}")

    def modify_test_case(self, row_idx):
        # 获取当前行的 Test Case ID
        test_case_id = self.table.item(row_idx, 0).text()
        
        # 从数据库中查询该记录的详细信息
        self.test_case_cursor.execute('SELECT * FROM test_cases WHERE id = ?', (test_case_id,))
        test_case = self.test_case_cursor.fetchone()

        # 弹出修改对话框
        modify_dialog = ModifyTestCaseDialog(self, test_case)
        if modify_dialog.exec_() == QDialog.Accepted:
            # 如果对话框返回 Accept（即点击了确认按钮），则更新数据库并刷新表格
            search_text = self.test_case_name.text()  # 获取搜索框中的文本
            if search_text:
                self.filter_test_cases() # 根据搜索条件重新加载表格数据
            else:
                self.load_test_cases()

    def filter_test_cases(self):
        # 根据输入框内容进行模糊匹配（实时过滤）
        search_text = self.test_case_name.text()
        self.test_case_cursor.execute("SELECT * FROM test_cases WHERE name LIKE ?", ('%' + search_text + '%',))
        rows = self.test_case_cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row[0])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(row[1]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(row[2]))

            # 添加操作按钮（查看、修改、删除）
            actions_layout = QHBoxLayout()

            # 添加查看按钮
            view_button = QPushButton("View")
            view_button.clicked.connect(lambda checked, row_idx=row_idx: self.view_test_case(row_idx))
            actions_layout.addWidget(view_button)

            # 添加修改按钮
            modify_button = QPushButton("Modify")
            modify_button.clicked.connect(lambda checked, row_idx=row_idx: self.modify_test_case(row_idx))
            actions_layout.addWidget(modify_button)

            # 添加删除按钮
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, row_idx=row_idx: self.delete_test_case(row_idx))
            actions_layout.addWidget(delete_button)

            # 将操作按钮放到同一列
            action_widget = QWidget()
            action_widget.setLayout(actions_layout)
            self.table.setCellWidget(row_idx, 3, action_widget)  # 在“Actions”列中放置操作按钮

    def create_autocomplete(self):
        # 获取所有测试用例名称
        self.test_case_cursor.execute("SELECT name FROM test_cases")
        names = [row[0] for row in self.test_case_cursor.fetchall()]

        # 设置自动补全器
        completer = QCompleter(names, self)
        self.test_case_name.setCompleter(completer)

class ModifyTestCaseDialog(QDialog):
    def __init__(self, parent, test_case):
        super().__init__(parent)
        self.test_case_id = test_case[0]
        self.test_case_name = test_case[1]
        self.test_case_description = test_case[2]
        self.test_case_code = test_case[3]

        # 设置对话框标题和大小
        self.setWindowTitle("Modify Test Case")
        self.setGeometry(200, 200, 400, 300)

        # 创建表单布局
        layout = QFormLayout()

        # 创建输入字段
        self.name_input = QLineEdit(self)
        self.name_input.setText(self.test_case_name)
        layout.addRow("Test Case Name:", self.name_input)

        self.description_input = QTextEdit(self)
        self.description_input.setText(self.test_case_description)
        layout.addRow("Test Case Description:", self.description_input)

        self.code_input = QTextEdit(self)
        self.code_input.setText(self.test_case_code)
        layout.addRow("Test Case code:", self.code_input)

        # 添加按钮
        self.modify_button = QPushButton("Modify", self)
        layout.addWidget(self.modify_button)

        # 绑定按钮
        self.modify_button.clicked.connect(self.modify_test_case)

        self.setLayout(layout)

    def modify_test_case(self):
        # 获取输入的修改内容
        name = self.name_input.text()
        description = self.description_input.toPlainText()
        code = self.code_input.toPlainText()

        if name and description:
            # 更新数据库中的记录
            test_case_cursor = self.parent().test_case_cursor
            test_case_cursor.execute('UPDATE test_cases SET name = ?, description = ?, code = ? WHERE id = ?',
                           (name, description, code, self.test_case_id))
            self.parent().test_case_conn.commit()
            self.accept()  # 关闭对话框并返回
    

