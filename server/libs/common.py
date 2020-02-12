import json
import struct
import configparser
import os
import sys
import math
import hashlib
import queue
from threading import Thread
from conf import settings


class Head:
    '''
    报头
    '''
    coding = settings.coding

    def __init__(self, socket, head_dic):
        self.socket = socket
        self.head_dic = head_dic

    def pack(self):               # 制作报头

        head_json = json.dumps(self.head_dic)
        head_json_bytes = bytes(head_json, self.coding)
        head_struct = struct.pack('i', len(head_json_bytes))
        self.socket.send(head_struct)
        self.socket.send(head_json_bytes)

    @classmethod
    def unpack(cls, socket):           # 解包
        head_struct = socket.recv(4)
        if not head_struct: return
        head_len = struct.unpack('i', head_struct)[0]
        head_json = socket.recv(head_len).decode(cls.coding)
        head_dic = json.loads(head_json)

        return head_dic


def sign_in(username, password, disk):
    user_path = settings.user_path
    home_path = settings.home_path
    os.mkdir(home_path)
    conf = configparser.ConfigParser()
    conf.read(user_path)
    conf.add_section(username)
    conf[username]['password'] = password
    conf[username]['disk_limit'] = disk
    conf[username]['home'] = home_path
    conf.write(open(user_path, 'w'))


def hs(args):
    '''
    哈希模块
    :param args:
    :return: 哈希值
    '''
    m = hashlib.md5()
    if type(args) == bytes:
        m.update(args)
    else:
        m.update(args.encode('utf8'))
    return m.hexdigest()


def progress_bar(recv_size, filesize):
    '''
    进度条
    :param recv_size: 已接收文件的大小
    :param filesize: 文件大小
    :return:
    '''

    s = ('\r%d%%  %s' % (math.floor(recv_size / filesize * 100), '#' * math.floor(recv_size / filesize * 100)))
    sys.stdout.write(s)
    sys.stdout.flush()


class ThreadPool:
    '''
    线程池
    '''

    def __init__(self, max_num=10):
        self.queue = queue.Queue(max_num)
        for i in range(max_num):            # 向队列填充线程类
            self.queue.put(Thread)

    def get_thread(self):       # 取数据
        return self.queue.get()

    def add_thread(self):           # 添加数据
        self.queue.put(Thread)

