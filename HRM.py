"""
主界面
"""
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QPushButton, QApplication
from PyQt5.QtCore import Qt
import sys

import Compare
import InfoSearch
import OARequest
import FileImport


class HRM:
    """
    主界面类
    """
    # 定义窗口大小
    main_window_width = 500
    main_window_height = 600
    version = 'v 1.2正式版'

    def __init__(self):
        self.app = QApplication(sys.argv)

        # 主窗口初始化
        self.main_window_init()

        # 首页界面初始化
        self.choice_window_init()

        sys.exit(self.app.exec_())

    def main_window_init(self):
        """
        主窗口初始化
        :return:
        """
        main_window = QMainWindow()
        main_window.resize(self.main_window_width, self.main_window_height)
        main_window.setWindowTitle('人力资源监视器')
        main_window.setWindowIcon(QIcon('icons/hrm.ico'))
        # 禁止调整大小
        main_window.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint)
        main_window.show()
        self.main_window = main_window

    def choice_window_init(self):
        """
        首页界面初始化
        :return:
        """

        # 窗口大小初始化
        choice_window = QWidget(self.main_window)
        choice_window.resize(self.main_window.width(), self.main_window.height())
        choice_window.show()

        # 版本号展示
        version_label = QLabel(self.version, choice_window)
        version_label.show()
        version_label_font_size = 13
        version_label.setStyleSheet(f'font-size: {version_label_font_size.__str__()}px;color: grey;')
        version_label.adjustSize()
        version_label.move(0, choice_window.height() - version_label_font_size)

        # 纵向布局
        choice_window_layout = QVBoxLayout(choice_window)
        choice_window_layout.setAlignment(Qt.AlignVCenter)

        label_tittle = QLabel(choice_window)
        label_tittle.setAlignment(Qt.AlignCenter)
        label_tittle.setText('HRM')
        label_tittle.setStyleSheet('font-size: 200px')
        choice_window_layout.addWidget(label_tittle)

        daily_record_btn = QPushButton()
        daily_record_btn.setText('日常记录')
        daily_record_btn.setStyleSheet('font-size: 30px')
        daily_record_btn.clicked.connect(lambda: Compare.daily_record_window_init(choice_window))
        choice_window_layout.addWidget(daily_record_btn)

        quick_compare_btn = QPushButton()
        quick_compare_btn.setText('快速比较')
        quick_compare_btn.setStyleSheet('font-size: 30px')
        quick_compare_btn.clicked.connect(lambda: Compare.quick_compare_window_init(choice_window))
        choice_window_layout.addWidget(quick_compare_btn)

        diy_compare_btn = QPushButton()
        diy_compare_btn.setText('自定义比较')
        diy_compare_btn.setStyleSheet('font-size: 30px')
        diy_compare_btn.clicked.connect(lambda: Compare.diy_compare_window_init(choice_window))
        choice_window_layout.addWidget(diy_compare_btn)

        info_search_btn = QPushButton('OA人员信息查询')
        info_search_btn.setStyleSheet('font-size: 30px')
        info_search_btn.clicked.connect(lambda: InfoSearch.info_search_window_init(choice_window))
        choice_window_layout.addWidget(info_search_btn)

        info_update_btn = QPushButton('OA人员信息更新')
        info_update_btn.setStyleSheet('font-size: 30px')
        info_update_btn.clicked.connect(lambda: OARequest.oa_request_window_init(choice_window))
        choice_window_layout.addWidget(info_update_btn)

        extend_btn = QPushButton('导入文件')
        extend_btn.setStyleSheet('font-size: 30px')
        extend_btn.clicked.connect(lambda: FileImport.file_import_window_init(choice_window))
        choice_window_layout.addWidget(extend_btn)

        exit_btn = QPushButton()
        exit_btn.setText('退出')
        exit_btn.setStyleSheet('font-size: 30px')
        exit_btn.clicked.connect(sys.exit)
        choice_window_layout.addWidget(exit_btn)

        self.choice_window = choice_window


if __name__ == '__main__':
    hrm = HRM()
