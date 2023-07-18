import json
import os.path

import selenium.common
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import requests
from PyQt5.QtWidgets import QLineEdit, QTextEdit, QWidget, QBoxLayout, QPushButton, QLabel, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot

import FileRead


def oa_request_window_init(choice_window: QWidget):
    """
    OA信息更新窗口
    :param choice_window:
    :return:
    """
    # 初始化窗口
    main_window: QWidget = choice_window.parent()
    oa_request_window = QWidget(main_window)
    oa_request_window.resize(main_window.width(), main_window.height())

    # 窗口切换
    oa_request_window.show()
    choice_window.hide()

    # 构建布局
    oa_request_layout = QBoxLayout(QBoxLayout.TopToBottom, oa_request_window)
    oa_request_layout.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)

    # OA账号密码登录布局
    login_lay_out = QBoxLayout(QBoxLayout.LeftToRight)
    oa_request_layout.addLayout(login_lay_out)

    user_label = QLabel('OA用户名', oa_request_window)
    user_label.show()
    login_lay_out.addWidget(user_label)

    user_lineedit = QLineEdit(oa_request_window)
    user_lineedit.show()
    login_lay_out.addWidget(user_lineedit)

    password_label = QLabel('OA密码', oa_request_window)
    password_label.show()
    login_lay_out.addWidget(password_label)

    password_lineedit = QLineEdit(oa_request_window)
    password_lineedit.setEchoMode(QLineEdit.Password)
    password_lineedit.show()
    login_lay_out.addWidget(password_lineedit)

    # 读取默认账号密码
    if FileRead.is_exists_login_json():
        user, password = FileRead.read_login_json()
        user_lineedit.setText(user)
        password_lineedit.setText(password)

    # 保存账号密码
    def save_login_info():
        FileRead.write_login_json(user_lineedit.text(), password_lineedit.text())

    remember_btn = QPushButton('保存', oa_request_window)
    remember_btn.show()
    remember_btn.clicked.connect(save_login_info)
    login_lay_out.addWidget(remember_btn)

    # cookie 刷新和测试布局
    cookie_lay_out = QBoxLayout(QBoxLayout.LeftToRight)
    oa_request_layout.addLayout(cookie_lay_out)

    # 刷新响应事件
    def flush_cookie():
        flush_cookie_thred.show_text_signal.connect(show_text_edit.setText)
        flush_cookie_thred.set_info(user_lineedit.text(), password_lineedit.text())
        flush_cookie_thred.start()

    flush_cookie_btn = QPushButton('刷新cookie', oa_request_window)
    flush_cookie_btn.show()
    # 刷新线程实例
    flush_cookie_thred = FlushCookieThread()
    flush_cookie_btn.clicked.connect(flush_cookie)
    cookie_lay_out.addWidget(flush_cookie_btn)

    # 测试cookie按钮
    def test_cookie():
        """
        测试cookie按钮的响应事件，若能成功返回个人信息则为正确cookie
        :return:
        """
        # 读取headers
        if not os.path.exists('jsons/headers.json'):
            show_text_edit.setText('cookie不存在')
            return
        try:
            with open('jsons/headers.json', 'r', encoding='utf-8') as f:
                headers = dict(json.load(f))

            cookie = headers.get('cookie')
            uid = re.findall(r'loginuuids=(\d+)', cookie)[0]
            card_info = request_cardinfo_by_id(uid)
            if card_info.get_info_name().get('姓名') == '':
                show_text_edit.setText('cookie无效或已过期')
            else:
                show_text_edit.setText('cookie目前可用\n\n' + card_info.get_cardinfo_text())
                update_info_btn.setEnabled(True)

        except Exception as e:
            show_text_edit.setText(e.__str__())

    test_cookie_btn = QPushButton('测试cookie', oa_request_window)
    test_cookie_btn.show()
    test_cookie_btn.clicked.connect(test_cookie)
    cookie_lay_out.addWidget(test_cookie_btn)

    # 下载更新info.json布局
    update_info_layout = QBoxLayout(QBoxLayout.LeftToRight, oa_request_window)
    oa_request_layout.addLayout(update_info_layout)

    # 时间间隔设置提示label
    request_interval_label = QLabel('爬取间隔/s:', oa_request_window)
    request_interval_label.show()
    request_interval_label.setMaximumSize(80, 25)
    update_info_layout.addWidget(request_interval_label)

    # 时间间隔设置combox
    request_interval_combox = QComboBox(oa_request_window)
    request_interval_combox.show()
    request_interval_combox.setMaximumSize(50, 25)
    request_interval_combox.addItems(['0.1', '0.5', '1', '2', '5', '10'])
    request_interval_combox.setCurrentIndex(2)
    update_info_layout.addWidget(request_interval_combox)

    # 下载按钮及下载函数
    update_info_thread = UpdateInfoThread()
    def update_info():
        """
        更新人员信息按钮响应事件
        :return:
        """
        update_info_thread.show_text_signal.connect(show_text_edit.setText)
        update_info_thread.set_info(float(request_interval_combox.currentText()))
        update_info_thread.start()

        # 激活取消按键
        update_info_cancel_btn.setEnabled(True)

    update_info_btn = QPushButton('更新人员信息', oa_request_window)
    update_info_btn.show()
    update_info_btn.clicked.connect(update_info)
    update_info_btn.setEnabled(False)
    update_info_layout.addWidget(update_info_btn)

    # 取消按键
    update_info_cancel_btn = QPushButton('取消', oa_request_window)
    update_info_cancel_btn.show()
    update_info_cancel_btn.clicked.connect(lambda: (update_info_thread.terminate(), update_info_cancel_btn.setEnabled(False)))
    update_info_cancel_btn.setEnabled(False)
    update_info_layout.addWidget(update_info_cancel_btn)

    # 展示框
    show_text_edit = QTextEdit(oa_request_window)
    show_text_edit.show()
    oa_request_layout.addWidget(show_text_edit)

    # 返回按钮定义
    button_back = QPushButton('返回', oa_request_window)
    button_back.setShortcut(Qt.Key_Escape)
    button_back.clicked.connect(lambda: (choice_window.show(), oa_request_window.deleteLater()))
    oa_request_layout.addWidget(button_back)


