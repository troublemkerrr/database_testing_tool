import pytest
import os
import shutil
import sys

test_code_filename = 'test_record/test_case.py'
pytest.main([test_code_filename])

# 写入合并后的内容
full_test_code = '''
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
'''

with open(test_code_filename, 'w') as f:
    f.write(full_test_code)
    f.flush()  # 强制刷新缓冲区
    os.fsync(f.fileno())  # 确保文件写入硬盘


# 删除 pytest 缓存文件夹
shutil.rmtree('.pytest_cache', ignore_errors=True)
# shutil.rmtree('__pycache__', ignore_errors=True)
# shutil.rmtree('test_record/.pytest_cache', ignore_errors=True)
shutil.rmtree('test_record/__pycache__', ignore_errors=True)
# 强制刷新文件缓存
os.sync()
# 执行 pytest 测试
pytest.main([test_code_filename, '--cache-clear', '--disable-warnings'])