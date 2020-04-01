import sys
import os
import stat
import shutil
import subprocess

DEMON_FOLDER = '/etc/systemd/system'

def get_python(executable=None):
    if not executable:
        return shutil.which('python3')

    return shutil.which(executable)


def make_demon_script(name_service, commands, add_cwd=False):

    exec_content=["#!/bin/bash"]

    if add_cwd:
        exec_content.append("cd " + os.getcwd())

    exec_content.extend(commands)
    exec_content = map((lambda item: item + '\n'), exec_content)

    # запишев в файл содержимое 
    name_exec_file = name_service + os.extsep + 'sh'
    with open(name_exec_file, mode='w', encoding='utf-8') as f:
        f.writelines(exec_content)
    
    # дадим права на исполнение нашему файлу
    st = os.stat(name_exec_file)
    os.chmod(name_exec_file, st.st_mode | stat.S_IEXEC)

    # возвращает имя исполняемого файла
    return name_exec_file


def make_service_file(name_service, executable, description=None):

    if not description:
        description = f"My App Service: {name_service}"

    service_content = \
f"""[Unit]
Description={description}
After=network.target

[Service]
Type=simple
ExecStart={DEMON_FOLDER}{os.sep}{executable}
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


if __name__ == "__main__":

    # имя сервиса - имя текущей директории проекта
    name_service = os.path.basename(os.getcwd())
    
    args = sys.argv[1:]

    if len(args) == 1:
        # лучше заменить на subprocess
        command = args[0]
        if command in ('start', 'stop', 'enable', 'disable', 'restart', 'status'):
            os.system(f'systemctl {command} {name_service}')
        elif command == "remove":
            print('remove files:',
                 f'{DEMON_FOLDER}/{name_service + os.extsep + "sh"}',
                 f'{DEMON_FOLDER}/{name_service + os.extsep + "service"}', sep='\n')
            os.system(f'rm -f {DEMON_FOLDER}/{name_service + os.extsep + "service"}')
            os.system(f'rm -f {DEMON_FOLDER}/{name_service + os.extsep + "sh"}')
        else:
            file_to_demon = args[0]

            if not os.path.isfile(file_to_demon):
                print(f'ФАЙЛА с именем: {os.path.abspath(file_to_demon)}\nНЕ существует или он не является файлом')
                exit()
    
            name_script_file = make_demon_script(name_service, [get_python()+' '+ file_to_demon], add_cwd=True)
            name_service_file = make_service_file(name_service, name_script_file)

            # перемещаем файлы в директорию где демоны
            shutil.move(name_script_file, DEMON_FOLDER)
            shutil.move(name_service_file, DEMON_FOLDER)
    else:
        print('Неправильное число аргументов')