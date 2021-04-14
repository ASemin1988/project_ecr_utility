import constants
import time
import json
import json_work
import config
import os
import helper



class ECR:
    def __init__(self, driver):
        self.dto10 = driver
        self.connect_kkt = self.dto10.connect_to_kkt_by_usb()
        self.serial_number = self.dto10.get_serial_number()
        self.fn_information = self.dto10.get_fn_information()
        self.read_licenses = self.dto10.read_licenses()
        self.status_fn = self.dto10.get_fn_fiscal_state()
        self.model_name_information = self.dto10.get_model_kkt()
        self.configuration_version = self.dto10.get_configuration()
        self.get_firmware_version = self.configuration_version.startswith(constants.VERSION_CONFIGURATION)
        self.platform = self.get_platform()
        self.code_model_kkt = self.dto10.get_model_information_kkt()
        self.logical_number_kkt = self.dto10.get_logical_number_kkt()

    def get_platform(self):
        if self.configuration_version.startswith('5'):
            return constants.PLATFORM_V5
        if self.configuration_version.startswith('3'):
            return constants.PLATFORM_V2_5

    def get_information_kkt(self):

        print(f'\n{constants.LINE_KKT_INFORM} Информация о ККТ {constants.LINE_KKT_INFORM}')

        if self.connect_kkt != self.dto10.fptr.LIBFPTR_OK:
            exit("Не удалось установить связь с ККТ!")

        print(f'Номер ККТ: {self.logical_number_kkt}')

        print(f'Модель ККТ: {self.model_name_information}({self.code_model_kkt})')

        print(f"Заводской номер ККТ: {self.serial_number}")

        print(f"Прошивка : {self.configuration_version}")

        if self.fn_information:
            print(f"Серийный номер ФН : {self.fn_information}")
        else:
            print(f"Серийный номер ФН: {self.dto10.error_description()}")

        print(f'{constants.LINE_KKT_LICENSE} Лицензии {constants.LINE_KKT_LICENSE}')

        self.check_licenses()

        print(constants.LINES)

    def write_licenses(self):
        if self.read_licenses:
            exit(f'Лицензии введены')
        else:
            path_dict = os.path.join(config.path_data_dict,
                                     '0' + self.code_model_kkt,
                                     self.serial_number + config.path_format_json)

            data_dict = json_work.open_json_file(name=path_dict)

            success_flag = True
            if self.platform == constants.PLATFORM_V5 or self.platform == constants.PLATFORM_V2_5 and \
                    self.get_firmware_version:
                license_list = []
                if self.platform == constants.PLATFORM_V5:
                    license_list = data_dict['licensesPlatform50']

                if self.platform == constants.PLATFORM_V2_5:
                    license_list = data_dict['licensesPlatform25']

                for license in license_list:
                    error = self.dto10.write_licenses(value=license['license'])
                    if error != self.dto10.fptr.LIBFPTR_OK:
                        success_flag = False

            elif self.platform == constants.PLATFORM_V2_5:
                    codes_list = data_dict['protectionCodes']
                    for codes in codes_list:
                        error = self.dto10.write_licenses(value=codes['codeValue'], number=codes['codeNumber'])
                        if error != self.dto10.fptr.LIBFPTR_OK:
                            success_flag = False

            return success_flag

    def check_initialisation_kkt(self):
        data_dict = json_work.open_json_file(
            name=os.path.join(config.path_data_dict, '0' + self.code_model_kkt,
                              self.serial_number + config.path_format_json))

        success_tag = True
        list = data_dict
        error = self.dto10.initialization_kkt(serial_number=list['serialNumber'],
                                              mac_address=list['macAddress'])
        if error != self.dto10.fptr.LIBFPTR_OK:
            success_tag = False
        return success_tag

    def check_licenses(self):
        if self.read_licenses:
            print(*self.read_licenses, sep='\n')
        elif self.read_licenses is not None:
            print(f"Нет введённых лицензий")
        else:
            print(self.dto10.error_description())

    def checking_inn(self):
        while True:
            inn = ""
            try:
                inn = int(input(f"\nВведите ИНН клиента : "))
                if len(str(inn)) == constants.MIN_LENGTH_INN or len(str(inn)) == constants.MAX_LENGTH_INN:
                    return inn
                else:
                    print('В ИНН количество цифр должно быть 10 или 12')
                    continue
            except ValueError:
                print(f'Введите только цифры!')

    def reboot_device_kkt(self):
        if self.dto10.reboot_device() == self.dto10.fptr.LIBFPTR_OK:
            print('Перезагрузка кассы выполнена успешно')
            return True
        else:
            print(f'Ошибка во время перезагрузки кассы: {self.dto10.error_description()}')
            return False

    def technical_reset_kkt(self):
        if self.dto10.technological_reset() == self.dto10.fptr.LIBFPTR_OK:
            print('Технологическое обнуление выполнено успешно')
            return True
        else:
            exit(f"Ошибка выполнения: {self.dto10.error_description()}")
            return False

    def check_platform_v2_5(self):
        input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
        self.technical_reset_kkt()
        input('Переставьте джампер или переключатель boot в OFF и нажмите ENTER для продолжения: ')
        print(f'\nКасса перезагружается..')
        self.reboot_device_kkt()

    def check_information_connect(self):
        while self.connect_kkt != self.dto10.fptr.LIBFPTR_OK:
            time.sleep(constants.CONNECT_WAIT)
            constants.CONNECT_TRIES += 1
            print(f'Подключение к ККТ(попытка {constants.CONNECT_TRIES})')
            if constants.CONNECT_TRIES == constants.MAX_CONNECT_TRIES:
                print(f'Ошибка очистки')

    def check_platform_v5(self):
        print(f'\nПроизводим технологическое обнуление..')
        self.technical_reset_kkt()
        print(f'\nКасса перезагружается..')
        self.reboot_device_kkt()
        time.sleep(constants.CONNECT_WAIT)

    def check_platform(self):
        # Выполнение метода если платформа 2.5
        if self.platform == constants.PLATFORM_V2_5:
            self.check_platform_v2_5()
        # Выполнение метода если платформа 5.0
        if self.platform == constants.PLATFORM_V5:
            self.check_platform_v5()

    def enter_uin_and_keys(self, uin, public_key, private_key, signature, mac=""):
        byte_keys = helper.string_to_byte(public_key)
        byte_keys.extend(helper.string_to_byte(signature))
        byte_keys.extend(helper.string_to_byte(private_key))
        return self.dto10.enter_keys(byte_keys=byte_keys, uin=uin, mac=mac)

    def enter_uin_from_file(self):
        data_dict = json_work.open_json_file(
            name=os.path.join(config.path_data_dict, '0' + self.code_model_kkt,
                                self.serial_number + config.path_format_json))

        list_uin = data_dict
        list_keys = data_dict['keysPlatform50']
        error = self.enter_uin_and_keys(uin=list_uin['UIN'],
                                        public_key=list_keys['public'],
                                        private_key=list_keys['private'],
                                        signature=list_keys['signature'])
        if error == self.dto10.fptr.LIBFPTR_OK:
            print('Ключи введены успешно')
            return True
        else:
            print(f'Ошибка ввода ключей: {self.dto10.fptr.errorDescription()}')
            return False

    def clear_fn_kkt(self):
        print(f'\nПроизводим очистку ФН, подождите...')
        if self.dto10.fn_clear() == self.dto10.fptr.LIBFPTR_OK:
            print('Инициализация ФН выполнена успешно')
            return True
        else:
            print(f'Ошибка инициализации ФН: {self.dto10.fptr.errorDescription()}')
        self.check_information_connect()

    def base_config_kkt(self):

        # Получаем состояние ФН
        self.status_fn

        # Получаем статус ФН готов к активации
        configured_fn = self.dto10.fptr.LIBFPTR_UT_CONFIGURATION

        if self.status_fn != configured_fn:
            print("\nФН фискализирован")

            # Очистка ФН
            self.clear_fn_kkt()

            # В зависимости от платформы производим действия
            self.check_platform()

        print('\nФН готов к аткивации')

        # Проверяем записанные в ККТ лицензии, если лицензий нет выводим уведомление и записываем лицензии
        if self.read_licenses:
            print(f"\nЛицензии введены", end='\n')
        else:
            print("\nНет введённых лицензий")
            print("\nВыполянется процесс записи лицензии в кассу, подождите...")
            time.sleep(constants.CONNECT_WAIT)
            self.write_licenses()
            print("\nЛицензии успешно записаны")

        self.enter_uin_from_file()

        # Процесс фискализации ФН
        inn = self.checking_inn()

        rnm = ""
        try:
            rnm = self.dto10.calc_rnm(full_serial_number=self.serial_number, inn_12=str(inn),
                                      rnm_number="1").ljust(20)
        except:
            exit(f"Ошибка при вычислении РНМ!")
        print(f"Регистрационный номер : {rnm}")

        # Записываем из json файла данные в переменную
        file_json = json_work.open_json_file(name=config.path_json_file)
        # Записываем данные inn and rnm в переменную с json данными
        file_json["organization"]["vatin"] = str(inn)
        file_json["device"]["registrationNumber"] = rnm

        print("Производим фискализацию")
        if self.dto10.process_json(
                json.dumps(file_json)) != self.dto10.fptr.LIBFPTR_OK:
            print(f"Ошибка : {self.dto10.error_description()}")
            exit("Не удалось фискализировать ККТ!")
        print("!!ККТ успешно фискализирована!!")

    def process_fiscalisation(self):

        # Получаем состояние ФН
        self.status_fn

        # Получаем статус ФН готов к активации
        configured_fn = self.dto10.fptr.LIBFPTR_UT_CONFIGURATION

        if self.status_fn != configured_fn:
            exit("\nФН фискализирован")
        else:
            print('\nФН готов к аткивации')

        # Проверяем записанные в ККТ лицензии, если лицензий нет выводим уведомление и записываем лицензии
        if self.read_licenses:
            print(f"\nЛицензии введены", end='\n')
        else:
            exit("\nНет введённых лицензий")

        # Процесс фискализации ФН
        inn = self.checking_inn()

        rnm = ""
        try:
            rnm = self.dto10.calc_rnm(full_serial_number=self.serial_number, inn_12=str(inn),
                                      rnm_number="1").ljust(20)
        except:
            exit(f"Ошибка при вычислении РНМ!")
        print(f"Регистрационный номер : {rnm}")

        # Записываем из json файла данные в переменную
        file_json = json_work.open_json_file(name=config.path_json_file)
        # Записываем данные inn and rnm в переменную с json данными
        file_json["organization"]["vatin"] = str(inn)
        file_json["device"]["registrationNumber"] = rnm

        print("Производим фискализацию")
        if self.dto10.process_json(
                json.dumps(file_json)) != self.dto10.fptr.LIBFPTR_OK:
            print(f"Ошибка : {self.dto10.error_description()}")
            exit("Не удалось фискализировать ККТ!")
        print("!!ККТ успешно фискализирована!!")

