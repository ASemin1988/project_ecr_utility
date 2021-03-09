# python 3.9
import json
import argparse
import dto_helper
import time



print("-" * 75)

driver = dto_helper.create_driver()


if dto_helper.connect_to_kkt_by_usb(driver) != driver.LIBFPTR_OK:
    exit("Не удалось установить связь с ККТ!")

serial_number = dto_helper.get_serial_number(driver)
print("Заводской номер ККТ : {serial_number}".format(serial_number=serial_number))

configurationVersion = dto_helper.get_configuration(driver)
print("Прошивка : {configurationVersion}".format(configurationVersion=configurationVersion))

serial_fn = dto_helper.fn_information(driver)
print("Серийный номер ФН: {serial_fn}".format(serial_fn=serial_fn))

print("-" * 75)

# Добавил аргументы для запуска
parser = argparse.ArgumentParser ()
parser.add_argument("--fiscal", "-f", help="- Фискализация кассы", action="store_true")
parser.add_argument("--info", "-i", help="- Печать информации о ККТ", action="store_true")
parser.add_argument("--reset", "-r", help="- Технологическое обнуление", action="store_true")
args = parser.parse_args()

if args.info:
    printInformation = dto_helper.print_information_kkt(driver)

if args.reset:
    if dto_helper.technoligical_reset(driver) != driver.LIBFPTR_OK:
        print(dto_helper.error_description(driver))


if args.fiscal:
    # Получаем состояние ФН
    state_fn = dto_helper.fn_fiscal_state(driver)

    # Получаем статус ФН готов к активации
    configured_fn = dto_helper.IFptr.LIBFPTR_UT_CONFIGURATION

    # Получаем статус ФН фискализирован
    # mode_fn = dto_helper.IFptr.LIBFPTR_FNS_FISCAL_MODE
    # Процесс проверки ФН, очистка и дальнейшая фискализация

    if state_fn != configured_fn:
        print("ФН фискализирован")
        # Очистка ФН
        dto_helper.fn_clear(driver)
        print(f'Завершена очистка ФН: {dto_helper.error_description(driver)}')
        time.sleep(10)
        # Технологиечское обнуление ККТ
        if configurationVersion == '3':
            permission_reset = input('Переставьте джампер и нажмите enter: ')
            dto_helper.technoligical_reset(driver)
            print(f'Технологическое обнуление: {dto_helper.error_description(driver)}')
            dto_helper.reboot_device(driver)
            print(f'Перезагрузка ККТ: {dto_helper.error_description(driver)}')
        elif configurationVersion == '5':
            dto_helper.technoligical_reset(driver)
            print(f'Технологическое обнуление: {dto_helper.error_description(driver)}')
            dto_helper.reboot_device(driver)
            print(f'Перезагрузка ККТ: {dto_helper.error_description(driver)}')
        else:
            exit(f'{dto_helper.error_description(driver)}')

    else:
        print('ФН готов к аткивации')
        inn = input("Введите ИНН клиента\t: ")
        rnm = ""
    try:
        rnm = dto_helper.calc_rnm(full_serial_number=serial_number, inn_12=inn, rnm_number="1").ljust(20)
    except:
        exit("\tОшибка при вычислении РНМ!")
    print("Регистрационный номер\t: {rnm}".format(rnm=rnm))

    dto_helper.JSON_FISCALISATION_DICT["organization"]["vatin"] = inn
    dto_helper.JSON_FISCALISATION_DICT["device"]["registrationNumber"] = rnm

    print("Производим фискализацию")
    if dto_helper.process_json(driver,
                            json.dumps(dto_helper.JSON_FISCALISATION_DICT)) != driver.LIBFPTR_OK:
        print("\tОшибка: [{error}]".format(error=driver.errorDescription()))
        exit("Не удалось фискализировать ККТ!")
    print("ККТ успешно фискализирована")
