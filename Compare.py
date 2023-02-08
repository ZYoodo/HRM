from PyQt5.QtWidgets import QComboBox, QTextEdit, QWidget, QBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
import datetime
import FileRead
import re


def data_json_record(src_data: str):
    # 完成姓名分割
    names_and_signs = src_data.split(';')
    # 去除最后一位空串
    list.remove(names_and_signs, '')
    names = [re.findall('^[^(]*', x)[0] for x in names_and_signs]
    signs = [None if re.findall('(?<=\().*(?=\))', x) == [] else re.findall('(?<=\().*(?=\))', x)[0] for x in
             names_and_signs]
    # 当天日期
    today = datetime.date.today().__str__()

    # 拼接当天姓名快照
    today_data = {today: {'names': names, 'signs': signs}}

    # 读取数据
    data, dates = FileRead.read_data_json()

    # 更新当天数据进历史数据
    data.update(today_data)

    # 写入当天数据及历史数据
    FileRead.write_data_json(data)


def get_adds_names(data: dict, start_date: str, end_date: str) -> list:
    """
    获取post_names - pre_names 的部分
    :param data: 源json文件中的内容
    :param start_date: 对比的开始日期
    :param end_date: 对比的结束日期
    :return: 返回开始日期比结束日期多的人名列表
    """

    pre_names = data[start_date]['names']
    post_names = data[end_date]['names']
    # 增量list
    adds = []
    # 标志位，处理重复名字问题
    n = [0 for _ in range(len(pre_names))]

    for i in range(len(post_names)):
        if post_names[i] in pre_names:
            flag = 0
            for j in range(len(pre_names)):
                if post_names[i] == pre_names[j] and n[j] == 0:
                    n[j] = 1
                    flag = 1
                    break
            if flag == 0:
                adds.append(post_names[i])
        else:
            adds.append(post_names[i])
    return adds


def get_compare_result_text(data: dict, pre_date: str, post_date: str):
    """
    生成比较结果的文本
    :param data:
    :param pre_date:
    :param post_date:
    :return:
    """
    adds = get_adds_names(data, pre_date, post_date)
    lost = get_adds_names(data, post_date, pre_date)
    lost_str = pre_date + ' 至 ' + post_date + ' 离职: ' + '、'.join(lost) if len(
        lost) > 0 else pre_date + ' 至 ' + post_date + ' 无人离职'
    adds_str = pre_date + ' 至 ' + post_date + ' 入职: ' + '、'.join(adds) if len(
        adds) > 0 else pre_date + ' 至 ' + post_date + ' 无人入职'
    return lost_str + '\n' * 3 + adds_str


def get_normal_compare_result_text(data: dict, dates: list, pre_date: str, post_date: str) -> str:
    """
    生成自定义比较结果的文本
    :param data:
    :param dates:
    :param pre_date:
    :param post_date:
    :return:
    """
    if datetime.datetime.strptime(pre_date, '%Y-%m-%d') > datetime.datetime.strptime(post_date, '%Y-%m-%d'):
        return '开始日期应不大于结束日期！！！'
    adds = []
    lost = []
    begin_idx = dates.index(pre_date)
    end_idx = dates.index(post_date)

    for i in range(begin_idx, end_idx):
        adds.extend(get_adds_names(data, dates[i], dates[i + 1]))
        lost.extend(get_adds_names(data, dates[i + 1], dates[i]))

    lost_str = pre_date + ' 至 ' + post_date + ' 离职: ' + '、'.join(lost) if len(
        lost) > 0 else pre_date + ' 至 ' + post_date + ' 无人离职'
    adds_str = pre_date + ' 至 ' + post_date + ' 入职: ' + '、'.join(adds) if len(
        adds) > 0 else pre_date + ' 至 ' + post_date + ' 无人入职'
    return lost_str + '\n' * 3 + adds_str


