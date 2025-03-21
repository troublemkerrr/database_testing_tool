import sys
import pytest
import io
import os
import textwrap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QDialog, QFormLayout, QTextEdit, QCompleter, QComboBox, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt
import sqlite3

class AddTestCaseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化数据库
        self.mysql_config_conn = sqlite3.connect('mysql_configs.db')
        self.mysql_config_cursor = self.mysql_config_conn.cursor()

        # 创建表格（如果表格已经存在，不会重新创建）
        self.mysql_config_cursor.execute('''CREATE TABLE IF NOT EXISTS mysql_configs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        host TEXT,
                        user TEXT,
                        password TEXT,
                        database TEXT)''')
        self.mysql_config_conn.commit()

        # 初始化预设测试代码数据库
        self.init_preset_base_test_db()
        self.init_preset_constraint_test_db()
        self.init_preset_transaction_test_db()

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

        # 配置选择下拉框
        self.config_combo = QComboBox(self)
        self.config_combo.addItem("Select Previous Configuration")
        self.load_cached_configs()  # 加载缓存的配置
        self.config_combo.currentIndexChanged.connect(self.load_selected_config)  # 选择配置时加载内容
        layout.addRow("Select Configuration:", self.config_combo)

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

        # 保存配置按钮
        self.save_config_button = QPushButton("Save Configuration", self)
        self.save_config_button.clicked.connect(self.save_mysql_config)  # 保存配置
        layout.addWidget(self.save_config_button)

        """初始化UI并根据数据库动态创建按钮 - base"""
        # 创建一个 QHBoxLayout 将按钮横向排列
        button_layout = QHBoxLayout()
        button_layout.addWidget(QLabel("Base test:"))  # 添加文本

        # 从数据库加载按钮名称并动态创建按钮
        button_names = self.load_button_names_from_db(self.preset_base_test_cursor)

        # 为每个按钮创建并连接事件
        for name in button_names:
            button = QPushButton(name, self)
            button.clicked.connect(lambda _, btn_name=name: self.handle_button_click(self.preset_base_test_cursor, btn_name))
            button_layout.addWidget(button)

        # 将按钮布局添加到表单布局中
        layout.addRow(button_layout)

        """初始化UI并根据数据库动态创建按钮 - constraint"""
        # 创建一个 QHBoxLayout 将按钮横向排列
        button_layout2 = QHBoxLayout()
        button_layout2.addWidget(QLabel("Constraint test:"))  # 添加文本

        # 从数据库加载按钮名称并动态创建按钮
        button_names2 = self.load_button_names_from_db(self.preset_constraint_test_cursor)

        # 为每个按钮创建并连接事件
        for name in button_names2:
            button = QPushButton(name, self)
            button.clicked.connect(lambda _, btn_name=name: self.handle_button_click(self.preset_constraint_test_cursor, btn_name))
            button_layout2.addWidget(button)

        # 将按钮布局添加到表单布局中
        layout.addRow(button_layout2)

        """初始化UI并根据数据库动态创建按钮 - transaction"""
        # 创建一个 QHBoxLayout 将按钮横向排列
        button_layout3 = QHBoxLayout()
        button_layout3.addWidget(QLabel("Transaction test:"))  # 添加文本

        # 从数据库加载按钮名称并动态创建按钮
        button_names3 = self.load_button_names_from_db(self.preset_transaction_test_cursor)

        # 为每个按钮创建并连接事件
        for name in button_names3:
            button = QPushButton(name, self)
            button.clicked.connect(lambda _, btn_name=name: self.handle_button_click(self.preset_transaction_test_cursor, btn_name))
            button_layout3.addWidget(button)

        # 将按钮布局添加到表单布局中
        layout.addRow(button_layout3)

        # 测试用例代码输入框
        self.test_case_code = QTextEdit(self)
        self.test_case_code.setPlaceholderText("Test Case Code")
        layout.addRow("Test Case Code:", self.test_case_code)
        self.test_case_code.setAcceptRichText(False)  # 只接受纯文本

        # 运行测试用例按钮
        self.run_button = QPushButton("Run Test Case", self)
        layout.addWidget(self.run_button)

        # 保存测试用例按钮
        self.save_test_case_button = QPushButton("Save Test Case", self)
        layout.addWidget(self.save_test_case_button)

        # 绑定按钮
        self.run_button.clicked.connect(self.run_test_case)  # 运行测试用例
        self.save_test_case_button.clicked.connect(self.add_test_case)  # 保存测试用例

        self.setLayout(layout)
    
    def init_preset_base_test_db(self):
        """初始化 SQLite 数据库并创建表"""
        # 连接数据库（如果不存在会自动创建）
        self.preset_base_test_conn = sqlite3.connect("preset_base_test.db")
        self.preset_base_test_cursor = self.preset_base_test_conn.cursor()

        # 创建存储按钮名称和代码的表
        self.preset_base_test_cursor.execute('''
            CREATE TABLE IF NOT EXISTS buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT NOT NULL
            )
        ''')
        self.preset_base_test_conn.commit()

        # 插入一些按钮名称和对应的代码到数据库（仅在表为空时插入）
        self.preset_base_test_cursor.execute('SELECT COUNT(*) FROM buttons')
        if self.preset_base_test_cursor.fetchone()[0] == 0:
            self.preset_base_test_cursor.executemany('''
                INSERT INTO buttons (name, code) VALUES (?, ?)
            ''', [
                ("Insert", '''
                    def test_insert_data(mysql_connection):
                        """测试向 MySQL 数据库插入数据"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 插入数据
                            cursor.execute("INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass) VALUES ('611', '陈思', '女', '1986-02-20', '95033')")

                            # 查询插入的数据
                            cursor.execute("SELECT COUNT(*) FROM Student WHERE Sid = '611' AND Sname = '陈思' AND Sgender = '女' AND Sbirthday = '1986-02-20' AND Sclass = '95033'")
                            count = cursor.fetchone()[0]

                            # 验证数据是否成功插入
                            assert count == 1
                        
                        finally:
                            # 回滚事务，恢复数据库状态
                            mysql_connection.rollback()

                        cursor.close()'''),
                ("Delete", '''
                    def test_delete_data(mysql_connection):
                        """测试向 MySQL 数据库删除数据"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 删除数据
                            cursor.execute("DELETE FROM Student WHERE Sname = '陈思'")

                            # 查询已删除的数据
                            cursor.execute("SELECT COUNT(*) FROM Student WHERE Sname = '陈思'")
                            count = cursor.fetchone()[0]

                            # 验证数据是否成功删除
                            assert count == 0
                        
                        finally:
                            # 回滚事务，恢复数据库状态
                            mysql_connection.rollback()

                        cursor.close()'''),
                ("Update", '''
                    def test_update_data(mysql_connection):
                        """测试修改数据"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 修改数据
                            cursor.execute("UPDATE Student SET Sname = '张三' WHERE Sid = '511'")

                            # 查询修改的数据
                            cursor.execute("SELECT Sname FROM Student WHERE Sid = '511'")
                            result = cursor.fetchone()

                            # 验证查询结果
                            assert result is not None, "查询结果为空"
                            assert result[0] == '张三', f"Sname 应为 '张三'，但实际是 {result[1]}"

                        finally:
                            # 回滚事务，恢复数据库状态
                            mysql_connection.rollback()

                        cursor.close()'''),
                ("Select", '''
                    def test_select_data(mysql_connection):
                        """测试查询数据"""
                        cursor = mysql_connection.cursor()

                        # 执行 SELECT 查询
                        cursor.execute("SELECT * FROM Student WHERE Sid = '511'")

                        # 获取查询结果
                        result = cursor.fetchone()

                        # 验证查询结果
                        assert result is not None, "查询结果为空"
                        assert result[0] == '511', f"Sid 应为 '611'，但实际是 {result[0]}"
                        assert result[1] == '陈思', f"Sname 应为 '陈思'，但实际是 {result[1]}"
                        assert result[2] == '女', f"Sgender 应为 '女'，但实际是 {result[2]}"
                        assert str(result[3]) == '1986-02-20', f"Sbirthday 应为 '1986-02-20'，但实际是 {result[3]}"
                        assert result[4] == '95033', f"Sclass 应为 '95033'，但实际是 {result[4]}"

                        cursor.close()''')
            ])
            self.preset_base_test_conn.commit()

    def init_preset_constraint_test_db(self):
        """初始化 SQLite 数据库并创建表"""
        # 连接数据库（如果不存在会自动创建）
        self.preset_constraint_test_conn = sqlite3.connect("preset_constraint_test.db")
        self.preset_constraint_test_cursor = self.preset_constraint_test_conn.cursor()

        # 创建存储按钮名称和代码的表
        self.preset_constraint_test_cursor.execute('''
            CREATE TABLE IF NOT EXISTS buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT NOT NULL
            )
        ''')
        self.preset_constraint_test_conn.commit()

        # 插入一些按钮名称和对应的代码到数据库（仅在表为空时插入）
        self.preset_constraint_test_cursor.execute('SELECT COUNT(*) FROM buttons')
        if self.preset_constraint_test_cursor.fetchone()[0] == 0:
            self.preset_constraint_test_cursor.executemany('''
                INSERT INTO buttons (name, code) VALUES (?, ?)
            ''', [
                ("primary_key_constraint", '''
                    def test_primary_key_constraint(mysql_connection):
                        """测试主键约束"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 1. 插入一个有效的记录，主键 Sid 为 '001'
                            cursor.execute("""
                                INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass)
                                VALUES ('001', '张三', '男', '2000-01-01', 'A1')
                            """)
                            # 查询插入的数据
                            cursor.execute("SELECT COUNT(*) FROM Student WHERE Sid = '001' AND Sname = '张三' AND Sgender = '男' AND Sbirthday = '2000-01-01' AND Sclass = 'A1'")
                            count = cursor.fetchone()[0]

                            # 验证数据是否成功插入
                            assert count == 1

                            # 2. 尝试插入一个具有相同 Sid 的记录，应该抛出错误
                            try:
                                cursor.execute("""
                                    INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass)
                                    VALUES ('001', '李四', '女', '1999-12-12', 'A2')
                                """)
                                pytest.fail("应该抛出错误，因为主键 Sid 重复")
                            except Error as e:
                                assert "Duplicate entry" in str(e)  # 主键重复错误

                            # 3. 尝试插入一个没有 Sid 值的记录，应该抛出错误，因为 Sid 不能为空
                            try:
                                cursor.execute("""
                                    INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass)
                                    VALUES (NULL, '王五', '男', '1998-05-05', 'B1')
                                """)
                                pytest.fail("应该抛出错误，因为 Sid 不能为空")
                            except Error as e:
                                assert "Column 'Sid' cannot be null" in str(e)  # Sid 不能为空错误

                        finally:
                            # 回滚事务，恢复数据库状态
                            mysql_connection.rollback()

                        cursor.close()'''),
                ("foreign_key_constraint", '''
                    def test_foreign_key_constraint(mysql_connection):
                        """测试外键约束"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 1.插入一个有效的教师记录，Tid 为 '001'
                            cursor.execute("""
                                INSERT INTO Teacher (Tid, Tname, Tgender, Tbirthday, Tprof, Depart)
                                VALUES ('001', '王五', '男', '1958-12-02', '副教授', '计算机系')
                            """)

                            # 2. 插入一个有效课程的记录，Tid 为 '001'
                            cursor.execute("""
                                INSERT INTO Course (Cid, Cname, Tid)
                                VALUES ('1-001', '离散数学', '001')
                            """)
                            # 查询插入的数据
                            cursor.execute("SELECT COUNT(*) FROM Course WHERE Cid = '1-001' AND Cname = '离散数学' AND Tid = '001'")
                            count = cursor.fetchone()[0]

                            # 验证数据是否成功插入
                            assert count == 1

                            # 3. 尝试插入一个不存在的 Tid（例如 '999'），应该抛出外键约束错误
                            try:
                                cursor.execute("""
                                    INSERT INTO Course (Cid, Cname, Tid)
                                    VALUES ('1-002', '英语', '999')
                                """)
                                pytest.fail("应该抛出错误，因为 Tid '999' 在 Teacher 表中不存在")
                            except Error as e:
                                assert "foreign key constraint fails" in str(e)  # 外键约束错误

                        finally:
                            # 回滚事务，恢复数据库状态
                            mysql_connection.rollback()

                        cursor.close()''')
            ])
            self.preset_constraint_test_conn.commit()

    def init_preset_transaction_test_db(self):
        """初始化 SQLite 数据库并创建表"""
        # 连接数据库（如果不存在会自动创建）
        self.preset_transaction_test_conn = sqlite3.connect("preset_transaction_test.db")
        self.preset_transaction_test_cursor = self.preset_transaction_test_conn.cursor()

        # 创建存储按钮名称和代码的表
        self.preset_transaction_test_cursor.execute('''
            CREATE TABLE IF NOT EXISTS buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT NOT NULL
            )
        ''')
        self.preset_transaction_test_conn.commit()

        # 插入一些按钮名称和对应的代码到数据库（仅在表为空时插入）
        self.preset_transaction_test_cursor.execute('SELECT COUNT(*) FROM buttons')
        if self.preset_transaction_test_cursor.fetchone()[0] == 0:
            self.preset_transaction_test_cursor.executemany('''
                INSERT INTO buttons (name, code) VALUES (?, ?)
            ''', [
                ("commit", '''
                    def test_transaction_commit(backup_and_restore_table, mysql_connection):
                        """测试事务提交功能"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 插入数据
                            cursor.execute("INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass) VALUES ('611', '陈思', '女', '1986-02-20', '95033')")
                            mysql_connection.commit()  # 提交事务

                            # 查询插入的数据
                            cursor.execute("SELECT COUNT(*) FROM Student WHERE Sid = '611' AND Sname = '陈思' AND Sgender = '女' AND Sbirthday = '1986-02-20' AND Sclass = '95033'")
                            count = cursor.fetchone()[0]

                            # 验证数据是否成功插入
                            assert count == 1
                        
                        finally:
                            cursor.close()'''),
                ("rollback", '''
                    def test_transaction_rollback(backup_and_restore_table, mysql_connection):
                        """测试事务回滚功能"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 插入数据
                            cursor.execute("INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass) VALUES ('711', '陈思', '女', '1986-02-20', '95033')")
                            mysql_connection.rollback()  # 回滚事务

                            # 查询是否插入数据
                            cursor.execute("SELECT * FROM Student WHERE Sid = '711' AND Sname = '陈思' AND Sgender = '女' AND Sbirthday = '1986-02-20' AND Sclass = '95033'")
                            result = cursor.fetchone()

                            # 验证数据是否没有插入
                            assert result is None
                        
                        finally:
                            cursor.close()
                    '''),
                ("multiple_operations", '''
                    def test_multiple_operations_in_transaction(backup_and_restore_table, mysql_connection):
                        """测试事务中的多个操作"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 插入数据
                            cursor.execute("INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass) VALUES ('611', '陈思', '女', '1986-02-20', '95033')")

                            # 更新数据
                            cursor.execute("UPDATE Student SET Sname = '张三' WHERE Sid = '611'")

                            # 提交事务
                            mysql_connection.commit()

                            # 查询更新后的数据
                            cursor.execute("SELECT Sname FROM Student WHERE Sid = '611'")
                            result = cursor.fetchone()

                            # 验证数据是否正确更新
                            assert result is not None, "查询结果为空"
                            assert result[0] == '张三', f"Sname 应为 '张三'，但实际是 {result[1]}"
                        
                        finally:
                            cursor.close()'''),
                ("error_and_rollback", '''
                    def test_transaction_error_and_rollback(backup_and_restore_table, mysql_connection):
                        """测试事务中的错误回滚"""
                        cursor = mysql_connection.cursor()

                        # 开始事务
                        mysql_connection.start_transaction()

                        try:
                            # 插入数据
                            cursor.execute("INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass) VALUES ('611', '陈思', '女', '1986-02-20', '95033')")
                            
                            # 故意插入违反唯一约束的数据（假设 name 列有唯一约束）
                            cursor.execute("INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass) VALUES ('611', '陈思', '女', '1986-02-20', '95033')")  # 重复插入

                            # 由于违反约束，会抛出异常
                            mysql_connection.commit()  # 这行不会被执行

                        except Exception as e:
                            # 发生错误时回滚事务
                            mysql_connection.rollback()

                            # 查询是否没有插入数据
                            cursor.execute("SELECT * FROM Student WHERE Sid = '611' AND Sname = '陈思' AND Sgender = '女' AND Sbirthday = '1986-02-20' AND Sclass = '95033'")
                            result = cursor.fetchone()

                            # 验证数据是否没有插入
                            assert result is None

                        finally:
                            cursor.close()''')
            ])
            self.preset_transaction_test_conn.commit()

    def load_button_names_from_db(self, cursor):
        """从数据库加载按钮名称"""
        cursor.execute('SELECT name FROM buttons')
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def handle_button_click(self, cursor, button_name):
        """处理按钮点击事件并从数据库中加载对应的代码"""
        test_case_code_text = self.test_case_code.toPlainText()
        if cursor == self.preset_transaction_test_cursor and 'backup_and_restore_table' not in test_case_code_text:
            append_code = '''
            def backup_table(table, backup_file, database = MYSQL_CONFIG['database'], user = MYSQL_CONFIG['user'], password = MYSQL_CONFIG['password'], host = MYSQL_CONFIG['host']):
                \"\"\"备份 MySQL 数据库中的指定表\"\"\"
                command = f"mysqldump -u {user} -p{password} -h {host} {database} {table} --result-file={backup_file}"
                subprocess.run(command, shell=True, check=True)

            def restore_table(backup_file, database = MYSQL_CONFIG['database'], user = MYSQL_CONFIG['user'], password = MYSQL_CONFIG['password'], host = MYSQL_CONFIG['host']):
                \"\"\"恢复 MySQL 数据库中的指定表\"\"\"
                command = f"mysql -u {user} -p{password} -h {host} {database} --default-character-set=utf8 --local-infile < {backup_file}"
                subprocess.run(command, shell=True, check=True)

            # 创建一个用于备份和恢复操作的 fixture
            @pytest.fixture(scope='function')
            def backup_and_restore_table():
                \"\"\"备份和恢复 MySQL 数据库中的指定表\"\"\"
                table = 'Student'
                backup_file = 'test_record/backup_table.sql'

                # 备份表
                backup_table(table, backup_file)
                
                # 在测试完成后恢复表
                yield
                restore_table(backup_file)'''
            # 使用 textwrap.dedent 去除多余的缩进和开头的换行符
            append_code = textwrap.dedent(append_code).lstrip("\n")
            
            # 将代码追加到输入框中
            self.test_case_code.append(append_code)

        # 从数据库获取按钮对应的代码
        cursor.execute('SELECT code FROM buttons WHERE name = ?', (button_name,))
        row = cursor.fetchone()

        if row:
            # 获取代码
            append_code = row[0]
            
            # 使用 textwrap.dedent 去除多余的缩进和开头的换行符
            append_code = textwrap.dedent(append_code).lstrip("\n")
            
            # 将代码追加到输入框中
            self.test_case_code.append(append_code)
        else:
            print(f"Button '{button_name}' not found in the database")

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
        import subprocess
        import os
        from mysql.connector.errors import Error  # 导入Error异常类

        # 配置你的 MySQL 数据库连接信息
        MYSQL_CONFIG = {mysql_config_str}

        # 创建一个连接 fixture
        @pytest.fixture(scope='function')
        def mysql_connection():
            \"\"\"创建并返回 MySQL 数据库连接\"\"\"
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            yield conn
            conn.close()  # 测试完成后关闭连接
        """

        # 使用 textwrap.dedent 去除多余的缩进和开头的换行符
        additional_code = textwrap.dedent(additional_code).lstrip("\n")

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
        host = self.mysql_host.text()
        user = self.mysql_user.text()
        database = self.mysql_database.text()

        if name and description:
            self.accept()  # 关闭对话框并返回
            # 把数据传递给父窗口
            self.parent().add_test_case_to_db(name, description, code, host, user, database)
    
    def load_cached_configs(self):
        """从数据库加载配置并添加到下拉框"""
        self.config_combo.clear()
        self.config_combo.addItem("Select Previous Configuration")
        
        self.mysql_config_cursor.execute("SELECT host, user, password, database FROM mysql_configs ORDER BY id DESC LIMIT 3")
        rows = self.mysql_config_cursor.fetchall()
        for row in rows:
            self.config_combo.addItem(row[0])  # 将主机名添加到下拉框
            self.mysql_config_cache.append(row)  # 缓存加载的配置

    def load_selected_config(self):
        """加载选择的配置到输入框"""
        selected_index = self.config_combo.currentIndex() - 1  # 去除第一个占位符项
        if selected_index >= 0:
            config = self.mysql_config_cache[selected_index]
            self.mysql_host.setText(config[0])
            self.mysql_user.setText(config[1])
            self.mysql_password.setText(config[2])
            self.mysql_database.setText(config[3])

    def save_mysql_config(self):
        """保存当前输入的配置并更新数据库"""
        config = {
            'host': self.mysql_host.text(),
            'user': self.mysql_user.text(),
            'password': self.mysql_password.text(),
            'database': self.mysql_database.text()
        }

        # 插入新的配置到SQLite数据库
        self.mysql_config_cursor.execute("""
            INSERT INTO mysql_configs (host, user, password, database)
            VALUES (?, ?, ?, ?)
        """, (config['host'], config['user'], config['password'], config['database']))
        self.mysql_config_conn.commit()

        # 更新缓存并重新加载配置
        self.mysql_config_cache.insert(0, (config['host'], config['user'], config['password'], config['database']))
        if len(self.mysql_config_cache) > 3:
            self.mysql_config_cache.pop()  # 保证缓存最多保存3个配置

        # 更新下拉框
        self.load_cached_configs()

        # 显示保存成功的提示
        QMessageBox.information(self, "Success", "Configuration Saved!")
