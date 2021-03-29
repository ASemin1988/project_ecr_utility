# python 3.9
import json
import time
import argparse
from dto10 import DTO10
from libfptr10 import IFptr
from constants import Constants


driver = DTO10()
connect_wait = 2
max_connect_tries = 120


print("-" * 30 + " Информация о ККТ " + "-" * 32)


if driver.connect_to_kkt_by_usb() != IFptr.LIBFPTR_OK:
    exit("Не удалось установить связь с ККТ!")

serial_number = driver.get_serial_number()
print(f"Заводской номер ККТ : {serial_number}")

configuration_version = driver.get_configuration()
print(f"Прошивка : {configuration_version}")

serial_fn = driver.fn_information()
print(f"Серийный номер ФН : {serial_fn}")

print("-" * 35 + " Лицензии " + "-" * 35)

if driver.read_licenses() is not None:
    print(*driver.read_licenses(), sep='\n')
else:
    print(f"Нет введённых лицензий")

print("-" * 80)


# Добавил аргументы для запуска
parser = argparse.ArgumentParser()
parser.add_argument("--fiscal", "-f", help="- Фискализация кассы", action="store_true")
parser.add_argument("--info", "-i", help="- Печать информации о ККТ", action="store_true")
parser.add_argument("--technical", "-t", help="- Технологическое обнуление", action="store_true")
parser.add_argument("--reboot", "-r", help="- Перезагрузка кассы", action="store_true")
parser.add_argument("--initialization", "-in", help="- Инициализация ККТ", action="store_true")
args = parser.parse_args()



if args.info:
    driver.print_information_kkt()
    if driver.connect_to_kkt_by_usb() != IFptr.LIBFPTR_OK:
        print(f'Ошибка связи с ККТ: {driver.error_description()}')


if args.reboot:
    if driver.reboot_device() != IFptr.LIBFPTR_OK:
        print(driver.error_description())

if args.technical:
    if driver.technological_reset() != IFptr.LIBFPTR_OK:
        print(driver.error_description())


if args.initialization:
    pass

if args.fiscal:
    # Получаем состояние ФН
    state_fn = driver.fn_fiscal_state()

    # Получаем статус ФН готов к активации
    configured_fn = IFptr.LIBFPTR_UT_CONFIGURATION

    platform_v5 = '5.7'
    platform_v2_5 = len(driver.check_platform_version_v2_5())
    connect_wait = 5
    max_connect_tries = 120

    if state_fn != configured_fn:
        print("ФН фискализирован")
        # Очистка ФН
        print(f'Производим очистку ФН, подождите...')
        driver.fn_clear()
        connect_tries = 0
        while driver.connect_to_kkt_by_usb() != IFptr.LIBFPTR_OK:
            time.sleep(connect_wait)
            connect_tries += 1
            print(f'Подклчюение к ККТ(попытка {connect_tries})')
        if connect_tries == max_connect_tries:
            print(f'Ошибка очистки')
        print(f'Завершение очистики ФН: {driver.error_description()}')


        # Если на ККТ платформа 2.5, то выполняется код ниже
        if driver.check_platform_version_v2_5() == platform_v2_5:
            input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
            if driver.technological_reset():
                print(f'Технологическое обнуление: {driver.error_description()}')
                raise Exception
            input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
            if driver.reboot_device():
                print(f'Перезагрузка ККТ: {driver.error_description()}')
                raise Exception
        # Если на ККТ платформа 5, то выполянется код ниже
        elif driver.check_platform_version_v5() >= platform_v5:
            driver.technological_reset()
            print(f'Технологическое обнуление: {driver.error_description()}')
        else:
            exit(f"Ошибка выполнения: {driver.error_description()}")
        driver.reboot_device()
        print(f'Перезагрузка ККТ: {driver.error_description()}')
    print('ФН готов к аткивации')

    # Проверяем записанные в ККТ лицензии, если лицензий нет выводим уведомление и заверашем работу
    if driver.read_licenses(driver) is not None:
        print(f"Лицензии введены", end='\n')
    else:
        exit(f"Нет введённых лицензий")

    # Процесс фискализации ФН
    inn = input(f"Введите ИНН клиента : ")
    rnm = ""
    try:
        rnm = driver.calc_rnm(full_serial_number=serial_number, inn_12=inn, rnm_number="1").ljust(20)
    except:
        exit(f"Ошибка при вычислении РНМ!")
    print(f"Регистрационный номер : {rnm}")

    driver.JSON_FISCAL_INFORMATION["organization"]["vatin"] = inn
    driver.JSON_FISCAL_INFORMATION["device"]["registrationNumber"] = rnm

    print("Производим фискализацию")
    if driver.process_json(
            json.dumps(driver.JSON_FISCAL_INFORMATION)) != IFptr.LIBFPTR_OK:
        print(f"Ошибка : {driver.error_description()}")
        exit("Не удалось фискализировать ККТ!")
    print("ККТ успешно фискализирована")


