import pytest
import mysql.connector
import subprocess
import os
from mysql.connector.errors import Error  # 导入Error异常类

# 配置你的 MySQL 数据库连接信息
MYSQL_CONFIG = {
    'host': '127.0.0.1',  # MySQL 服务器地址
    'user': 'admin_01',    # MySQL 用户名
    'password': 'Pwd_0001',  # MySQL 密码
    'database': 'testdb'    # 要连接的数据库
}


# 创建一个连接 fixture
@pytest.fixture(scope='function')
def mysql_connection():
    """创建并返回 MySQL 数据库连接"""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    yield conn
    conn.close()  # 测试完成后关闭连接

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

    cursor.close()