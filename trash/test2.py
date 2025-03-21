import pytest
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
import sys

class TestExecution(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化窗口
        self.setWindowTitle("Test Execution")
        self.setGeometry(100, 100, 600, 400)

        # 创建布局
        layout = QVBoxLayout()

        self.run_button = QPushButton("Run Tests", self)
        self.result_label = QLabel("Test Results: ", self)
        layout.addWidget(self.run_button)
        layout.addWidget(self.result_label)

        # 绑定按钮
        self.run_button.clicked.connect(self.run_tests)

        self.setLayout(layout)

    def run_tests(self):
        result = pytest.main(["--maxfail=1", "--disable-warnings", "-q"])
        if result == 0:
            self.result_label.setText("All tests passed!")
        else:
            self.result_label.setText("Some tests failed!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestExecution()
    sys.exit(app.exec_())
