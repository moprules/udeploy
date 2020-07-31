# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import shutil

# Название папки где будут храниться демоны
DEMON_FOLDER = '/etc/systemd/system'

def get_python(executable=None):
    if not executable:
        return shutil.which('python3')

    return shutil.which(executable)

def make_service_file(name_service, executable, description=None):
    """Создаёт файл сервиса"""

    if not description:
        description = f"My App Service: {name_service}"

    service_content = f"""
[Unit]
Description={description}
After=syslog.target
After=network.target

[Service]
Type=simple
ExecStart={executable}
WorkingDirectory={os.getcwd()}
Restart=always

[Install]
WantedBy=multi-user.target
"""
    name_file_service = name_service + os.extsep + 'service'
    with open(name_file_service, mode='w', encoding='utf-8') as f:
        f.write(service_content)
    
    # возвращает имя файла сервиса
    return name_file_service


def parse_args(args):
    parser = dict()

    iterable = iter(args)

    try:
        while True:
            key = next(iterable)
            item = next(iterable)
            parser[key] = item
    except StopIteration:
        pass

    return parser


def main():
    # имя сервиса - имя текущей директории проекта
    name_service = os.path.basename(os.getcwd())
    
    args = sys.argv[1:]

    if len(args) == 1:
        # лучше заменить на subprocess
        command = args[0]
        if command in ('start', 'stop', 'enable', 'disable', 'restart', 'status'):
            os.system(f'systemctl {command} {name_service}')
        elif command == "remove":
            trash = f"{DEMON_FOLDER}{os.sep}{name_service}{os.extsep}service"
            print('remove files:', trash, sep="\n")
            # Останавливаем сервис
            os.system(f'systemctl stop {name_service}')
            # Удаляем файл сервиса
            os.remove(trash)
            # говорим systemd увидеть изменения
            os.system("systemctl daemon-reload")
        else:
            file_to_demon = args[0]

            if not os.path.isfile(file_to_demon):
                print(f'ФАЙЛА с именем: {os.path.abspath(file_to_demon)}\nНЕ существует или он не является файлом')
                exit()
    
            name_service_file = make_service_file(name_service, get_python()+' '+ file_to_demon)

            # перемещаем файлы в директорию где демоны
            shutil.move(name_service_file, DEMON_FOLDER)

            # говорим systemd чтобы он проверил конфиги и увидел новый сервис
            os.system("systemctl daemon-reload")
    else:
        print('Неправильное число аргументов')
