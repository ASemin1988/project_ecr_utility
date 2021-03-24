# python 3.9
import json
import dto_helper
import time
import argparse


connect_wait = 2
max_connect_tries = 120


print("-" * 30 + " Информация о ККТ " + "-" * 32)

driver = dto_helper.create_driver()

if dto_helper.connect_to_kkt_by_usb(driver) != driver.LIBFPTR_OK:
    exit("Не удалось установить связь с ККТ!")

serial_number = dto_helper.get_serial_number(driver)
print(f"Заводской номер ККТ : {serial_number}".format(serial_number=serial_number))

configuration_version = dto_helper.get_configuration(driver)
print(f"Прошивка : {configuration_version}".format(configuration_version=configuration_version))

serial_fn = dto_helper.fn_information(driver)
print(f"Серийный номер ФН : {serial_fn}".format(serial_fn=serial_fn))

print("-" * 35 + " Лицензии " + "-" * 35)

if dto_helper.read_licenses(driver) is not None:
    print(*dto_helper.read_licenses(driver), sep='\n')
else:
    print(f"Нет введённых лицензий")

print("-" * 80)


# Добавил аргументы для запуска
parser = argparse.ArgumentParser()
parser.add_argument("--fiscal", "-f", help="- Фискализация кассы", action="store_true")
parser.add_argument("--info", "-i", help="- Печать информации о ККТ", action="store_true")
parser.add_argument("--technical", "-t", help="- Технологическое обнуление", action="store_true")
parser.add_argument("--reboot", "-r", help="- Перезагрузка кассы", action="store_true")
args = parser.parse_args()



if args.info:
    dto_helper.print_information_kkt(driver)
    if dto_helper.connect_to_kkt_by_usb(driver) != driver.LIBFPTR_OK:
        print(f'Ошибка связи с ККТ: {dto_helper.error_description(driver)}')


if args.reboot:
    if dto_helper.reboot_device(driver) != driver.LIBFPTR_OK:
        print(dto_helper.error_description(driver))

if args.technical:
    if dto_helper.technological_reset(driver) != driver.LIBFPTR_OK:
        print(dto_helper.error_description(driver))


if args.fiscal:
    # Получаем состояние ФН
    state_fn = dto_helper.fn_fiscal_state(driver)

    # Получаем статус ФН готов к активации
    configured_fn = dto_helper.IFptr.LIBFPTR_UT_CONFIGURATION

    platform_v5 = '5.7'
    platform_v2_5 = len(dto_helper.configuration_version_v2_5(driver))
    connect_wait = 5
    max_connect_tries = 120

    if state_fn != configured_fn:
        print("ФН фискализирован")
        # Очистка ФН
        print(f'Производим очистку ФН, подождите...')
        dto_helper.fn_clear(driver)
        connect_tries = 0
        while dto_helper.connect_to_kkt_by_usb(driver) != driver.LIBFPTR_OK:
            time.sleep(connect_wait)
            connect_tries += 1
            print(f'Подклчюение к ККТ(попытка {connect_tries})')
        if connect_tries == max_connect_tries:
            print(f'Ошибка очистки')
        print(f'Завершение очистики ФН: {dto_helper.error_description(driver)}')


        # Если на ККТ платформа 2.5, то выполняется кож ниже
        #if re.findall(r'3', configuration_version):
        if len(dto_helper.configuration_version_v2_5(driver)) == platform_v5:
            input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
            if dto_helper.technological_reset(driver):
                print(f'Технологическое обнуление: {dto_helper.error_description(driver)}')
                raise Exception
            input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
            if dto_helper.reboot_device(driver):
                print(f'Перезагрузка ККТ: {dto_helper.error_description(driver)}')
                raise Exception
        # Если на ККТ платформа 5, то выполянется код ниже
        elif dto_helper.configuration_version_v5(driver) >= platform_v5:
            dto_helper.technological_reset(driver)
            print(f'Технологическое обнуление: {dto_helper.error_description(driver)}')
        else:
            exit(f"Ошибка выполнения: {dto_helper.error_description(driver)}")
        dto_helper.reboot_device(driver)
        print(f'Перезагрузка ККТ: {dto_helper.error_description(driver)}')
    print('ФН готов к аткивации')

    # Проверяем записанные в ККТ лицензии, если лицензий нет выводим уведомление и заверашем работу
    if dto_helper.read_licenses(driver) is not None:
        print(f"Лицензии введены", end='\n')
    else:
        exit(f"Нет введённых лицензий")

    # Процесс фискализации ФН
    inn = input(f"Введите ИНН клиента : ")
    rnm = ""
    try:
        rnm = dto_helper.calc_rnm(full_serial_number=serial_number, inn_12=inn, rnm_number="1").ljust(20)
    except:
        exit(f"Ошибка при вычислении РНМ!")
    print(f"Регистрационный номер : {rnm}".format(rnm=rnm))

    dto_helper.JSON_FISCALISATION_DICT["organization"]["vatin"] = inn
    dto_helper.JSON_FISCALISATION_DICT["device"]["registrationNumber"] = rnm

    print("Производим фискализацию")
    if dto_helper.process_json(driver,
                            json.dumps(dto_helper.JSON_FISCALISATION_DICT)) != driver.LIBFPTR_OK:
        print(f"Ошибка : [{error}]".format(error=driver.errorDescription()))
        exit("Не удалось фискализировать ККТ!")
    print("ККТ успешно фискализирована")


