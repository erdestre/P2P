import socket
import time
import json
from os import listdir
from os.path import isfile, join
import logging
from sys import stdout

USERNAME = input("Enter username:")
CHUNKS_FPATH = "generated_chunks/"
PORT = 5000


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_addr = s.getsockname()[0]
    s.close()
    return ip_addr


def listdir_nohidden(path):
    for f in listdir(path):
        if not f.startswith('.'):
            yield f


if __name__ == '__main__':
    logging.basicConfig(stream=stdout, level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(name)s]:  %(message)s')
    logger = logging.getLogger('service_announcer')

    announcer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    announcer.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    announcer.settimeout(0.2)

    ip = get_ip_address().split('.')
    ip = '{}.{}.{}.255'.format(ip[0], ip[1], ip[2])
    while True:
        files = list(listdir_nohidden(CHUNKS_FPATH))
        data = {'username': USERNAME, 'files': files}
        json_message = json.dumps(data)

        announcer.sendto(json_message.encode(), (ip, PORT))
        logger.info("message sent to {}: {}".format(ip, json_message))
        time.sleep(60)