def get_detail_compare_result_text(data: dict, dates: list, pre_date: str, post_date: str) -> str:
    """
    生成详细比较结果的文本
    :param data:
    :param dates:
    :param pre_date:
    :param post_date:
    :return:
    """
    if datetime.datetime.strptime(pre_date, '%Y-%m-%d') > datetime.datetime.strptime(post_date, '%Y-%m-%d'):
        return '开始日期应不大于结束日期！！！'

    begin_idx = dates.index(pre_date)
    end_idx = dates.index(post_date)

    output_str = ''
    adds_count = 0
    lost_count = 0

    for i in range(begin_idx, end_idx):
        adds = get_adds_names(data, dates[i], dates[i + 1])
        lost = get_adds_names(data, dates[i + 1], dates[i])
        adds_count += len(adds)
        lost_count += len(lost)
        lost_str = dates[i] + ' 至 ' + dates[i + 1] + ' 离职: ' + '、'.join(lost) if len(
            lost) > 0 else dates[i] + ' 至 ' + dates[i + 1] + ' 无人离职'
        adds_str = dates[i] + ' 至 ' + dates[i + 1] + ' 入职: ' + '、'.join(adds) if len(
            adds) > 0 else dates[i] + ' 至 ' + dates[i + 1] + ' 无人入职'
        output_str += lost_str + '\n' + adds_str + '\n' * 2
    output_str += pre_date + ' 至 ' + post_date + ' 共离职: ' + lost_count.__str__() + '人' + '\n'
    output_str += pre_date + ' 至 ' + post_date + ' 共入职: ' + adds_count.__str__() + '人' + '\n'
    output_str += '人数变化: ' + len(data[pre_date]['names']).__str__() + ' -> ' + \
                  len(data[post_date]['names']).__str__()
    return output_str


def daily_record_window_init(choice_window: QWidget):
    """
    日常记录窗口初始化
    :param choice_window:
    :return:
    """

    # 初始化窗口
    main_window: QWidget = choice_window.parent()
    daily_record_window = QWidget(main_window)
    daily_record_window.resize(main_window.width(), main_window.height())

    # 窗口切换
    daily_record_window.show()
    choice_window.hide()

    # 构建布局
    daily_record_layout = QBoxLayout(QBoxLayout.TopToBottom, daily_record_window)
    daily_record_layout.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)

    # 标题展示
    label_tittle = QLabel(daily_record_window)
    label_tittle.setText('请输入当天姓名集')
    label_tittle.setAlignment(Qt.AlignCenter)
    label_tittle.show()
    daily_record_layout.addWidget(label_tittle)

    # 输入框
    input_textedit = QTextEdit(daily_record_window)
    input_textedit.show()
    daily_record_layout.addWidget(input_textedit)

    # 提交按钮， 提交后后清除输入框中内容
    commit_btn = QPushButton(daily_record_window)
    commit_btn.setText('提交')
    commit_btn.clicked.connect(
        lambda: (data_json_record(input_textedit.toPlainText()), label_tittle.setText('提交完成!!!')))
    commit_btn.show()
    daily_record_layout.addWidget(commit_btn)

    # 返回按钮定义
    button_back = QPushButton('返回', daily_record_window)
    button_back.setShortcut(Qt.Key_Escape)
    button_back.clicked.connect(lambda: (choice_window.show(), daily_record_window.deleteLater()))
    daily_record_layout.addWidget(button_back)


def quick_compare_window_init(choice_window: QWidget):
    """
    快速比较窗口生成
    :param choice_window:
    :return:
    """

    # 初始化窗口
    main_window: QWidget = choice_window.parent()
    quick_compare_window = QWidget(main_window)
    quick_compare_window.resize(main_window.width(), main_window.height())

    # 窗口切换
    quick_compare_window.show()
    choice_window.hide()

    # 布局构造
    quick_compare_layout = QBoxLayout(QBoxLayout.TopToBottom, quick_compare_window)
    quick_compare_layout.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
    quick_compare_layout.setSpacing(int(quick_compare_window.height() * 0.1))

    # 展示输出文本
    show_text = QTextEdit(quick_compare_window)
    show_text.show()
    quick_compare_layout.addWidget(show_text)

    # 返回按钮定义
    button_back = QPushButton('返回', quick_compare_window)
    button_back.setShortcut(Qt.Key_Escape)
    button_back.clicked.connect(lambda: (choice_window.show(), quick_compare_window.deleteLater()))
    quick_compare_layout.addWidget(button_back)

    try:
        data, dates = FileRead.read_data_json()
        if len(dates) < 2:
            output_str = '历史数据数量不足'
            show_text.setText(output_str)
        else:
            pre_date = dates[-2]
            post_date = dates[-1]
            output_str = get_compare_result_text(data, pre_date, post_date)
            show_text.setText(output_str)
    except Exception as e:
        show_text.setText(e.__str__())

