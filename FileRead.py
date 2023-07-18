import json
import os.path
import datetime
import shutil

def read_data_json():
    """
    读取data.json
    :return:
    """
    if not os.path.exists('jsons/data.json'):
        raise Exception('不存在data.json文件')

    with open('jsons/data.json', 'r') as f:
        data = json.load(f)
    dates = list(data.keys())
    dates.sort()
    return data, dates


def write_data_json(write_data: dict):
    """
    写入data.json
    :param write_data:
    :return:
    """
    if not os.path.exists('jsons'):
        os.mkdir('jsons')

    with open('jsons/data.json', 'w') as f:
        json.dump(write_data, f)


def read_info_json():
    """
    读取OA爬取的人员信息json
    :return:
    """
    if not os.path.exists('jsons/infos.json'):
        raise Exception('不存在infos.json文件')

    with open('jsons/infos.json', 'r') as f:
        data: dict = json.load(f)
    # 返回更新日期和info {id:{info...}}
    return list(data.keys())[0], list(data.values())[0]


def write_info_json(info_json: dict):

    if not os.path.exists('jsons'):
        os.mkdir('jsons')

    with open('jsons/infos.json', 'w', encoding='utf-8') as f:
        today = datetime.date.today().__str__()
        json.dump({today: info_json}, f)


def backup_info_json():
    if not os.path.exists('history'):
        os.mkdir('history')

    date, data = read_info_json()
    with open(f'history/info{date}.json', 'w', encoding='utf-8') as f:
        json.dump({date: data}, f)


def is_exists_login_json():
    return os.path.exists('jsons/login.json')


def write_login_json(user: str, password: str):
    """
    保存登录信息
    :return:
    """
    if not os.path.exists('jsons'):
        os.mkdir('jsons')

    with open('jsons/login.json', 'w', encoding='utf-8') as f:
        json.dump({'user': user, 'password': password}, f)


def read_login_json():
    """
    读取登录信息
    :return:
    """
    if not os.path.exists('jsons/login.json'):
        raise Exception('不存在login.json文件')
    with open('jsons/login.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('user'), data.get('password')


def import_file(file_path: str, file_name: str):
    try:
        shutil.copyfile(file_path, os.path.curdir + '/'+file_name)
    except Exception as e:
        raise Exception(e.__str__())