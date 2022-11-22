import time
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class ReadSignals(QObject):
    result_temp = pyqtSignal(object)
    result_log = pyqtSignal(object)
    check_cam = pyqtSignal(int, bool)
    error_read = pyqtSignal(object)


class Writer(QRunnable):
    signals = ReadSignals()

    def __init__(self, client, adr_dev, command):
        super(Writer, self).__init__()
        self.client = client
        self.adr_dev = adr_dev
        self.command = command

    @pyqtSlot()
    def run(self):
        try:
            if self.command:
                rq = self.client.write_registers(8192, [1], init=self.adr_dev)
                if not rq.isError():
                    txt_log = 'Cam ' + str(self.adr_dev) + ' is enabled!'
                else:
                    txt_log = 'Cam ' + str(self.adr_dev) + ' is unsuccessful attempt'
            else:
                rq = self.client.write_registers(8192, [0], init=self.adr_dev)
                if not rq.isError():
                    txt_log = 'Cam ' + str(self.adr_dev) + ' is disabled!'
                else:
                    txt_log = 'Cam ' + str(self.adr_dev) + ' is unsuccessful attempt'
            self.signals.result_log.emit(txt_log)

        except Exception as e:
            self.signals.error_read.emit(e)


class Reader(QRunnable):
    signals = ReadSignals()

    def __init__(self, client):
        super(Reader, self).__init__()
        self.cycle = True
        self.is_run = False
        self.client = client
        self.is_paused = False
        self.is_killed = False
        self.sens_regs = [4098, 4103, 4108]

    @pyqtSlot()
    def run(self):
        while self.cycle:
            try:
                if not self.is_run:
                    time.sleep(1)
                else:
                    result_list = []
                    for i in range(1, 9):
                        temp_arr = []
                        rr = self.client.read_holding_registers(8192, 1, unit=i)
                        if not rr.isError():

                            if rr.registers[0] == 1:
                                self.signals.check_cam.emit(i, True)
                                for j in range(3):
                                    temp_list = []
                                    rr = self.client.read_holding_registers(self.sens_regs[j], 3, unit=i)
                                    temp_list.append(bin(rr.registers[0])[2:].zfill(16))
                                    temp_list.append(bin(rr.registers[1])[2:].zfill(8))
                                    temp_list.append(bin(rr.registers[2])[2:].zfill(8))

                                    temp_arr.append(temp_list)

                            else:
                                self.signals.check_cam.emit(i, False)
                                txt_log = 'Base Station ' + str(i) + ' is disabled'
                                self.signals.result_log.emit(txt_log)
                                temp_arr.append([['1111111111101100', '11101100', '11101100'],
                                                 ['1111111111101100', '11101100', '11101100'],
                                                 ['1111111111101100', '11101100', '11101100']])  # -20

                        else:
                            txt_log = 'Base Station ' + str(i) + ' does not answer'
                            self.signals.result_log.emit(txt_log)
                            temp_arr.append([['1111111111110110', '11110110', '11110110'],
                                             ['1111111111110110', '11110110', '11110110'],
                                             ['1111111111110110', '11110110', '11110110']]) # -10

                        result_list.append(temp_arr)

                    self.signals.result_temp.emit(result_list)
                    time.sleep(2)

            except Exception as e:
                self.signals.error_read.emit(e)

    def startProcess(self):
        self.cycle = True
        self.is_run = True
        txt_log = 'Start process'
        self.signals.result_log.emit(txt_log)

    def pauseProcess(self):
        self.is_run = False
        txt_log = 'Pause process'
        self.signals.result_log.emit(txt_log)

    def exitProcess(self):
        self.cycle = False
        txt_log = 'Exit process'
        self.signals.result_log.emit(txt_log)
