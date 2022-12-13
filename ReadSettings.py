import configparser
from pymodbus.client.sync import ModbusSerialClient as ModbusClient


class COMSettings(object):
    """Чтение настроек СОМ порта из файла ini"""

    def __init__(self):
        try:
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

            self.IP_adr = config["Local"]["IP_Address"]
            self.local_port = int(config["Local"]["Port"])

            self.active_log = config["PrgSet"]["Log"]

            a = self.initPort()


        except Exception as e:
            print(str(e))

    def initPort(self):
        try:
            self.client = ModbusClient(method='ascii', port=str(self.portNumber),
                                       timeout=1, baudrate=int(self.portSpeed),
                                       stopbits=int(self.portStopBits),
                                       parity=str(self.portParity), strict=False)

            self.port_connect = self.client.connect()

            if self.port_connect:
                return True
            else:
                return False

        except Exception as e:
            print(str(e))


class Registers(object):
    def __init__(self):
        self.temp = '-10'
        self.serial = '-10'
        self.bat = '-10'


class DataSens(object):
    def __init__(self):
        self.sens = []


class DataCam(object):
    def __init__(self):
        self.cam = []
