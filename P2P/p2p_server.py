import socket
import os
from datetime import datetime
import math
import sys
import json
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(name)s]:  %(message)s')
logger = logging.getLogger('p2p_server')

PATH_TO_FILES = 'files_to_host/'
CHUNKS = 'generated_chunks/'
PORT = 5001
BUF_SIZE = 1024 * 1024


def get_now():
    return datetime.now().strftime("%m/%d/%Y_%H:%M:%S")


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip_addr = s.getsockname()[0]
    s.close()
    return ip_addr


def listdir_nohidden(path):
    for f in os.listdir(path):
        if not f.startswith('.'):
            yield f


def split_file_into_5_chunks(file_name):
    logger.info('splitting {} into 5 chunks'.format(file_name))
    file_path = PATH_TO_FILES + file_name
    c = os.path.getsize(file_path)
    chunk_size = math.ceil(math.ceil(c) / 5)

    index = 1
    with open(file_path, 'rb') as infile:
        chunk = infile.read(int(chunk_size))
        while chunk:
            chunkname = os.path.splitext(file_name)[0] + '_' + str(index)
            chunk_addr = CHUNKS + chunkname
            with open(chunk_addr,'wb+') as chunk_file:
                chunk_file.write(chunk)
            index += 1
            chunk = infile.read(int(chunk_size))
    infile.close()


if __name__ == '__main__':
    ip = get_ip_address()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, PORT))
    s.listen(2)
    logger.info('Listening on {}:{}'.format(ip, PORT))

    print('Available files:')
    file_list = list(listdir_nohidden(PATH_TO_FILES))
    for i, c in enumerate(file_list):
        print(str(i) + '\t', c)
    i = int(input('Pick a file to share: '))
    file_name = file_list[i]

    split_file_into_5_chunks(file_name)

    logger.info('ready to accept connections for file {}'.format(file_name))

    while True:
        try:
            conn, addr = s.accept()
            logger.info('connected to client: {}:{}'.format(str(addr[0]), str(addr[1])))
            request = conn.recv(BUF_SIZE)
            logger.info('received request from {}: {}'.format(str(addr[0]), str(request.decode())))
            req_json = json.loads(request)
            chunk_to_upload = req_json["filename"]

            with open(CHUNKS + chunk_to_upload, 'rb') as out:
                conn.send(bytes(out.read()))
                with open("upload_log.txt", 'a') as up_log:
                    up_log.write('[{}] transferred {} to {}\n'.format(get_now(), chunk_to_upload, str(addr[0])))

            logger.info('processed request for {}: {}'.format(str(addr[0]), str(request.decode())))

        except Exception as e:
            print(e.args)
            s.close()
            sys.exit()