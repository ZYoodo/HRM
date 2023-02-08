from PyQt5.QtWidgets import QWidget, QBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
import FileRead

class DragTextEdit(QTextEdit):
    """
    支持拖拽文件进入并获取文件路径的QTextEdit
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        """
        若拖拽的文件名包含data.json或infos.json则直接导入文件
        :param event:
        :return:
        """
        try:
            import_file = []
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.path()
                file_name = url.path().split('/')[-1]
                if file_name in ['data.json', 'infos.json']:
                    FileRead.import_file(file_path[1:], 'jsons/'+file_name)
                    import_file.append(file_name)
            import_file = list(set(import_file))
            import_file.sort()
            show_text = ''
            for f in import_file:
                show_text += f'{f}已经被成功导入\n'
            self.setText(show_text)

        except Exception as e:
            self.setText(e.__str__())


def file_import_window_init(choice_window: QWidget):
    """
    导入文件窗口初始化
    :param choice_window:
    :return:
    """
    # 初始化窗口
    main_window: QWidget = choice_window.parent()
    file_import_window = QWidget(main_window)
    file_import_window.resize(main_window.width(), main_window.height())

    # 窗口切换
    file_import_window.show()
    choice_window.hide()

    # 导入文件窗口布局
    file_import_layout = QBoxLayout(QBoxLayout.TopToBottom, file_import_window)
    file_import_layout.setAlignment(Qt.AlignVCenter)

    show_tittle = QLabel('文件导入', file_import_window)
    show_tittle.show()
    show_tittle.setAlignment(Qt.AlignHCenter)
    show_tittle.setStyleSheet('font-size:50px;')
    file_import_layout.addWidget(show_tittle)

    def import_event(file_name):
        try:
            data_import_filedialog = QFileDialog()
            file_path_origin = data_import_filedialog.getOpenFileName(file_import_window, "打开文件", './',
                                                                      'Json (*.json)')

            file_path = file_path_origin[0]
            FileRead.import_file(file_path, file_name)
            show_text_edit.setText(f'{file_name}已经导入完成')
        except Exception as e:
            show_text_edit.setText(e.__str__())

    # data.json 文件导入布局
    data_import_layout = QBoxLayout(QBoxLayout.LeftToRight)
    file_import_layout.addLayout(data_import_layout)

    data_import_tittle = QLabel('data.json导入', file_import_window)
    data_import_tittle.show()
    data_import_layout.addWidget(data_import_tittle)

    data_import_btn = QPushButton('导入', file_import_window)
    data_import_btn.show()
    data_import_btn.clicked.connect(lambda: import_event('jsons/data.json'))
    data_import_layout.addWidget(data_import_btn)

    # infos.json 文件导入布局
    infos_import_layout = QBoxLayout(QBoxLayout.LeftToRight)
    file_import_layout.addLayout(infos_import_layout)

    infos_import_tittle = QLabel('infos.json导入', file_import_window)
    infos_import_tittle.show()
    infos_import_layout.addWidget(infos_import_tittle)

    infos_import_btn = QPushButton('导入', file_import_window)
    infos_import_btn.show()
    infos_import_btn.clicked.connect(lambda: import_event('jsons/infos.json'))
    infos_import_layout.addWidget(infos_import_btn)

    # show_text_edit
    show_text_edit = DragTextEdit(file_import_window)
    show_text_edit.show()
    file_import_layout.addWidget(show_text_edit)

    # 返回按钮定义
    button_back = QPushButton('返回', file_import_window)
    button_back.setShortcut(Qt.Key_Escape)
    button_back.clicked.connect(lambda: (choice_window.show(), file_import_window.deleteLater()))
    file_import_layout.addWidget(button_back)
