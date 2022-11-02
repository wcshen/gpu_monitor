"""
https://github.com/zhangwenxiao/GPU-Manager
"""
import re
import time
import json
import argparse
from threading import Thread, Lock
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler

import pytz
import datetime

class CustomHandler(BaseHTTPRequestHandler):
    alert_record = { }

    def do_GET(self):
        length = int(self.headers['content-length'])
        info = json.loads(self.rfile.read(length).decode())
        slaver_address, _ = self.client_address
        lock.acquire()
        if slaver_address not in info_record:
            info_record[slaver_address] = {}
        info_record[slaver_address]['info'] = info
        info_record[slaver_address]['timestamp'] = time.time()
        lock.release()
        report_user()
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return


def http_func():
    server = HTTPServer((opt.address, opt.port), CustomHandler)
    print("listening... <Ctrl-C> exit")
    server.serve_forever()


def isExpire(timestamp):
    if time.time() - timestamp > opt.expiretime:
        return True
    return False


def report_user():

    gpu_usage_dict = {}
    lock.acquire()
    for slaver_address in sorted(info_record.keys()):
        if isExpire(info_record[slaver_address]['timestamp']):
            continue
    
        gpu_mem_list = info_record[slaver_address]['info']['gpu']
        gpu_idx = info_record[slaver_address]['info']['gpu_idx']
        ts = info_record[slaver_address]['info']['ts']
        gpu_usage_dict[gpu_idx] = {'ts': ts, 'card_mems':[]}
        for gpu_mem in gpu_mem_list:
            this_card_id = gpu_mem['card_id']
            this_card_mem_per = gpu_mem['mem_percent']
            this_card_mem_free = gpu_mem['mem_free']
            this_card_mem_usg = gpu_mem['mem_usage']
            this_card_mem_total = gpu_mem['mem_total']
            gpu_usage_dict[gpu_idx]['card_mems'].append([this_card_id, this_card_mem_per, this_card_mem_free, this_card_mem_usg, this_card_mem_total])
    lock.release()

    print('=' * 60)
    current_time = "{0:%Y%m%d-%H-%M-%S}".format(datetime.datetime.now(tz=pytz.timezone("Asia/Chongqing")))
    print(current_time)
    idx_order_keys = sorted(gpu_usage_dict)
    for gpu_idx in idx_order_keys:
        cards_mem = gpu_usage_dict[gpu_idx]
        print(f"gpu{gpu_idx} \t\t {cards_mem['ts']}")
        for card_mem in cards_mem['card_mems']:
            print(f"card {card_mem[0]} usage_percent:{card_mem[1]}, mem_free:{card_mem[2]}, mem_usg:{card_mem[3]}, mem_total:{card_mem[4]}")
        print("\n")
    gpu_usage_dict = {}
    return


parser = argparse.ArgumentParser()
parser.add_argument('--address', default = '172.16.0.247', help = 'the ip of server')
parser.add_argument('--port', type = int, default = '5678', help = 'server port, default: 5678')
parser.add_argument('--expiretime', type = int, default = 100, help = 'client expiration time, default: 100s')
opt = parser.parse_args()

info_record = { }
lock = Lock()

http_thread = Thread(target = http_func)
http_thread.start()
