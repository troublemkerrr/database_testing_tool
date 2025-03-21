import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel
from PyQt5.QtCore import Qt
import sys

class TestResultAnalysis(QWidget):
    def __init__(self):
        super().__init__()

        # 初始化窗口
        self.setWindowTitle("Test Result Analysis")
        self.setGeometry(100, 100, 600, 400)

        # 模拟结果数据
        self.passed = 15
        self.failed = 3
        self.skipped = 2

        # 创建布局
        layout = QVBoxLayout()

        self.analyze_button = QPushButton("Analyze Results", self)
        layout.addWidget(self.analyze_button)

        self.setLayout(layout)
        self.analyze_button.clicked.connect(self.analyze_results)

    def analyze_results(self):
        categories = ['Passed', 'Failed', 'Skipped']
        counts = [self.passed, self.failed, self.skipped]

        # 生成饼图
        plt.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
        plt.title("Test Result Distribution")
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestResultAnalysis()
    sys.exit(app.exec_())
