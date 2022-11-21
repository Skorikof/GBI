import time
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class ReadSignals(QObject):
    result_temp = pyqtSignal(object)
    result_log = pyqtSignal(object)
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
                rq = self.client.write_register(8192, 1, init=self.adr_dev)
                txt_log = 'Cam ' + str(self.adr_dev) + ' is enabled!'
            else:
                rq = self.client.write_register(8192, 0, init=self.adr_dev)
                txt_log = 'Cam ' + str(self.adr_dev) + ' is disabled!'
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
                    for i in range(8):
                        temp_arr = []
                        rr = self.client.read_holding_registers(8192, 1, unit=i+1)
                        msg = str(self.client.framer._buffer)
                        #print(msg)
                        if msg == "b''":
                            txt_log = 'Base Station ' + str(i) + ' does not answer'
                            self.signals.result_log.emit(txt_log)
                            temp_arr.append([['1111111111110110', '11110110', '11110110'],
                                             ['1111111111110110', '11110110', '11110110'],
                                             ['1111111111110110', '11110110', '11110110']]) # -10
                        else:
                            msg = msg[9:-7:]
                            if msg == '0000':
                                txt_log = 'Base Station ' + str(i + 1) + ' is disabled'
                                self.signals.result_log.emit(txt_log)
                                temp_arr.append([['1111111111101100', '11101100', '11101100'],
                                                 ['1111111111101100', '11101100', '11101100'],
                                                 ['1111111111101100', '11101100', '11101100']]) # -20
                            else:
                                temp_list = []
                                for j in range(3):
                                    rr = self.client.read_holding_registers(4098 + j, 1, unit=i+1)
                                    msg = str(self.client.framer._buffer)
                                    msg = msg[9:-7:]
                                    temp_list.append(msg)
                                temp_arr.append(temp_list)

                                for j in range(3):
                                    rr = self.client.read_holding_registers(4103 + j, 1, unit=i+1)
                                    msg = str(self.client.framer._buffer)
                                    msg = msg[9:-7:]
                                    temp_list.append(msg)
                                temp_arr.append(temp_list)

                                for j in range(3):
                                    rr = self.client.read_holding_registers(4108 + j, 1, unit=i+1)
                                    msg = str(self.client.framer._buffer)
                                    msg = msg[9:-7:]
                                    temp_list.append(msg)
                                temp_arr.append(temp_list)

                        result_list.append(temp_arr)

                    self.signals.result_temp.emit(result_list)
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
