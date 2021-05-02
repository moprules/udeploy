# -*- coding: utf-8 -*-
import sys
import os
import shutil

# Код версии программы
__version__ = "0.0.4"


# Название папки где будут храниться демоны
DEMON_DIR = '/etc/systemd/system'

# Шаблон файла сервиса
SERVICE_TEMPLATE = """[Unit]
Description={description}
After=syslog.target
After=network.target

[Service]
Type=simple
ExecStart={executable}
WorkingDirectory={workdir}
Restart=always

[Install]
WantedBy=multi-user.target
"""

# Вспомогательное сообщение для пользователя
HELP_MESSAGE = f"""
udeploy {__version__}
  --help        : Вывести подсказку
  -f <filename> : Сделать отдельный файл сервисом
  --django      : Сделать Django проект сервисом systemd
  -----------Управление через sytemctl--------------------
  start   : Запустить демон
  enable  : Добавить в автозапуск
  stop    : Остановить демон
  disable : Убрать демон из автозапуска
  remove  : Удалить демон (и все его файлы)
"""


def get_python(executable=None):
    """Получить версию питона"""
    if not executable:
        return shutil.which('python3')

    return shutil.which(executable)


def make_demon(name_service, command, description=None):
    """
    Создаёт файл сервиса
    name_service - имя сервиса
    command - выполняемая комманда как независимый процесс
    description - описание сервиса, опционально
    """
    # Если нет описания
    if not description:
        # Берём описание по умолчанию
        description = f"My App Service: {name_service}"

    # Словарь, чтобы заполнить нужные параметры сервиса
    d = {'description': description,
         'executable': command,
         'workdir': os.getcwd()}

    # содержиммое файла сервиса
    content = SERVICE_TEMPLATE.format(**d)

    # создаём имя файла сервиса
    name_file_service = name_service + os.extsep + 'service'

    # Записываем содержимое в файл сервиса
    # Файл сервиса расположен в текущем рабочем каталоге
    with open(name_file_service, mode='w', encoding='utf-8') as f:
        f.write(content)

    # перемещаем файлы в директорию где демоны
    shutil.move(name_file_service, DEMON_DIR)

    # говорим systemd чтобы он проверил конфиги и увидел новый сервис
    os.system("systemctl daemon-reload")

    # Пишем сообщение об успешном создании демона
    print(f"Демон '{name_service}' успешно создан")


def make_django_demon(name_service):
    """Сделать демон Django проект"""
    # Проверяем есть ли в проекта manage.py файл
    if not os.path.isfile('manage.py'):
        print('Внутри проекта нет управляющего файла')
        print(f'ФАЙЛА с именем: {os.path.abspath("manage.py")}')
        print('НЕ существует или он не является файлом')
    else:
        # Управляющий файл существует
        # Собираем для него комманду
        command = f'{get_python()} manage.py runserver 0.0.0.0:80'
        # Создаём нужный демон
        make_demon(name_service, command)


def make_demon_from_file(name_service, file_to_demon):
    """Превращает простой файл в демон"""
    # Проверяем вообще существует ли такой файл
    if not os.path.isfile(file_to_demon):
        print(f'ФАЙЛА с именем: {os.path.abspath(file_to_demon)}')
        print('НЕ существует или он не является файлом')
    else:
        # Файл есть, собираем комманду для запуска
        command = f'{get_python()} {file_to_demon}'
        # Создаём нужный демон
        make_demon(name_service, command)


def systemd_shell(name_service, command):
    """Оболочка для работы с коммандами systemd"""
    # если команда есть среди стандартных
    if command in ('start', 'stop', 'enable', 'disable', 'restart', 'status'):
        # Просто передаём управление systemd
        os.system(f'systemctl {command} {name_service}')
    elif command == "remove":
        # Отдельная комманда, чтобы проще удалить сервис
        # Останавливаем сервис
        os.system(f'systemctl stop {name_service}')
        trash = f"{DEMON_DIR}{os.sep}{name_service}{os.extsep}service"
        print('remove files:', trash, sep="\n")
        # Удаляем файл сервиса
        os.remove(trash)
        # говорим systemd увидеть изменения
        os.system("systemctl daemon-reload")
    else:
        # Неизвестная комманда. Говорим об этом
        print(f"Неизвестная комманда '{command}' для systemctl")


def main():
    # имя сервиса - имя текущей директории проекта
    name_service = os.path.basename(os.getcwd())

    # Из аргкментов коммандной строки убираем ненужное название
    # Вызывающей программы
    args = sys.argv[1:]

    # Если не передали ни одного аргумента
    if not args:
        # Выводим вспомогательное сообщение
        print(HELP_MESSAGE)
    elif len(args) == 1:
        # Если передали только один аргумент
        # Это либо просьба вывести вспомогательное сообщение
        if args[0] == '--help':
            print(HELP_MESSAGE)
        elif args[0] == '--django':
            # Либо сделать Django проект сервисом
            make_django_demon(name_service)
        else:
            # Иначе обращаются напрямую к systemd
            systemd_shell(name_service, command=args[0])
    elif len(args) == 2:
        # Если передали ровно два аргумента
        # Проверяем есть ли известные для нас флаги
        # Если хотят сделать из файла демон
        if '-f' in args:
            # Удаляем из аргументов строку флага
            args.remove('-f')
            # Теперь точно всегда имя файла будет на первом месте
            file_to_demon = args[0]
            # Создаём демон из файла
            make_demon_from_file(name_service, file_to_demon)
        else:
            # Других флагов пока нет, поэтому выводим сообщение об неверном вводе
            print(f"Неправильные аргументы: {' '.join(args)}")
            print('Для подсказки используйте "udeploy --help"')
    else:
        # Ввели 3 и более аргументов, выводим сообщение об ошибке
        print(f"Неправильное число аргументов: {' '.join(args)}")
        print('Для подсказки используйте "udeploy --help"')
