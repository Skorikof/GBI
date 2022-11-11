import configparser
from pymodbus.client.sync import ModbusSerialClient as ModbusClient


class COMSettings(object):
    """Чтение настроек СОМ порта из файла ini"""

    def __init__(self, logger):
        try:
            self.logger = logger
            config = configparser.ConfigParser()
            config.read("Settings.ini")
            self.portNumber = 'COM' + config["ComPort"]["NumberPort"]
            temp_val = config["ComPort"]["PortSettings"]
            temp_com = str.split(temp_val, ",")
            self.portSpeed = int(temp_com[0])
            self.portParity = temp_com[1]
            self.portDataBits = temp_com[2]
            self.portStopBits = temp_com[3]
            self.client = ModbusClient()

        except Exception as e:
            self.logger.error(e)

    def initPort(self):
        try:
            self.client = ModbusClient(method='ascii', port=self.portNumber,
                                       timeout=1, baudrate=self.portSpeed,
                                       stopbits=int(self.portStopBits),
                                       parity=self.portParity, strict=False)

            self.port_connect = self.client.connect()

            if self.port_connect:
                return True
            else:
                return False

        except Exception as e:
            self.logger.error(e)


class Registers(object):
    def __init__(self):
        self.temp = 0
        self.serial = 0
        self.bat = 0


class DataSens(object):
    def __init__(self):
        self.sens = []


class DataCam(object):
    def __init__(self):
        self.cam = []
