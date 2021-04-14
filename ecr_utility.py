# python 3.9
import argparse
from dto10 import DTO10
from ecr import ECR




driver = DTO10()
kkt = ECR(driver)

# Запрос общей информации о ККТ
kkt.get_information_kkt()


# Добавил аргументы для запуска
parser = argparse.ArgumentParser()
parser.add_argument("--fiscal", "-f", help="- Фискализация кассы", action="store_true")
parser.add_argument("--full_base_config", "-b", help="- Полная базовая настройка кассы", action="store_true")
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
if args.info:
    kkt.print_info_kkt()

# Перезагрузка кассы
if args.reboot:
    kkt.reboot_device_kkt()

# Технологическое обнуление кассы
if args.technical:
    kkt.technical_reset_kkt()

# Инициализация устройства
if args.initialization:
    kkt.check_initialisation_kkt()

# Запись лицензий/кодов защиты в ККТ
if args.write_licenses:
    kkt.write_licenses()

# Процесс фискализации кассы
if args.fiscal:
    kkt.process_fiscalisation()

# Полная базовая настройка кассы
if args.base_config:
    kkt.full_base_config_kkt()

# Запись ключей и uin в ккт
if args.write_uin_keys:
    kkt.enter_uin_from_file()
