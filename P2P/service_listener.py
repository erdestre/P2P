import socket
import logging
from sys import stdout
import json

PORT = 5000
FILE_OUT = 'content_dict.txt'
BUF_SIZE = 64 * 1024


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip_addr = s.getsockname()[0]
    s.close()
    return ip_addr


def json_to_dict(announcer_data):
    content_dict = {}
    announcer_json = json.loads(announcer_data)

    for filename in announcer_json['files']:
        if filename not in content_dict:
            content_dict[filename] = set()
        content_dict[filename].add(address[0])

    logger.info(content_dict)
    return content_dict


def write_to_file(providers, filename):
    fo = open(filename, "w")
    fo.truncate(0)

    providers_serializable = dict()
    for key, value in providers.items():
        providers_serializable[key] = list(providers[key])

    providers_json = json.dumps(providers_serializable)
    fo.write(providers_json)
    fo.close()


if __name__ == '__main__':
    logging.basicConfig(stream=stdout, level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(name)s]:  %(message)s')
    logger = logging.getLogger('service_listener')

    listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    ip = get_ip_address().split('.')
    ip = '{}.{}.{}.255'.format(ip[0], ip[1], ip[2])
    listener.bind((ip, PORT))
    logger.info('listening on {}:{}'.format(ip, PORT))

    while True:
        data, address = listener.recvfrom(BUF_SIZE)
        annnouncer_data = data.decode()
        logger.info('received message from {}: {}'.format(address[0], annnouncer_data))

        providers_dict = json_to_dict(annnouncer_data)
        write_to_file(providers_dict, FILE_OUT)
