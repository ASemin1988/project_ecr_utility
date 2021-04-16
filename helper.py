import re



class Hex:
    # StrHex:           '404132'
    # StrHexSpace:      '40 41 32'
    # List:             [0x40, 0x41, 0x32]
    # Bytes (Symbols):  '@A2'
    Array = []

    def clear(self):
        self.Array = []

    def set_hex_data(self, data, bytes=None):
        self.Array = self.hex_data(data, bytes)

    def hex_data(self, data, bytes):
        Result = []
        if type(data) == list:
            Result = data
        elif type(data) == str:
            if not bytes:
                if re.match('^[A-Fa-f0-9]*$', data) is not None:
                    Index = 0
                    while Index < len(data):
                        Result.append(int(data[Index:Index + 2], 16))
                        Index += 2
                    return Result
                elif re.match('^[A-Fa-f0-9 ]*$', data) is not None:
                    for byte in data.split(' '):
                        if len(byte) > 2:
                            Result = []
                            return Result
                        Result.append(int(byte, 16))
                    return Result
            for symbol in bytearray(data, encoding='utf-8'):
                Result.append(symbol)
        return Result

    def toList(self):
        return self.Array


def string_to_byte(_string):
    buf = Hex()
    buf.clear()
    buf.set_hex_data(_string)
    byte_array = buf.toList()
    return byte_array