def diy_compare_window_init(choice_window: QWidget):
    """
    自定义比较窗口生成
    :param choice_window:
    :return:
    """

    # 初始化窗口
    main_window: QWidget = choice_window.parent()
    diy_compare_window = QWidget(main_window)
    diy_compare_window.resize(main_window.width(), main_window.height())

    # 窗口切换
    diy_compare_window.show()
    choice_window.hide()

    # 定义整体布局
    diy_compare_layout = QBoxLayout(QBoxLayout.TopToBottom)
    diy_compare_layout.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)

    # 定义横向tittle layout
    tittle_layout = QBoxLayout(QBoxLayout.LeftToRight)
    tittle_layout.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
    diy_compare_layout.addLayout(tittle_layout)

    # 定义tittle
    pre_date_label = QLabel(diy_compare_window)
    pre_date_label.setText('开始日期')
    pre_date_label.resize(int(diy_compare_window.width() / 2), 50)
    pre_date_label.show()
    tittle_layout.addWidget(pre_date_label)

    pre_date_combox = QComboBox(diy_compare_window)
    pre_date_combox.show()
    tittle_layout.addWidget(pre_date_combox)

    post_date_label = QLabel(diy_compare_window)
    post_date_label.setText('结束日期')
    post_date_label.resize(int(diy_compare_window.width() / 2), 50)
    post_date_label.show()
    tittle_layout.addWidget(post_date_label)

    post_date_combox = QComboBox(diy_compare_window)
    post_date_combox.show()
    tittle_layout.addWidget(post_date_combox)

    # 输出模式
    method_combox = QComboBox(diy_compare_window)
    method_combox.show()
    method_combox.addItems(['普通模式', '日志模式'])
    tittle_layout.addWidget(method_combox)

    # 输出文本框
    show_text = QTextEdit(diy_compare_window)
    show_text.show()
    diy_compare_layout.addWidget(show_text)

    def get_compare_result() -> str:
        """
        根据当前模式获取返回文本
        :return:
        """
        if method_combox.currentText() == '普通模式':
            return get_normal_compare_result_text(data, dates, pre_date_combox.currentText(),
                                                  post_date_combox.currentText())
        elif method_combox.currentText() == '日志模式':
            return get_detail_compare_result_text(data, dates, pre_date_combox.currentText(),
                                                  post_date_combox.currentText())

    # 确认按钮
    commit_btn = QPushButton(diy_compare_window)
    commit_btn.setText('确认')
    commit_btn.setShortcut(Qt.Key_Return)
    commit_btn.clicked.connect(lambda: show_text.setText(get_compare_result()))
    diy_compare_layout.addWidget(commit_btn)

    # 返回按钮定义
    button_back = QPushButton('返回', diy_compare_window)
    button_back.setShortcut(Qt.Key_Escape)
    button_back.clicked.connect(lambda: (choice_window.show(), diy_compare_window.deleteLater()))
    diy_compare_layout.addWidget(button_back)

    diy_compare_layout.addLayout(tittle_layout)
    diy_compare_window.setLayout(diy_compare_layout)

    # 初始化数据
    try:
        data, dates = FileRead.read_data_json()
        pre_date_combox.addItems(dates[::-1])
        post_date_combox.addItems(dates[::-1])
    except Exception as e:
        # 若不存在文件
        show_text.setText(e.__str__())
        commit_btn.setEnabled(False)

