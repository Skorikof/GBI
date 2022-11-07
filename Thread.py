import time
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class ReadSignals(QObject):
    result = pyqtSignal(object)
    error_read = pyqtSignal(object)
    result_log = pyqtSignal(object)


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
    def run(self):
        while self.cycle:
            try:
                if not self.is_run:
                    time.sleep(1)
                else:
                    temp_arr = []
                    for i in range(240, 248):
                        temp_list = []
                        for j in range(4098, 4109, 5):
                            rr = self.client.read_holding_registers(j, 1, unit=i)
                            if not rr.isError():
                                temp_val = ''.join(bin(rr.registers[0])[2:].zfill(16))
                                temp_list.append(temp_val)

                            else:
                                temp_list.append('1111111100111000')

                        temp_arr.append(temp_list)

                    self.signals.result.emit(temp_arr)
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
