"""
https://github.com/zhangwenxiao/GPU-Manager
"""
import re
import pwd
from ssl import MemoryBIO
import time
import json
import psutil
import argparse
import requests
import subprocess

import pytz
import datetime

# client gpu_idx
gpu_idx = 14

def get_owner(pid):
    try:
        for line in open('/proc/%d/status' % pid):
            if line.startswith('Uid:'):
                uid = int(line.split()[1])
                return pwd.getpwuid(uid).pw_name
    except:
        return None

def get_info():
    time_stamp = "{0:%Y%m%d-%H-%M-%S}".format(datetime.datetime.now(tz=pytz.timezone("Asia/Chongqing")))
    info = { 'gpu': [], 'gpu_idx': gpu_idx, 'ts':time_stamp}
    msg = subprocess.Popen('nvidia-smi', stdout = subprocess.PIPE).stdout.read().decode()
    msg = msg.strip().split('\n')

    # line maybe different with different nvidia-smi versions
    line = 9
    this_card_id = 0
    while True:
        status = re.findall('.*\d+%.*\d+C.*\d+W / +\d+W.* +(\d+)MiB / +(\d+)MiB.* +\d+%.*', msg[line])
        if status == []: break
        mem_usage, mem_total = status[0]
        info['gpu'].append({
            'mem_percent': f"{float(mem_usage)/float(mem_total)*100.0:.1f}%",
            'mem_usage': f"{float(mem_usage)/1024:.1f}GB",
            'mem_free': f"{(float(mem_total)-float(mem_usage))/1024:.1f}GB",
            'mem_total': f"{float(mem_total)/1024:.1f}GB",
            'card_id': this_card_id,
        })
        line += 4
        this_card_id += 1

    return info

parser = argparse.ArgumentParser()
# gpu14 172.16.0.247
parser.add_argument('--address', default = '172.16.0.247', help = 'the ip of server')
parser.add_argument('--port', default = '5678', help = 'server port, default: 5678')
parser.add_argument('--persecond', default = 20, help = 'watch gpu_mem frequency, default:20s')
opt = parser.parse_args()

url = 'http://%s:%s' % (opt.address, opt.port)

while True:
    mean_info = get_info()
    datas = json.dumps(mean_info)
    # print(datas)
    print(f"ts: {mean_info['ts']}")
    for gpu_mem in mean_info['gpu']:
        print(f"card {gpu_mem['card_id']} usage_percent:{gpu_mem['mem_percent']}, mem_free:{gpu_mem['mem_free']}, mem_usg:{gpu_mem['mem_usage']}, mem_total:{gpu_mem['mem_total']}")
    try:
        response = requests.get(url, data = datas)
        print('HTTP status_code: ', response.status_code, '\n')
    except Exception as e:
        print(e)
    time.sleep(opt.persecond)