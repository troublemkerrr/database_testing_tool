import pytest
import mysql.connector
from mysql.connector.errors import Error  # 导入Error异常类

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

    cursor.close()

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

    cursor.close()