import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QDialog, QFormLayout, QTextEdit, QCompleter
from PyQt5.QtCore import Qt

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
        self.test_case_code.setAcceptRichText(False)  # 只接受纯文本


        # 添加按钮
        self.add_button = QPushButton("Add Test Case", self)
        layout.addWidget(self.add_button)

        # 绑定按钮
        self.add_button.clicked.connect(self.add_test_case)

        self.setLayout(layout)

    def add_test_case(self):
        # 获取输入的测试用例名称和描述
        name = self.test_case_name.text()
        description = self.test_case_description.toPlainText()
        code = self.test_case_code.toPlainText()

        if name and description:
            self.accept()  # 关闭对话框并返回
            self.parent().add_test_case_to_db(name, description, code)  # 把数据传递给父窗口