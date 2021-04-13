# python 3.9
import argparse
from dto10 import DTO10
from libfptr10 import IFptr
from ecr import ECR
import helper



driver = DTO10()
kkt = ECR(driver)

# Запрос общей информации о ККТ
kkt.get_information_kkt()


# Добавил аргументы для запуска
parser = argparse.ArgumentParser()
parser.add_argument("--fiscal", "-f", help="- Фискализация кассы", action="store_true")
parser.add_argument("--info", "-i", help="- Печать информации о ККТ", action="store_true")
parser.add_argument("--technical", "-t", help="- Технологическое обнуление", action="store_true")
parser.add_argument("--reboot", "-r", help="- Перезагрузка кассы", action="store_true")
parser.add_argument("--initialization", "-in", help="- Инициализация ККТ", action="store_true")
parser.add_argument("--write_licenses", "-w", help="- Записать лицензии/коды защиты  в ККТ", action="store_true")
parser.add_argument("--write_uin_keys", "-u", help="- Запись ключей и uin", action="store_true")
args = parser.parse_args()

# Печать информации
if args.info:
    if driver.print_information_kkt() != IFptr.LIBFPTR_OK:
        print(f'Ошибка печати информации о ККТ: {kkt.dto10.error_description()}')

# Перезагрузка кассы
if args.reboot and driver.reboot_device() != IFptr.LIBFPTR_OK:
    print(f'Перезагрузка ККТ: {driver.error_description()}')

# Технологическое обнуление кассы
if args.technical and driver.technological_reset() != IFptr.LIBFPTR_OK:
    print(f'Ошибка технологического обнуления: {driver.error_description()}')

# Инициализация устройства
if args.initialization and kkt.check_initialisation_kkt() != IFptr.LIBFPTR_OK:
    print(f'Инициализация ККТ: {driver.error_description()}')

# Запись лицензий/кодов защиты в ККТ
if args.write_licenses and kkt.write_licenses():
    print(driver.error_description())

# Процесс фискализации кассы
if args.fiscal and kkt.process_fiscalisation() != IFptr.LIBFPTR_OK:
    print(driver.error_description())

# Запись ключей и uin в ккт
if args.write_uin_keys and kkt.enter_uin_from_file != IFptr.LIBFPTR_OK:
    print(driver.error_description())