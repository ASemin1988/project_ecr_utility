# python 3.9
import argparse
from dto10 import DTO10
from libfptr10 import IFptr
from ecr import ECR
import config
import os
import json_work
from constants import PLATFORM_V5, PLATFORM_V2_5


driver = DTO10()
kkt = ECR(driver)


# Запрос общей информации о ККТ
kkt.get_information_kkt()


def write_licenses():
    data_dict = json_work.open_json_file(name=os.path.join(config.path_data_dict, '0' + driver.get_model_information_kkt(),
                driver.get_serial_number() + config.path_format_json))

    if kkt.platform == PLATFORM_V5:
        lic_list = data_dict['licensesPlatform50']
        for lic in lic_list:
            driver.write_licenses(value=lic['license'])
        print(f'Лицензии записаны')

    if kkt.platform == PLATFORM_V2_5 and kkt.get_firmware_version:
        lic_list = data_dict['licensesPlatform25']
        for lic in lic_list:
            driver.write_licenses(value=lic['data'])
        print(f'Лицензии записаны')


def write_security_codes():
    data_dict = json_work.open_json_file(
            name=os.path.join(config.path_data_dict, '0' + driver.get_model_information_kkt(),
            driver.get_serial_number() + config.path_format_json))

    if kkt.platform == PLATFORM_V2_5:
        codes_list = data_dict['protectionCodes']
        for codes in codes_list:
            driver.write_licenses(value=codes['codeValue'], number=codes['codeNumber'])
    print(f'Коды защиты записаны')


def check_initialisation_kkt():
    data_dict = json_work.open_json_file(
        name=os.path.join(config.path_data_dict, '0' + driver.get_model_information_kkt(),
                                    driver.get_serial_number() + config.path_format_json))

    for lic in data_dict:
        driver.write_licenses(value=lic['serialNumber'], number=['macAddress'])
    print(f'Инициализация ККТ')


# Добавил аргументы для запуска
parser = argparse.ArgumentParser()
parser.add_argument("--fiscal", "-f", help="- Фискализация кассы", action="store_true")
parser.add_argument("--info", "-i", help="- Печать информации о ККТ", action="store_true")
parser.add_argument("--technical", "-t", help="- Технологическое обнуление", action="store_true")
parser.add_argument("--reboot", "-r", help="- Перезагрузка кассы", action="store_true")
parser.add_argument("--initialization", "-in", help="- Инициализация ККТ", action="store_true")
parser.add_argument("--write_licenses", "-w", help="- Записать лицензии/коды защиты  в ККТ", action="store_true")
args = parser.parse_args()


# Печать информации
if args.info and driver.print_information_kkt() != IFptr.LIBFPTR_OK:
    print(f'Ошибка печати информации о ККТ: {kkt.dto10.error_description()}')


# Перезагрузка кассы
if args.reboot and driver.reboot_device() != IFptr.LIBFPTR_OK:
    print(f'Перезагрузка ККТ: {kkt.dto10.error_description()}')


# Технологическое обнуление кассы
if args.technical and driver.technological_reset() != IFptr.LIBFPTR_OK:
    print(f'Ошибка технологического обнуления: {kkt.dto10.error_description()}')


# Инициализация устройства
if args.initialization and driver.initialization_kkt() != IFptr.LIBFPTR_OK:
    print(f'Инициализация ККТ: {kkt.dto10.error_description ()}')


# Запись лицензий/кодов защиты в ККТ
if args.write_licenses and write_licenses() != IFptr.LIBFPTR_OK:
    print(f'{kkt.dto10.error_description()}')


if args.fiscal and kkt.process_fiscalisation() != IFptr.LIBFPTR_OK:
    print(f'{kkt.dto10.error_description()}')

