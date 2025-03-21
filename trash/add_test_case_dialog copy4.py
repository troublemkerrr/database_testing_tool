import sys
import pytest
import io
import os
import textwrap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QDialog, QFormLayout, QTextEdit, QCompleter, QComboBox
from PyQt5.QtCore import Qt

class AddTestCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置对话框标题和大小
        self.setWindowTitle("Add New Test Case")
        self.setGeometry(200, 200, 400, 400)

        # 缓存：最多保存3个最近使用的配置
        self.mysql_config_cache = []

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

        # 配置选择下拉框
        self.config_combo = QComboBox(self)
        self.config_combo.addItem("Select Previous Configuration")
        self.load_cached_configs()  # 加载缓存的配置
        self.config_combo.currentIndexChanged.connect(self.load_selected_config)  # 选择配置时加载内容
        layout.addRow("Select Configuration:", self.config_combo)

        # 添加按钮
        self.save_button = QPushButton("Save Configuration", self)
        self.save_button.clicked.connect(self.save_mysql_config)  # 保存配置
        layout.addWidget(self.save_button)

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
        result = self.run_pytest(code, mysql_config)

        # 打印或显示结果
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Test Result", result)

    def run_pytest(self, test_code, mysql_config):
        """
        使用pytest运行测试用例，并将MySQL配置作为参数传递给测试用例
        """
        # 生成一个临时的测试文件
        test_code_filename = 'test_record/test_case.py'

        # 如果 test_record 目录不存在，则新建它
        if not os.path.exists(os.path.dirname(test_code_filename)):
            os.makedirs(os.path.dirname(test_code_filename))

        print(mysql_config)  # 检查字典内容

        # 使用 f-string 格式化配置
        mysql_config_str = f"""{{
            'host': '{mysql_config['host']}',  # MySQL 服务器地址
            'user': '{mysql_config['user']}',    # MySQL 用户名
            'password': '{mysql_config['password']}',  # MySQL 密码
            'database': '{mysql_config['database']}'    # 要连接的数据库
        }}
        """

        # 要写入的内容
        additional_code = f"""
        import pytest
        import mysql.connector

        # 配置你的 MySQL 数据库连接信息
        MYSQL_CONFIG = {mysql_config_str}

        # 创建一个连接 fixture
        @pytest.fixture(scope='module')
        def mysql_connection():
            \"\"\"创建并返回 MySQL 数据库连接\"\"\"
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            yield conn
            conn.close()  # 测试完成后关闭连接
        """

        # 使用 textwrap.dedent 去除多余的缩进
        additional_code = textwrap.dedent(additional_code)

        # 将额外的代码与测试代码合并
        full_test_code = additional_code + "\n" + test_code

        # 写入合并后的内容
        with open(test_code_filename, 'w') as f:
            f.write(full_test_code)


        # 创建一个内存中的文件来捕获输出
        result_output = io.StringIO()

        # 保存原来的stdout
        original_stdout = sys.stdout
        sys.stdout = result_output  # 将 stdout 重定向到 result_output

        # 保存原来的stderr
        original_stderr = sys.stderr
        sys.stderr = result_output  # 将 stderr 也重定向到 result_output

        try:
            # 使用 pytest.main() 执行测试
            pytest.main([test_code_filename])
        finally:
            # 恢复 stdout 和 stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        # 返回捕获的输出
        return result_output.getvalue()

    def add_test_case(self):
        # 获取输入的测试用例名称和描述
        name = self.test_case_name.text()
        description = self.test_case_description.toPlainText()
        code = self.test_case_code.toPlainText()

        if name and description:
            self.accept()  # 关闭对话框并返回
            # 把数据传递给父窗口
            self.parent().add_test_case_to_db(name, description, code)
    
    def load_cached_configs(self):
        """从缓存加载配置并添加到下拉框"""
        self.config_combo.clear()
        self.config_combo.addItem("Select Previous Configuration")
        for config in self.mysql_config_cache:
            self.config_combo.addItem(config['host'])  # 将主机名添加到下拉框

    def load_selected_config(self):
        """加载选择的配置到输入框"""
        selected_index = self.config_combo.currentIndex() - 1  # 去除第一个占位符项
        if selected_index >= 0:
            config = self.mysql_config_cache[selected_index]
            self.mysql_host.setText(config['host'])
            self.mysql_user.setText(config['user'])
            self.mysql_password.setText(config['password'])
            self.mysql_database.setText(config['database'])

    def save_mysql_config(self):
        """保存当前输入的配置并更新缓存"""
        config = {
            'host': self.mysql_host.text(),
            'user': self.mysql_user.text(),
            'password': self.mysql_password.text(),
            'database': self.mysql_database.text()
        }

        # 更新缓存：如果缓存中已有该配置，则删除，确保唯一
        if config not in self.mysql_config_cache:
            self.mysql_config_cache.insert(0, config)  # 插入到缓存的最前面
            if len(self.mysql_config_cache) > 3:
                self.mysql_config_cache.pop()  # 保证缓存最多保存3个配置

        # 更新下拉框
        self.load_cached_configs()

        # 可选择将配置保存到文件或数据库
        print("Configuration Saved:", config)

