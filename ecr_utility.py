# python 3.9
import argparse
from dto10 import DTO10
from libfptr10 import IFptr
from ecr import ECR


driver = DTO10()
kkt = ECR(driver)

# Запрос общей информации о ККТ
kkt.check_information_kkt()


# Добавил аргументы для запуска
parser = argparse.ArgumentParser()
parser.add_argument("--fiscal", "-f", help="- Фискализация кассы", action="store_true")
parser.add_argument("--info", "-i", help="- Печать информации о ККТ", action="store_true")
parser.add_argument("--technical", "-t", help="- Технологическое обнуление", action="store_true")
parser.add_argument("--reboot", "-r", help="- Перезагрузка кассы", action="store_true")
parser.add_argument("--initialization", "-in", help="- Инициализация ККТ", action="store_true")
args = parser.parse_args()

# Печать информации
if args.info and driver.print_information_kkt():
    print(f'Ошибка печати информации о ККТ: {kkt.error}')

# Перезагрузка кассы
if args.reboot and driver.reboot_device() != IFptr.LIBFPTR_OK:
    print(f'Перезагрузка ККТ: {kkt.error}')

# Технологическое обнуление кассы
if args.technical and driver.technological_reset() != IFptr.LIBFPTR_OK:
    print(f'Ошибка технологического обнуления: {kkt.error}')


if args.initialization:
    pass

if args.fiscal:
    kkt.process_fiscalisation()



