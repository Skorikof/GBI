import time
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class ReadSignals(QObject):
    result_temp = pyqtSignal(object)
    result_bat = pyqtSignal(object)
    result_serial = pyqtSignal(object)
    result_log = pyqtSignal(object)
    error_read = pyqtSignal(object)


class Runner(QRunnable):
    signals = ReadSignals()

    def __init__(self, client):
        super(Runner, self).__init__()
        self.cycle = True
        self.is_run = False
        self.client = client
        self.is_paused = False
        self.is_killed = False

    @pyqtSlot()
    def write(self):
        try:
            if self.command:
                rr = self.client.write_holding_registers(2000, 1, init=self.adr_dev)
            else:
                rr = self.client.write_holding_registers(2000, 0, init=self.adr_dev)
        except Exception as e:
            self.signals.error_read.emit(e)

    def startWrite(self, command, adr_dev):
        self.command = command
        self.adr_dev = adr_dev

    @pyqtSlot()
    def run(self):
        while self.cycle:
            try:
                if not self.is_run:
                    time.sleep(1)
                else:
                    temp_arr = []
                    bat_arr = []
                    serial_arr = []
                    for i in range(1, 9):
                        temp_list = []
                        bat_list = []
                        serial_list = []
                        for j in range(4098, 4109, 5):
                            rr = self.client.read_holding_registers(j, 1, unit=i)
                            if not rr.isError():
                                temp_val = ''.join(bin(rr.registers[0])[2:].zfill(16))
                                temp_list.append(temp_val)
                            else:
                                temp_list.append('Err')
                        for j in range(4100, 4111, 5):
                            rr = self.client.read_holding_registers(j, 1, unit=i)
                            if not rr.isError():
                                bat_val = ''.join(bin(rr.registers[0])[2:].zfill(16))
                                bat_list.append(bat_val)
                            else:
                                bat_list.append('Err')
                        for j in range(4099, 4100, 5):
                            rr = self.client.read_holding_registers(j, 1, unit=i)
                            if not rr.isError():
                                serial_val = ''.join(bin(rr.registers[0])[2:].zfill(16))
                                serial_list.append(serial_val)
                            else:
                                serial_list.append('Err')

                        temp_arr.append(temp_list)
                        bat_arr.append(bat_list)
                        serial_arr.append(serial_list)

                    self.signals.result_temp.emit(temp_arr)
                    self.signals.result_bat.emit(bat_arr)
                    self.signals.result_serial.emit(serial_arr)
                    time.sleep(5)

            except Exception as e:
                self.signals.error_read.emit(e)

    def startProcess(self):
        self.cycle = True
        self.is_run = True
        txt_log = 'Start process'
        self.signals.result_log.emit(txt_log)

    def exitProcess(self):
        self.cycle = False
        txt_log = 'Exit process'
        self.signals.result_log.emit(txt_log)
