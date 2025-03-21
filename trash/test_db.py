import pytest
import mysql.connector

# 配置你的 MySQL 数据库连接信息
MYSQL_CONFIG = {
    'host': '127.0.0.1',  # MySQL 服务器地址
    'user': 'admin_01',       # MySQL 用户名
    'password': 'Pwd_0001',  # MySQL 密码
    'database': 'testdb'   # 要连接的数据库
}

# 创建一个连接 fixture
@pytest.fixture(scope='module')
def mysql_connection():
    """创建并返回 MySQL 数据库连接"""
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    yield conn
    conn.close()  # 测试完成后关闭连接

# 创建一个表并进行测试
@pytest.fixture(scope='module')
def setup_table(mysql_connection):
    """创建一个测试用表"""
    cursor = mysql_connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        );
    """)
    mysql_connection.commit()
    yield cursor
    # 测试结束后清理表
    cursor.execute("DROP TABLE IF EXISTS test_table;")
    mysql_connection.commit()

def test_insert_data(mysql_connection, setup_table):
    """测试向 MySQL 数据库插入数据"""
    cursor = mysql_connection.cursor()

    # 插入数据
    cursor.execute("INSERT INTO test_table (name) VALUES ('Alice')")
    mysql_connection.commit()

    # 查询插入的数据
    cursor.execute("SELECT * FROM test_table WHERE name='Alice'")
    result = cursor.fetchone()

    # 验证数据是否成功插入
    assert result is not None
    assert result[1] == 'Alice'

    cursor.close()

def test_delete_data(mysql_connection, setup_table):
    """测试从 MySQL 数据库删除数据"""
    cursor = mysql_connection.cursor()

    # 删除数据
    cursor.execute("DELETE FROM test_table WHERE name='Alice'")
    mysql_connection.commit()

    # 查询已删除的数据
    cursor.execute("SELECT * FROM test_table WHERE name='Alice'")
    result = cursor.fetchone()

    # 验证数据是否已被删除
    assert result is None
    cursor.close()
