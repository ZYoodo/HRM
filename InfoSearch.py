import FileRead
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QWidget, QBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import Qt
import re


def info_search_window_init(choice_window: QWidget):
    """
    OA信息查询窗口初始化
    :param choice_window:
    :return:
    """
    # 初始化窗口
    main_window: QWidget = choice_window.parent()
    info_search_window = QWidget(main_window)
    info_search_window.resize(main_window.width(), main_window.height())

    # 窗口切换
    info_search_window.show()
    choice_window.hide()

    # 构建布局
    info_search_layout = QBoxLayout(QBoxLayout.TopToBottom, info_search_window)
    info_search_layout.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)

    # 信息更新时间说明
    last_update_tittle = QLabel('信息最近更新日期:' + get_info_date(), info_search_window)
    last_update_tittle.show()
    info_search_layout.addWidget(last_update_tittle)

    # 搜索过滤条件展示和展示函数
    def search_filter_label_flush():
        show_text = ''
        if len(search_filter_list) > 0:
            for i in range(len(search_filter_list)):
                if i == 0:
                    show_text += search_filter_list[i].get(list(search_filter_list[i].keys())[0]).__str__()
                else:
                    show_text += list(search_filter_list[i].keys())[0] + search_filter_list[i].get(list(search_filter_list[i].keys())[0]).__str__()
        search_filter_label.setText(show_text)


    search_filter_label = QLabel('', info_search_window)
    search_filter_label.show()
    info_search_layout.addWidget(search_filter_label)

    # 过滤命令记录
    search_filter_list = [{str: {str: str}}]

    # 搜索布局
    search_layout = QBoxLayout(QBoxLayout.LeftToRight, info_search_window)
    info_search_layout.addLayout(search_layout)

    # 搜索id缓存
    search_ids = []

    def set_search_ids(ids: list):
        """
        给search_ids赋值
        :param ids:
        :return:
        """
        search_ids.clear()
        for id in ids:
            search_ids.append(id)

    search_type_combox = QComboBox(info_search_window)
    search_type_list = ['姓名', '部门', '性别', '工号', '邮箱', '直接上级姓名', '直接上级id', '职位', '岗位',
                        '聘用形式', '员工职级old', '办公地点', '联系电话', '转正状态', '员工状态', '创建时间',
                        '最后修改日期']
    search_type_combox.addItems(search_type_list)
    search_type_combox.show()
    search_layout.addWidget(search_type_combox)

    word_search_textline = QLineEdit(info_search_window)
    word_search_textline.show()
    search_layout.addWidget(word_search_textline)

    def search_func(func):
        """
        搜索、并集、交集按钮
        :param func: 调用的函数
        :return:
        """
        if func == get_info_ids_by_word_regexp:
            search_filter_list.clear()
            search_filter_list.append({'|': {search_type_combox.currentText(): word_search_textline.text()}})
        elif func == get_info_union_ids_by_word_regexp:
            search_filter_list.append({'|': {search_type_combox.currentText(): word_search_textline.text()}})
        elif func == get_info_intersection_ids_by_word_regexp:
            search_filter_list.append({'&': {search_type_combox.currentText(): word_search_textline.text()}})

        search_filter_label_flush()

        ids = func(word_search_textline.text(), search_type_combox.currentText(), search_ids)
        show_text = get_info_text_by_ids(ids)
        show_text_edit.setText(show_text)
        set_search_ids(ids)

    word_search_btn = QPushButton('搜索', info_search_window)
    word_search_btn.setMaximumSize(40, 25)
    word_search_btn.show()
    word_search_btn.clicked.connect(lambda: search_func(get_info_ids_by_word_regexp))
    search_layout.addWidget(word_search_btn)

    word_search_union_btn = QPushButton('并集', info_search_window)
    word_search_union_btn.setMaximumSize(40, 25)
    word_search_union_btn.show()
    word_search_union_btn.clicked.connect(lambda: search_func(get_info_union_ids_by_word_regexp))
    search_layout.addWidget(word_search_union_btn)

    word_search_intersection_btn = QPushButton('交集', info_search_window)
    word_search_intersection_btn.setMaximumSize(40, 25)
    word_search_intersection_btn.show()
    word_search_intersection_btn.clicked.connect(lambda: search_func(get_info_intersection_ids_by_word_regexp))
    search_layout.addWidget(word_search_intersection_btn)

    # 撤回按钮和撤回函数
    def search_undo():
        """
        根据命令日志，完成过滤撤回操作
        :return:
        """
        if len(search_filter_list) <= 1:
            # 清空操作记录
            search_filter_list.clear()
            search_filter_label_flush()
            show_text_edit.setText('')
        else:
            # 去除最后一步操作记录
            search_filter_list.pop()
            # 刷新过滤条件展示标签
            search_filter_label_flush()

            # 重新一步步完成过滤操作
            set_search_ids([])
            for search_filter in search_filter_list:
                filter_method = list(search_filter.keys())[0]
                word = list(search_filter.get(filter_method).values())[0]
                value_type = list(search_filter.get(filter_method).keys())[0]
                if filter_method == '|':
                    ids = get_info_union_ids_by_word_regexp(word, value_type, search_ids)
                    set_search_ids(ids)
                elif filter_method == '&':
                    ids = get_info_intersection_ids_by_word_regexp(word, value_type, search_ids)
                    set_search_ids(ids)
            show_text_edit.setText(get_info_text_by_ids(search_ids))

    word_search_undo_btn = QPushButton('撤回', info_search_window)
    word_search_undo_btn.setMaximumSize(40, 25)
    word_search_undo_btn.show()
    word_search_undo_btn.clicked.connect(search_undo)
    search_layout.addWidget(word_search_undo_btn)

    # 展示框
    show_text_edit = QTextEdit(info_search_window)
    show_text_edit.show()
    info_search_layout.addWidget(show_text_edit)

    # 返回按钮定义
    button_back = QPushButton('返回', info_search_window)
    button_back.clicked.connect(lambda: (choice_window.show(), info_search_window.deleteLater()))
    info_search_layout.addWidget(button_back)