class FlushCookieThread(QThread):
    """
    刷新按钮进程
    """
    show_text_signal = pyqtSignal(str)
    def __init__(self):
        super(FlushCookieThread, self).__init__()


    def set_info(self, user: str, password: str):
        self.user = user
        self.password = password

    def run(self) -> None:
        try:
            self.emit_show_text('正在刷新cookie...请不要按其他按钮')
            download_headers(self.user, self.password)
            self.emit_show_text('刷新完成')
        except Exception as e:
            self.emit_show_text(e.__str__())

    @pyqtSlot(str)
    def emit_show_text(self, txt):
        self.show_text_signal.emit(txt)


class UpdateInfoThread(QThread):
    """
    下载人员信息进程
    """
    show_text_signal = pyqtSignal(str)

    def __init__(self):
        super(UpdateInfoThread, self).__init__()

    def set_info(self, interval: float):
        self.interval = interval
        self.api_url = 'https://oa.synyi.com/api/hrm/resource/getResourceCard?operation=getResourceBaseView&id='

        FileRead.mkdir('jsons')
        with open('jsons/headers.json', 'r', encoding='utf-8') as f:
            self.headers = dict(json.load(f))


    def run(self) -> None:
        """
        完成人员信息id遍历及下载
        :return:
        """
        # 初始化id
        id = 1
        # 允许连续30个为空的id
        wait_num = 30
        # 当前为连续空的id数
        cur_null_num = 0

        # 存储的json
        infos_json = {}

        # 开始遍历
        begin_time = time.time()
        while True:
            response = requests.get(self.api_url + id.__str__(), headers=self.headers)
            cardinfo = CardInfos(response.text)
            # 输出提示
            self.emit_show_text(f'id({id}):正在读取{cardinfo.get_info_name().get("姓名")}的数据')
            # 若当前id为空
            if cardinfo.get_info_name().get("姓名") == '':
                cur_null_num += 1
                if cur_null_num >= wait_num:
                    break
            else:
                infos_json.update({id: cardinfo.get_cardinfo_dict()})

            time.sleep(self.interval)
            id += 1

        max_id = max([int(x) for x in infos_json.keys()])
        end_time = time.time()
        show_text = f'读取结束,耗时约{round(end_time-begin_time)}秒，合计约{round((end_time-begin_time)/60)}分钟\n' \
                    + f'目前id为{max_id.__str__()}, 共读取{len(infos_json).__str__()}条信息'
        self.emit_show_text(show_text)
        FileRead.write_info_json(infos_json)


    @pyqtSlot(str)
    def emit_show_text(self, txt):
        self.show_text_signal.emit(txt)



