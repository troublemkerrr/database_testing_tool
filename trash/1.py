import subprocess
import os
import pytest
import mysql.connector

# 配置你的 MySQL 数据库连接信息
MYSQL_CONFIG = {
    'host': '127.0.0.1',  # MySQL 服务器地址
    'user': 'admin_01',    # MySQL 用户名
    'password': 'Pwd_0001',  # MySQL 密码
    'database': 'testdb'    # 要连接的数据库
}

# 创建一个连接 fixture
@pytest.fixture(scope='module')
def mysql_connection():
    """创建并返回 MySQL 数据库连接"""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    yield conn
    conn.close()  # 测试完成后关闭连接

def backup_table(database, table, backup_file, user, password, host):
    """备份 MySQL 数据库中的指定表"""
    command = f"mysqldump -u {user} -p{password} -h {host} {database} {table} --result-file={backup_file}"
    subprocess.run(command, shell=True, check=True)

def test_backup_table():
    """使用 pytest 测试备份 MySQL 表"""
    database = 'testdb'
    table = 'Student'
    user = 'admin_01'
    password = 'Pwd_0001'
    host = '127.0.0.1'
    backup_file = 'backup_table.sql'

    # 执行备份
    backup_table(database, table, backup_file, user, password, host)

    # 验证备份文件是否创建成功
    assert os.path.exists(backup_file), "备份文件未创建"

def restore_table(backup_file, user, password, host, database):
    """恢复 MySQL 数据库中的指定表"""
    command = f"mysql -u {user} -p{password} -h {host} {database} --default-character-set=utf8 --local-infile < {backup_file}"
    subprocess.run(command, shell=True, check=True)

def test_restore_table():
    """使用 pytest 测试恢复 MySQL 表"""
    backup_file = 'backup_table.sql'
    database = 'testdb'
    user = 'admin_01'
    password = 'Pwd_0001'
    host = '127.0.0.1'

    # 恢复表
    restore_table(backup_file, user, password, host, database)

    # 验证表是否恢复成功
    # 你可以用一个 SELECT 查询来验证数据是否恢复
    # 配置你的 MySQL 数据库连接信息
    MYSQL_CONFIG = {
        'host': '127.0.0.1',  # MySQL 服务器地址
        'user': 'admin_01',    # MySQL 用户名
        'password': 'Pwd_0001',  # MySQL 密码
        'database': 'testdb'    # 要连接的数据库
    }
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Student")  # 这里检查表中是否有数据
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    assert result[0] > 0, "恢复失败，表中没有数据"


# test_backup_table()
# test_restore_table()


def test_transaction_commit(mysql_connection):
    test_backup_table()
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
        cursor.close()
        test_restore_table()

def test_transaction_rollback(mysql_connection):
    test_backup_table()
    """测试事务回滚功能"""
    cursor = mysql_connection.cursor()

    # 开始事务
    mysql_connection.start_transaction()

    try:
        # 插入数据
        cursor.execute("INSERT INTO Student (Sid, Sname, Sgender, Sbirthday, Sclass) VALUES ('611', '陈思', '女', '1986-02-20', '95033')")
        mysql_connection.rollback()  # 回滚事务

        # 查询是否插入数据
        cursor.execute("SELECT * FROM Student WHERE Sid = '611' AND Sname = '陈思' AND Sgender = '女' AND Sbirthday = '1986-02-20' AND Sclass = '95033'")
        result = cursor.fetchone()

        # 验证数据是否没有插入
        assert result is None
    
    finally:
        cursor.close()
    test_restore_table()

def test_multiple_operations_in_transaction(mysql_connection):
    test_backup_table()
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
        cursor.close()
    test_restore_table()

def test_transaction_error_and_rollback(mysql_connection):
    test_backup_table()
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
        cursor.close()
    test_restore_table()
