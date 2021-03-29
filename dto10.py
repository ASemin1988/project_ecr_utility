from libfptr10 import IFptr

class DTO10:

    JSON_FISCAL_INFORMATION = {
        "type": "registration",
        "operator": {
            "name": "Кассир",
            "vatin": "123654789507"
        },
        "organization": {
            "name": "ПАО \"Test AAS\"",
            "vatin": "",
            "email": "test@atol.ru",
            "taxationTypes": [
                "osn"
            ],
            "address": "г. Москва ул. Бронницкая 112"
        },
        "reason": "fnChange",
        "changeInfoReasons": [],
        "device": {
            "paymentsAddress": "Торговый зал",
            "ffdVersion": "1.05",
            "fnsUrl": "www.fns.ru",
            "registrationNumber": "",
            "internet": False,
            "offlineMode": False,
            "machineInstallation": False,
            "bso": False,
            "encryption": False,
            "autoMode": False,
            "machineNumber": "",
            "service": False,
            "gambling": False,
            "lottery": False,
            "excise": False,
            "defaultTaxationType": "osn",
            "ofdChannel": "proto"
        },
        "ofd": {
            "name": "ООО Такском",
            "vatin": "7704211201",
            "host": "178.57.71.71",
            "port": 7777
        }
    }

    def __init__(self):
        self.fptr = None
        self.create_driver()


    def create_driver(self):
        self.fptr = IFptr('./fptr10.dll')



    def check_platform_version_v2_5(self):
        platform_v2_5 = self.get_configuration()
        return platform_v2_5


    def check_platform_version_v5(self):
        platform_v5 = self.fptr.get_configuration()
        return platform_v5


    def error_description(self):
        return self.fptr.errorDescription()


    def error_code(self):
        return self.fptr.errorCode()


    # Функция проверки лицензии в ККТ
    def read_licenses(self):
        # Вспомогательная функция чтения следующей записи
        def readNextRecord(recordsID):
            self.fptr.setParam(IFptr.LIBFPTR_PARAM_RECORDS_ID, recordsID)
            return self.fptr.readNextRecord()

        self.fptr.setParam(IFptr.LIBFPTR_PARAM_RECORDS_TYPE, IFptr.LIBFPTR_RT_LICENSES)
        self.fptr.beginReadRecords()
        recordsID = self.fptr.getParamString(IFptr.LIBFPTR_PARAM_RECORDS_ID)
        id_licenses = []
        while readNextRecord(recordsID) == IFptr.LIBFPTR_OK:
            id = self.fptr.getParamInt(IFptr.LIBFPTR_PARAM_LICENSE_NUMBER)
            name = self.fptr.getParamString(IFptr.LIBFPTR_PARAM_LICENSE_NAME)
            dateFrom = self.fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_LICENSE_VALID_FROM)
            dateUntil = self.fptr.getParamDateTime(IFptr.LIBFPTR_PARAM_LICENSE_VALID_UNTIL)
            id_licenses.append(name)
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_RECORDS_ID, recordsID)
        self.fptr.endReadRecords()
        return id_licenses


    def connect_to_kkt_by_usb(self):
        self.fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_MODEL, str(IFptr.LIBFPTR_MODEL_ATOL_AUTO))
        self.fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_USB))
        self.fptr.applySingleSettings()
        self.fptr.open()
        return self.fptr.errorCode()


    def get_serial_number(self):
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_STATUS)
        self.fptr.setParam(IFptr.LIBFPTR_DT_STATUS, IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)
        self.fptr.queryData()
        return self.fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)


    def get_configuration(self):
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_UNIT_VERSION)
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_UNIT_TYPE, IFptr.LIBFPTR_UT_CONFIGURATION)
        self.fptr.queryData()
        return self.fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)


    def process_json(self, json_job):
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_JSON_DATA, json_job)
        self.fptr.processJson()
        return self.fptr.errorCode()


    def print_information_kkt(self):
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_KKT_INFO)
        self.fptr.report()


    def fn_fiscal_state(self):
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_FN_INFO)
        self.fptr.fnQueryData()
        return self.fptr.getParamInt(IFptr.LIBFPTR_PARAM_FN_STATE)


    def fn_clear(self):
        self.fptr.initMgm()


    def fn_information(self):
        self.fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_FN_INFO)
        self.fptr.setParam(IFptr.LIBFPTR_FNDT_FN_INFO, IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)
        self.fptr.fnQueryData()
        return self.fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)


    def technological_reset(self):
        self.fptr.resetSettings()


    def reboot_device(self):
        self.fptr.deviceReboot()

    def calc_rnm(self, full_serial_number, inn_12, rnm_number):
        def crc16_ccitt(buf):
            result = 0xFFFF
            table = []
            for i in range(0x100):
                r = ((i & 0xFF) << 8)
                for j in range(8):
                    if r & (1 << 15):
                        r = ((r << 1) ^ 0x1021)
                    else:
                        r = (r << 1)
                table.append(r & 0xFFFF)
            for BYTE in buf:
                result = ((result << 8) & 0xFFFF) ^ table[((result >> 8) & 0xFFFF) ^ BYTE]
            return result

        full_serial_number = full_serial_number[:20]
        if len(full_serial_number) < 20:
            full_serial_number = full_serial_number.zfill(20)
        inn_12 = inn_12[:12].strip()
        if len(inn_12) < 12:
            inn_12 = inn_12.zfill(12)
        rnm_number = rnm_number[:10]
        if len(rnm_number) < 10:
            rnm_number = rnm_number.zfill(10)

        p_buf = []
        for CHAR in bytearray(rnm_number + inn_12 + full_serial_number, encoding='utf-8'):
            p_buf.append(CHAR)
        return rnm_number + str(crc16_ccitt(p_buf)).zfill(6)


