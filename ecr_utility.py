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
parser.add_argument("--base_config", "-b", help="- Базовая настройка кассы", action="store_true")
parser.add_argument("--clear_fn", "-c", help="- Инициализация ФНа", action="store_true")
parser.add_argument("--info", "-i", help="- Печать информации о ККТ", action="store_true")
parser.add_argument("--technical", "-t", help="- Технологическое обнуление", action="store_true")
parser.add_argument("--reboot", "-r", help="- Перезагрузка кассы", action="store_true")
parser.add_argument("--initialization", "-in", help="- Инициализация ККТ", action="store_true")
parser.add_argument("--write_licenses", "-w", help="- Записать лицензии/коды защиты  в ККТ", action="store_true")
parser.add_argument("--write_uin_keys", "-k", help="- Запись ключей и uin", action="store_true")
args = parser.parse_args()

# Инициализация ФНа
if args.clear_fn:
    kkt.clear_fn_kkt()

# Печать информации
if args.info and driver.print_information_kkt() != IFptr.LIBFPTR_OK:
    print(f'Ошибка печати информации о ККТ: {kkt.dto10.error_description()}')

# Перезагрузка кассы
if args.reboot:
    driver.reboot_device()

# Технологическое обнуление кассы
if args.technical:
    driver.technological_reset()

# Инициализация устройства
if args.initialization and kkt.check_initialisation_kkt() != IFptr.LIBFPTR_OK:
    print(f'Инициализация ККТ: {driver.error_description()}')

# Запись лицензий/кодов защиты в ККТ
if args.write_licenses and kkt.write_licenses():
    print(f'Запись лицензий: {driver.error_description()}')

# Процесс фискализации кассы
if args.fiscal and kkt.process_fiscalisation() != IFptr.LIBFPTR_OK:
    print(driver.error_description())

# Базовая настройка кассы
if args.base_config and kkt.base_config_kkt() != IFptr.LIBFPTR_OK:
    print(driver.error_description())

# Запись ключей и uin в ккт
if args.write_uin_keys:
    kkt.enter_uin_from_file()
