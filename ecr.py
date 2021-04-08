import constants
import time
import json
import json_work
import config



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
        self.get_firmware_version = self.configuration_version.startswith('8541')
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



    def check_licenses(self):
        if self.read_licenses:
            print(*self.read_licenses, sep='\n')
        elif self.read_licenses is not None:
            print(f"Нет введённых лицензий")
        else:
            print(self.dto10.error_description())



    def check_platform_v2_5(self):
        if self.platform == constants.PLATFORM_V2_5:
            input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
            if self.dto10.technological_reset():
                print(f'Технологическое обнуление: {self.dto10.error_description()}')
                raise Exception
            elif self.connect_kkt != self.dto10.fptr.LIBFPTR_OK:
                exit(f'{self.dto10.error_description()}')
            input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
            if self.dto10.reboot_device():
                print(f'Перезагрузка ККТ: {self.dto10.error_description()}')
                raise Exception
        exit(f'{self.dto10.error_description()}')


    def check_information_connect(self):
        constants.CONNECT_TRIES
        while self.connect_kkt != self.dto10.fptr.LIBFPTR_OK:
            time.sleep(constants.CONNECT_WAIT)
            constants.CONNECT_TRIES += 1
            print(f'Подключение к ККТ(попытка {constants.CONNECT_TRIES})')
            if constants.CONNECT_TRIES == constants.MAX_CONNECT_TRIES:
                print(f'Ошибка очистки')


    def check_platform_v5(self):
        if self.platform == constants.PLATFORM_V5:
            print(f'\nПроизводим технологическое обнуление..')
            self.dto10.technological_reset()
        else:
            exit(f"Ошибка выполнения: {self.dto10.error_description()}")
        print(f'\nКасса перезагружается..')
        self.dto10.reboot_device()
        time.sleep(constants.TIME_SLEEP)
        print(f'\nПерезагрузка ККТ: {self.dto10.error_description()}')


    def check_platform(self):
        # Выполнение метода если платформа 2.5
        self.check_platform_v2_5()
        # Выполнение метода если платформа 5.0
        self.check_platform_v5()


    def process_fiscalisation(self):

        # Получаем состояние ФН
        self.status_fn

        # Получаем статус ФН готов к активации
        configured_fn = self.dto10.fptr.LIBFPTR_UT_CONFIGURATION

        if self.status_fn != configured_fn:
            print("\nФН фискализирован")
            # Очистка ФН
            print(f'\nПроизводим очистку ФН, подождите...')
            self.dto10.fn_clear()
            self.check_information_connect()
            print(f'\nЗавершение очистики ФН: {self.dto10.error_description()}')

            # В зависимости от платформы производим действия
            self.check_platform()

        print('\nФН готов к аткивации')

        # Проверяем записанные в ККТ лицензии, если лицензий нет выводим уведомление и заверашем работу
        if self.read_licenses is not None:
            print(f"\nЛицензии введены", end='\n')
        else:
            exit(f"Нет введённых лицензий")

        # Процесс фискализации ФН
        inn = input(f"\nВведите ИНН клиента : ")
        rnm = ""
        try:
            rnm = self.dto10.calc_rnm(full_serial_number=self.serial_number, inn_12=inn, rnm_number="1").ljust(20)
        except:
            exit(f"Ошибка при вычислении РНМ!")
        print(f"Регистрационный номер : {rnm}")

        # Записываем из json файла данные в переменную
        file_json = json_work.open_json_file(name=config.path_json_file)
        # Записываем данные inn and rnm в переменную с json данными
        file_json["organization"]["vatin"] = inn
        file_json["device"]["registrationNumber"] = rnm

        print("Производим фискализацию")
        if self.dto10.process_json(
                json.dumps(file_json)) != self.dto10.fptr.LIBFPTR_OK:
            print(f"Ошибка : {self.dto10.error_description()}")
            exit("Не удалось фискализировать ККТ!")
        print("!!ККТ успешно фискализирована!!")