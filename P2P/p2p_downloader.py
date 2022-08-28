import socket
import json
from datetime import datetime
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(name)s]:  %(message)s')
logger = logging.getLogger('p2p_downloader')

PATH_DOWNLOADED_CHUNKS = 'downloaded_chunks/'
PATH_DOWNLOADED_FILES = 'downloaded_files/'
DICT_FILE = 'content_dict.txt'
PORT = 5001
BUF_SIZE = 1024 * 1024


def get_now():
    return datetime.now().strftime("%m/%d/%Y_%H:%M:%S")


def file_to_dict(filename):
    content_dict_file = open(filename, 'rt')
    content_dict = json.load(content_dict_file)
    return content_dict


def merge_chunks(file_name):
    chunk_names = [file_name + '_1', file_name + '_2', file_name + '_3', file_name + '_4', file_name + '_5']
    fname_final = file_name + '.png'

    with open(PATH_DOWNLOADED_FILES + fname_final, 'wb') as outfile:
        for chunk in chunk_names:
            with open(PATH_DOWNLOADED_CHUNKS + chunk, 'rb') as infile:
                outfile.write(infile.read())

    logger.info('merged chunks into {}'.format(fname_final))


if __name__ == '__main__':
    while True:
        content_dict = file_to_dict(DICT_FILE)
        unique_files = list(set(chunk[:len(chunk) - 2] for chunk in content_dict))

        print('Available files to download:')
        for i, c in enumerate(unique_files):
            print(str(i) + '\t', c)

        i = int(input('Pick a file to download: '))
        fname_prefix = unique_files[i]

        req_string = {
            "filename": ""
        }

        dl_count = 0
        dl_files = []
        for i in range(1, 6):
            fname_dl = fname_prefix + '_' + str(i)
            req_string["filename"] = fname_dl
            req_json = json.dumps(req_string)
            for ip in content_dict[fname_dl]:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect((ip, PORT))
                    s.send(bytes(req_json, 'utf-8'))
                    logger.info('sending request {}'.format(req_json))
                    dl_chunk = s.recv(BUF_SIZE)
                    dl_count += 1

                    with open('download_log.txt', 'a') as dl_log:
                        dl_log.write('[{}] downloaded {} from {}\n'.format(get_now(), fname_dl, str(ip)))

                    with open("downloaded_chunks/" + fname_dl, 'wb') as f:
                        f.write(dl_chunk)

                    f.close()
                    s.close()

                    dl_files.append(fname_dl)
                    logger.info('downloaded chunk {}'.format(fname_dl))
                except Exception as e:
                    s.close()
                    logger.error('{}: while downloading {} from {}'.format(e, fname_dl, ip))
                    continue

            if dl_count == 5:
                logger.info('downloaded all 5 chunks')
                dl_count = 0
                merge_chunks(fname_prefix)
                print('\n')