def download_headers(user: str, password: str):
    """
    获取cookie拼接为刷接口的header并写到文件headers.json
    :return:
    """
    url = 'https://oa.synyi.com'

    # 下载chrome的driver
    service = Service(executable_path=ChromeDriverManager().install())
    # 不展示浏览器界面
    option = webdriver.ChromeOptions()
    option.add_argument("headless")

    driver = webdriver.Chrome(service=service, options=option)
    driver.get(url)

    # 完成登录
    while True:
        try:
            driver.find_element(By.ID, 'loginid')
        except Exception as e:
            continue

        driver.find_element(By.ID, 'loginid').send_keys(user)
        driver.find_element(By.ID, 'userpassword').send_keys(password)
        driver.find_element(By.ID, 'submit').click()
        break
    time.sleep(2)

    # 通过判断是否还存在登录框来判断登录成功
    try:
        driver.find_element(By.ID, 'loginid')
        raise Exception('登录失败')
    except selenium.common.NoSuchElementException:
        pass

    # 获取cookie
    cookie = ''
    for i in driver.get_cookies():
        cookie += i['name'] + '=' + i['value'] + ';'
    # 退出浏览器
    driver.quit()

    # 拼接headers
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=utf-8',
        'referer': 'https://oa.synyi.com/spa/hrm/index_mobx.html',
        'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    headers.update({'cookie': cookie})

    with open('jsons/headers.json', 'w', encoding='utf-8') as f:
        json.dump(headers, f)