def get_info_json():
    """
    获取info中的内容
    :return:
    """
    date, data = FileRead.read_info_json()
    return data


def get_info_date():
    """
    获取的info的生成日期
    :return:
    """
    date, data = FileRead.read_info_json()
    return date


def get_pretty_info_text(info: dict) -> str:
    """
    整理好传入的info
    :param info:
    :return:
    """
    type_list = ['姓名', '部门', '性别', '工号', '邮箱', '直接上级姓名', '直接上级id', '职位', '岗位', '聘用形式',
                 '员工职级old', '办公地点', '联系电话', '转正状态', '员工状态', '创建时间', '最后修改日期']
    pretty_info_text = ''
    for key in type_list:
        pretty_info_text += f'{key}: {info.get(key)}\n'
    return pretty_info_text


def get_info_ids_by_word_regexp(word: str, value_type: str, source_ids: list = []) -> list:
    """
    按给定的列模糊搜索，返回数据id list,sourece_ids为维护一致性
    :param word:
    :param value_type:
    :return:
    """
    data: dict = get_info_json()
    ids = [x[0] for x in data.items() if re.search(word, x[1].get(value_type)) is not None]
    return ids


def get_info_union_ids_by_word_regexp(word: str, value_type: str, source_ids: list) -> list:
    """
    新ids和源ids求合集
    :param word:
    :param value_type:
    :param ids:
    :return:
    """
    data: dict = get_info_json()
    ids = [x[0] for x in data.items() if re.search(word, x[1].get(value_type)) is not None]
    return list(set(ids) | set(source_ids))


def get_info_intersection_ids_by_word_regexp(word: str, value_type: str, source_ids: list) -> list:
    """
    新ids和源ids求交集
    :param word:
    :param value_type:
    :param ids:
    :return:
    """
    data: dict = get_info_json()
    ids = [x[0] for x in data.items() if re.search(word, x[1].get(value_type)) is not None]
    return list(set(ids) & set(source_ids))


def get_info_text_by_ids(ids: list):
    """
    按给定ids 返回整理好的人员信息
    :param ids:
    :return:
    """
    data: dict = get_info_json()
    info_text = ''
    if len(ids) >= 1:
        info_text += f'共查询到{len(ids)}人\n\n'
        for id in ids:
            info_text += get_pretty_info_text(data.get(id))
            info_text += '\n\n\n'
    else:
        info_text += '未查询到结果'
    return info_text
