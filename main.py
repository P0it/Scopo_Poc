import binascii
import csv
import sys
from datetime import datetime
import yaml
from elasticsearch import helpers, Elasticsearch


def es_insert():
    es = Elasticsearch('http://localhost:9200')

    def generate_docs():
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                doc = {
                    '_index': 'mon_dev_info',
                    '_source': {
                        'dev_ip': row['dev_ip'],
                        'dev_name': row['dev_name'],
                        'group': row['group'],
                        'type': row['type'],
                        'dev_hw': row['dev_hw'],
                        'dev_os': row['dev_os'],
                        'user': row['user'],
                        'pwd': binascii.hexlify(bytes(row['pwd'], 'utf-8')).decode('utf8'),
                        'enable': binascii.hexlify(bytes(row['enable'], 'utf-8')).decode('utf8'),
                        'community': binascii.hexlify(bytes(row['community'], 'utf-8')).decode('utf8'),
                        'port': int(row['port']),
                        'con_status': 'yet',
                        'mon_status': 'yet',
                        'set_time': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    },
                }
                yield doc

    helpers.bulk(es, generate_docs())

    print("--- elasticsearch saved! ---")


def yaml_file():
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)

        device_list = []
        for row in reader:
            device = {row['dev_name']: {'type': row['type'],
                                        'os': row['dev_os'],
                                        'alias': row['dev_ip'],
                                        'connections': {
                                            'cli': {
                                                'protocol': 'ssh',
                                                'ip': row['dev_ip'],
                                                'port': int(row['port'])}},
                                        'credentials': {
                                            'default': {
                                                'username': row['user'],
                                                'password': row['pwd']},
                                            'enable': row['enable']}}}
            # Since 'dict' type  does not support 'append or insert'
            device_list.append(device)

        # Covert list into dict
        device_dict = {}
        for i in device_list:
            device_dict.update(i)

        result = {'devices': device_dict}

    # dict to yaml
    file = open("dev_testbed.yaml", "w")
    yaml.dump(result, file)
    file.close()
    print("--- yaml file saved! ---")


def dev_ip():
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        device_ip = []
        for row in reader:
            device_ip.append(row['dev_ip'])

    with open('dev_ips.py', 'w') as fp:
        fp.write('devices = [ \n')
        for item in device_ip:
            fp.write(f"'{item}',\n")
        fp.write(']')
        print("--- py file saved! ---")


def info_update():
    es_insert()
    yaml_file()
    dev_ip()


# 메인 실행 함수
if len(sys.argv) < 2:

    print('--- Please run with csv file! ---')

elif len(sys.argv) == 2:
    file_path = sys.argv[1]
    info_update()

else:
    print("Only single csv file is required.")
