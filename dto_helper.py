from libfptr10 import IFptr



JSON_FISCALISATION_DICT = {
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


def create_driver():
    return IFptr('')


def error_description(fptr):
    return fptr.errorDescription()


def error_code(fptr):
    return fptr.errorCode()


def connect_to_kkt_by_usb(fptr):
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_MODEL, str(IFptr.LIBFPTR_MODEL_ATOL_AUTO))
    fptr.setSingleSetting(IFptr.LIBFPTR_SETTING_PORT, str(IFptr.LIBFPTR_PORT_USB))
    fptr.applySingleSettings()
    fptr.open()
    return fptr.errorCode()


def get_serial_number(fptr):
    fptr.setParam(fptr.LIBFPTR_PARAM_DATA_TYPE, fptr.LIBFPTR_DT_STATUS)
    fptr.setParam(fptr.LIBFPTR_DT_STATUS, fptr.LIBFPTR_PARAM_SERIAL_NUMBER)
    fptr.queryData()
    return fptr.getParamString(fptr.LIBFPTR_PARAM_SERIAL_NUMBER)


def get_configuration(fptr):
    fptr.setParam(IFptr.LIBFPTR_PARAM_DATA_TYPE, IFptr.LIBFPTR_DT_UNIT_VERSION)
    fptr.setParam(IFptr.LIBFPTR_PARAM_UNIT_TYPE, IFptr.LIBFPTR_UT_CONFIGURATION)
    fptr.queryData()
    return fptr.getParamString(IFptr.LIBFPTR_PARAM_UNIT_VERSION)


def process_json(fptr, json_job):
    fptr.setParam(fptr.LIBFPTR_PARAM_JSON_DATA, json_job)
    fptr.processJson()
    return fptr.errorCode()


def print_information_kkt(fptr):
    fptr.setParam(IFptr.LIBFPTR_PARAM_REPORT_TYPE, IFptr.LIBFPTR_RT_KKT_INFO)
    fptr.report()


def fn_fiscal_state(fptr):
    fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_FN_INFO)
    fptr.fnQueryData()
    return fptr.getParamInt(IFptr.LIBFPTR_PARAM_FN_STATE)


def fn_clear(fptr):
    fptr.initMgm()


def fn_information(fptr):
    fptr.setParam(IFptr.LIBFPTR_PARAM_FN_DATA_TYPE, IFptr.LIBFPTR_FNDT_FN_INFO)
    fptr.setParam(IFptr.LIBFPTR_FNDT_FN_INFO, IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)
    fptr.fnQueryData()
    return fptr.getParamString(IFptr.LIBFPTR_PARAM_SERIAL_NUMBER)


def technological_reset(fptr):
    fptr.resetSettings()


def reboot_device(fptr):
    fptr.deviceReboot()

def calc_rnm(full_serial_number, inn_12, rnm_number):
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
