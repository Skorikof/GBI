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


class DataCheck(object):
    def __init__(self):
        self.cam1 = False
        self.cam2 = False
        self.cam3 = False
        self.cam4 = False
        self.cam5 = False
        self.cam6 = False
        self.cam7 = False
        self.cav8 = False


class DataSensBin(object):
    def __init__(self):
        self.cam1 = []
        self.cam2 = []
        self.cam3 = []
        self.cam4 = []
        self.cam5 = []
        self.cam6 = []
        self.cam7 = []
        self.cam8 = []


class DataSensInt(object):
    def __init__(self):
        self.cam1 = []
        self.cam2 = []
        self.cam3 = []
        self.cam4 = []
        self.cam5 = []
        self.cam6 = []
        self.cam7 = []
        self.cam8 = []
