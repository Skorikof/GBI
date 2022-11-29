import time
import socket
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot


class ReadSignals(QObject):
    result_temp = pyqtSignal(object)
    result_log = pyqtSignal(object)
    connect_check = pyqtSignal(int, bool)
    connect_data = pyqtSignal(int)
    check_cam = pyqtSignal(int, bool)
    error_read = pyqtSignal(object)


class Connection(QRunnable):
    signals = ReadSignals()
    def __init__(self, ip, port):
        super(Connection, self).__init__()
        self.ip = ip
        self.port = port

    @pyqtSlot()
    def run(self):
        try:
            while self.cycle:
                while not self.flag_connect:
                    time.sleep(1)
                    self.startConnect()

                while self.flag_connect:
                    try:
                        msg = self.sock.recv(1024)
                        print(msg)
                        if msg == b'':
                            time.sleep(1)
                            self.flag_connect = False
                            self.sock.close()
                            self.startConnect()

                        elif msg == b'Hello! ASU server welcomes you!':
                            txt_log = 'Connection complite'
                            self.signals.result_log.emit(txt_log)

                        elif msg[:3] == b'KAM':
                            temp_list = msg.decode(encoding='utf-8').split(',')
                            camera = temp_list[1]
                            command = temp_list[2]
                            if command == 'ON':
                                self.signals.connect_check.emit(camera, True)
                            if command == 'OFF':
                                self.signals.connect_check.emit(camera, False)
                            if command == 'DATA':
                                self.signals.connect_data.emit(camera)

                    except Exception as e:
                        self.signals.result_log.emit(e)
                        self.flag_connect = False
                        self.sock.close()

        except Exception as e:
            self.signals.error_read.emit(e)

    def startConnect(self):
        try:
            self.cycle = True
            self.flag_connect = False
            self.sock = socket.socket()
            self.sock.connect((self.ip, self.port))
            txt_log = 'Connecting..'
            self.signals.result_log.emit(txt_log)
            self.flag_connect = True

        except Exception as e:
            self.flag_connect = False
            txt_log = 'Connection is lose..'
            self.sock.close()
            self.signals.result_log.emit(txt_log)
            self.signals.error_read.emit(e)

    def sendData(self, sens_list):
        self.sock.send(sens_list)
        print('msg send')

    def closeConnect(self):
        self.cycle = False
        self.sock.close()
        txt_log = 'Exit connect'
        self.signals.result_log.emit(txt_log)


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
                rq = self.client.write_registers(8192, [1], unit=self.adr_dev)
                if not rq.isError():
                    txt_log = 'Cam ' + str(self.adr_dev) + ' is enabled!'
                    self.signals.check_cam.emit(self.adr_dev, True)
                else:
                    txt_log = 'Cam ' + str(self.adr_dev) + ' is unsuccessful attempt'
                    self.signals.check_cam.emit(self.adr_dev, False)
            else:
                rq = self.client.write_registers(8192, [0], unit=self.adr_dev)
                if not rq.isError():
                    txt_log = 'Cam ' + str(self.adr_dev) + ' is disabled!'
                    self.signals.check_cam.emit(self.adr_dev, False)
                else:
                    txt_log = 'Cam ' + str(self.adr_dev) + ' is unsuccessful attempt'
                    self.signals.check_cam.emit(self.adr_dev, True)
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
        self.flag_write = False

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
                                    temp_list.append(str(rr.registers[1]))
                                    temp_list.append(bin(rr.registers[2])[2:].zfill(8))

                                    temp_arr.append(temp_list)

                            else:
                                self.signals.check_cam.emit(i, False)
                                txt_log = 'Base Station ' + str(i) + ' is disabled'
                                self.signals.result_log.emit(txt_log)
                                for j in range(3):
                                    temp_arr.append(['off', 'off', 'off'])

                        else:
                            txt_log = 'Base Station ' + str(i) + ' does not answer'
                            self.signals.result_log.emit(txt_log)
                            for j in range(3):
                                temp_arr.append(['err', 'err', 'err'])

                        result_list.append(temp_arr)
                        time.sleep(0.1)

                    self.signals.result_temp.emit(result_list)
                    time.sleep(1)

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
