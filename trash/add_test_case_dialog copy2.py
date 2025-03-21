import sys
import pytest
import io
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QDialog, QFormLayout, QTextEdit, QCompleter
from PyQt5.QtCore import Qt

class AddTestCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置对话框标题和大小
        self.setWindowTitle("Add New Test Case")
        self.setGeometry(200, 200, 400, 400)  # 增加高度以适应新输入项

        # 创建表单布局
        layout = QFormLayout()

        # 创建输入字段
        self.test_case_name = QLineEdit(self)
        self.test_case_name.setPlaceholderText("Test Case Name")
        layout.addRow("Test Case Name:", self.test_case_name)

        self.test_case_description = QTextEdit(self)
        self.test_case_description.setPlaceholderText("Test Case Description")
        layout.addRow("Test Case Description:", self.test_case_description)

        # MySQL配置项
        self.mysql_host = QLineEdit(self)
        self.mysql_host.setPlaceholderText("MySQL Host")
        layout.addRow("MySQL Host:", self.mysql_host)

        self.mysql_user = QLineEdit(self)
        self.mysql_user.setPlaceholderText("MySQL User")
        layout.addRow("MySQL User:", self.mysql_user)

        self.mysql_password = QLineEdit(self)
        self.mysql_password.setEchoMode(QLineEdit.Password)  # 密码框
        self.mysql_password.setPlaceholderText("MySQL Password")
        layout.addRow("MySQL Password:", self.mysql_password)

        self.mysql_database = QLineEdit(self)
        self.mysql_database.setPlaceholderText("MySQL Database")
        layout.addRow("MySQL Database:", self.mysql_database)

        self.test_case_code = QTextEdit(self)
        self.test_case_code.setPlaceholderText("Test Case Code")
        layout.addRow("Test Case Code:", self.test_case_code)
        self.test_case_code.setAcceptRichText(False)  # 只接受纯文本

        # 添加按钮
        self.run_button = QPushButton("Run Test Case", self)
        layout.addWidget(self.run_button)

        self.save_button = QPushButton("Save Test Case", self)
        layout.addWidget(self.save_button)

        # 绑定按钮
        self.run_button.clicked.connect(self.run_test_case)  # 运行测试用例
        self.save_button.clicked.connect(self.add_test_case)  # 保存测试用例

        self.setLayout(layout)

    def run_test_case(self):
        # 获取输入的测试用例代码
        code = self.test_case_code.toPlainText()

        # 获取MySQL配置
        mysql_config = {
            'host': self.mysql_host.text(),
            'user': self.mysql_user.text(),
            'password': self.mysql_password.text(),
            'database': self.mysql_database.text()
        }

        # 将mysql_config作为参数传递给测试函数
        self.run_pytest(code, mysql_config)
        # result = self.run_pytest(code, mysql_config)

        # # 打印或显示结果
        # print(result)
        # from PyQt5.QtWidgets import QMessageBox
        # QMessageBox.information(self, "Test Result", result)

    def run_pytest(self, test_code, mysql_config):
        """
        使用pytest运行测试用例，并将MySQL配置作为参数传递给测试用例
        """
        # 生成一个临时的测试文件
        test_code_filename = 'test_case.py'
        with open(test_code_filename, 'w') as f:
            f.write(test_code)

        try:
            # 使用 pytest.main() 执行测试
            pytest.main([test_code_filename])
        except Exception as e:
            return f"Error executing test case: {str(e)}"

        # # 设置 pytest 捕获输出流
        # from pytest import capture_stdout

        # result_output = capture_stdout()

        # try:
        #     # 使用 pytest.main() 执行测试
        #     pytest.main([test_code_filename])
        # except Exception as e:
        #     return f"Error executing test case: {str(e)}"

        # # 返回捕获的输出
        # return result_output.getvalue()

    def add_test_case(self):
        # 获取输入的测试用例名称和描述
        name = self.test_case_name.text()
        description = self.test_case_description.toPlainText()
        code = self.test_case_code.toPlainText()

        if name and description:
            self.accept()  # 关闭对话框并返回
            # 把数据传递给父窗口
            self.parent().add_test_case_to_db(name, description, code)
