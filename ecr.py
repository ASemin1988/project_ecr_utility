import constants
#import ecr_utility
import time
import json



class ECR:

    def __init__(self, driver):
        self.dto10 = driver
        self.check_configuration_version = self.dto10.get_configuration()
        self.connect_kkt = self.dto10.connect_to_kkt_by_usb()
        self.serial_number = self.dto10.get_serial_number()
        self.check_fn_information = self.dto10.fn_information()
        self.check_read_licenses = self.dto10.read_licenses()
        self.error = self.dto10.error_description()
        self.status_fn = self.dto10.fn_fiscal_state()
        self.check_model_name_information = self.dto10.check_model_kkt()


    def check_information_kkt(self):

        print(f'\n{constants.line_kkt_inform} {" Информация о ККТ "} {constants.line_kkt_inform}')

        if self.connect_kkt != self.dto10.fptr.LIBFPTR_OK:
            exit("Не удалось установить связь с ККТ!")

        print(f'Наименование ККТ: {self.check_model_name_information}')

        print(f"Заводской номер ККТ: {self.serial_number}")

        print(f"Прошивка : {self.dto10.get_configuration()}")

        if self.check_fn_information:
            print(f"Серийный номер ФН : {self.check_fn_information}")
        else:
            print(f"Серийный номер ФН: {self.error}")

        print(f'{constants.line_kkt_license} {" Лицензии "} {constants.line_kkt_license}')

        if self.check_read_licenses is not None:
            print(*self.check_read_licenses, sep='\n')
        else:
            print(f"Нет введённых лицензий")

        print(constants.lines)


    def process_fiscalisation(self):
        # Получаем состояние ФН
        state_fn = self.dto10.fn_fiscal_state()

        # Получаем статус ФН готов к активации
        configured_fn = self.dto10.fptr.LIBFPTR_UT_CONFIGURATION

        if state_fn != configured_fn:
            print("ФН фискализирован")
            # Очистка ФН
            print(f'Производим очистку ФН, подождите...')
            self.dto10.fn_clear()
            while self.connect_kkt != self.dto10.fptr.LIBFPTR_OK and constants.connect_tries < 0:
                time.sleep(constants.connect_wait)
                constants.connect_tries += 1
                print(f'Подклчюение к ККТ(попытка {constants.connect_tries})')
            if constants.connect_tries == constants.max_connect_tries:
                print(f'Ошибка очистки')
            print(f'Завершение очистики ФН: {self.error}')

            # Если на ККТ платформа 2.5, то выполняется код ниже
            if self.dto10.check_platform_version == self.dto10.check_platform_version:
                input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
                if self.dto10.technological_reset():
                    print(f'Технологическое обнуление: {self.error}')
                    raise Exception
                elif self.connect_kkt != self.dto10.fptr.LIBFPTR_OK:
                    exit(f'{self.error}')
                input('Переставьте джампер или переключатель boot в ON и нажмите ENTER для продолжения: ')
                if self.dto10.reboot_device():
                    print(f'Перезагрузка ККТ: {self.error}')
                    raise Exception
            # Если на ККТ платформа 5, то выполянется код ниже
            elif self.dto10.check_platform_version == self.dto10.check_platform_version:
                self.dto10.technological_reset()
                print(f'Технологическое обнуление: {self.error}')
            else:
                exit(f"Ошибка выполнения: {self.error}")
            self.dto10.reboot_device
            print(f'Перезагрузка ККТ: {self.error}')
        print('ФН готов к аткивации')

        # Проверяем записанные в ККТ лицензии, если лицензий нет выводим уведомление и заверашем работу
        if self.check_read_licenses is not None:
            print(f"Лицензии введены", end='\n')
        else:
            exit(f"Нет введённых лицензий")

        # Процесс фискализации ФН
        inn = input(f"Введите ИНН клиента : ")
        rnm = ""
        try:
            rnm = self.dto10.calc_rnm(full_serial_number=self.serial_number, inn_12=inn, rnm_number="1").ljust(20)
        except:
            exit(f"Ошибка при вычислении РНМ!")
        print(f"Регистрационный номер : {rnm}")

        constants.file_json["organization"]["vatin"] = inn
        constants.file_json["device"]["registrationNumber"] = rnm

        print("Производим фискализацию")
        if self.dto10.process_json(
                json.dumps(constants.file_json)) != self.dto10.fptr.LIBFPTR_OK:
            print(f"Ошибка : {self.error}")
            exit("Не удалось фискализировать ККТ!")
        print("ККТ успешно фискализирована")