class CardInfos:
    """
    对接口返回的信息卡片json串进行解析

    """

    def __init__(self, info: str):
        self.info: json = json.loads(info)

    def get_info_name(self) -> dict:
        """
        姓名
        :return:
        """
        try:
            name = [x.get('value') for x in self.info.get('result')[0].get('items') if x.get('name') == 'lastname'][0]
        except Exception as e:
            name = ''
        return {'姓名': name}

    def get_info_work_code(self) -> dict:
        """
        工号
        :return:
        """
        try:
            work_code = \
                [x.get('value') for x in self.info.get('result')[0].get('items') if x.get('name') == 'workcode'][0]
        except Exception as e:
            work_code = ''
        return {'工号': work_code}

    def get_info_sex(self) -> dict:
        """
        性别
        :return:
        """
        try:
            sex = [x.get('value') for x in self.info.get('result')[0].get('items') if x.get('name') == 'sex'][0]
        except Exception as e:
            sex = ''
        return {'性别': sex}

    def get_info_department(self) -> dict:
        """
        部门
        :return:
        """
        try:
            department = re.sub(r'<[^>]*>', '', [x.get('value') for x in self.info.get('result')[0].get('items') if
                                                 x.get('name') == 'orginfo'][0])
        except Exception as e:
            department = ''
        return {'部门': department}

    def get_info_post(self) -> dict:
        """
        岗位
        :return:
        """
        try:
            post = re.sub(r'<[^>]*>', '',
                          [x.get('value') for x in self.info.get('result')[3].get('items') if x.get('label') == '岗位'][
                              0])
        except Exception as e:
            post = ''
        return {'岗位': post}

    def get_info_duty(self) -> dict:
        """
        职位
        :return:
        """
        try:
            duty = [x.get('value') for x in self.info.get('result')[3].get('items') if x.get('label') == '职务'][0]
        except Exception as e:
            duty = ''
        return {'职位': duty}

    def get_info_location(self) -> dict:
        """
        办公地点
        :return:
        """
        try:
            location = str.replace(
                [x.get('value') for x in self.info.get('result')[3].get('items') if x.get('label') == '办公地点'][0],
                '&nbsp;', '')
        except Exception as e:
            location = ''
        return {'办公地点': location}

    def get_info_employee_rank(self) -> dict:
        """
        员工职级old
        :return:
        """
        try:
            employee_rank = \
                [x.get('value') for x in self.info.get('result')[3].get('items') if x.get('label') == '员工职级old'][0]
        except Exception as e:
            employee_rank = ''
        return {'员工职级old': employee_rank}

    def get_info_employee_form(self) -> dict:
        """
        聘用形式
        :return:
        """
        try:
            employee_form = \
                [x.get('value') for x in self.info.get('result')[3].get('items') if x.get('label') == '聘用形式'][0]
        except Exception as e:
            employee_form = ''
        return {'聘用形式': employee_form}

    def get_info_probation_status(self) -> dict:
        """
        转正状态
        :return:
        """
        try:
            probation_status = \
                [x.get('value') for x in self.info.get('result')[3].get('items') if x.get('label') == '转正状态'][0]
        except Exception as e:
            probation_status = ''
        return {'转正状态': probation_status}

    def get_info_direct_superior_name(self) -> dict:
        """
        直接上级姓名
        :return:
        """
        try:
            direct_superior_name = \
                [x.get('showName') for x in self.info.get('result')[1].get('items')[3].get('accountinfo') if
                 x.get('name') == 'managerid'][0]
        except Exception as e:
            direct_superior_name = ''
        return {'直接上级姓名': direct_superior_name}

    def get_info_direct_superior_id(self) -> dict:
        """
        直接上级id
        :return:
        """
        try:
            direct_superior_workcode = \
                [x.get('value') for x in self.info.get('result')[1].get('items')[3].get('accountinfo') if
                 x.get('name') == 'managerid'][0]
        except Exception as e:
            direct_superior_workcode = ''
        return {'直接上级id': direct_superior_workcode}

    def get_info_employee_status(self) -> dict:
        """
        员工状态
        :return:
        """
        try:
            employee_status = [x.get('value') for x in self.info.get('result')[1].get('items')[3].get('accountinfo') if
                               x.get('name') == 'status'][0]
        except Exception as e:
            employee_status = ''
        return {'员工状态': employee_status}

    def get_info_createdate(self) -> dict:
        """
        创建时间
        :return:
        """
        try:
            createdate = [x.get('value') for x in self.info.get('result')[1].get('items')[3].get('accountinfo') if
                          x.get('name') == 'createdate'][0]
        except Exception as e:
            createdate = ''
        return {'创建时间': createdate}

    def get_info_lastmoddate(self) -> dict:
        """
        最后修改日期
        :return:
        """
        try:
            lastmoddate = [x.get('value') for x in self.info.get('result')[1].get('items')[3].get('accountinfo') if
                           x.get('name') == 'lastmoddate'][0]
        except Exception as e:
            lastmoddate = ''
        return {'最后修改日期': lastmoddate}

    def get_info_mobile_phone(self) -> dict:
        """
        联系电话
        :return:
        """
        try:
            mobile_phone = \
                [x.get('value') for x in self.info.get('result')[4].get('items') if x.get('type') == 'mobile'][0]
        except Exception as e:
            mobile_phone = ''
        return {'联系电话': mobile_phone}

    def get_info_email(self):
        """
        邮箱
        :return:
        """
        try:
            email = re.sub(r'<[^>]*>', '', [x.get('value') for x in self.info.get('result')[4].get('items') if
                                            x.get('type') == 'email'][0])
        except Exception as e:
            email = ''
        return {'邮箱': email}

    def get_cardinfo_dict(self) -> dict:
        """
        获取信息字典
        :return:
        """
        cardinfo_dict = {}
        for method in self.get_methods():
            cardinfo_dict.update(eval('self.' + method)())
        return cardinfo_dict

    def get_cardinfo_text(self) -> str:
        cardinfo_text = ''
        type_list = ['姓名', '部门', '性别', '工号', '邮箱', '直接上级姓名', '直接上级id', '职位', '岗位', '聘用形式',
                     '员工职级old', '办公地点', '联系电话', '转正状态', '员工状态', '创建时间', '最后修改日期']

        cardinfo_dict = self.get_cardinfo_dict()
        for key in type_list:
            cardinfo_text += f'{key}: {cardinfo_dict.get(key)}\n'
        return cardinfo_text

    def print_cardinfo_text(self):
        """
        返回信息文本
        :return:
        """
        print(self.get_cardinfo_text())

    def get_methods(self) -> list:
        """
        获取当前类全部获取类方法名
        :return:
        """
        methods = sorted(
            [x for x in list(filter(lambda m: not m.startswith("_") and callable(getattr(self, m)), dir(self))) if
             x[:8] == 'get_info'])
        return methods


def request_cardinfo_by_id(id: int):
    """
    按id刷接口获取人员信息
    :param id:
    :return:
    """
    # 读取headers
    if not os.path.exists('jsons/headers.json'):
        download_headers()

    with open('jsons/headers.json', 'r', encoding='utf-8') as f:
        headers = dict(json.load(f))

    # 请求接口
    api_url = 'https://oa.synyi.com/api/hrm/resource/getResourceCard?operation=getResourceBaseView&id='
    response = requests.get(api_url + id.__str__(), headers=headers)
    if response.status_code != 200:
        raise Exception('请求接口失败')

    source_json = response.text
    return CardInfos(source_json)
