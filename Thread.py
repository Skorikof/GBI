import time
import os
import socket
from datetime import datetime
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

base_dir = os.path.dirname(__file__)

class ReadSignals(QObject):
    result_temp = pyqtSignal(object)
    result_log = pyqtSignal(object)
    connect_check = pyqtSignal(int, bool)
    connect_data = pyqtSignal(int)
    lucky_attemp = pyqtSignal(int, bool)
    check_cam = pyqtSignal(int, bool)
    error_read = pyqtSignal(object)


class LogWriter(QRunnable):
    def __init__(self, mode, obj_name, msg):
        super(LogWriter, self).__init__()
        try:
            if mode == 'info':
                _date_log = str(datetime.now().day).zfill(2) + '_' + str(datetime.now().month).zfill(2) + \
                    '_' + str(datetime.now().year)
            if mode == 'error':
                _date_log = 'errors'

            _path_logs = base_dir + '/log'
            self.filename = _path_logs + '/' + _date_log + '.log'
            self.msg = msg
            self.nam_f = obj_name[0]
            self.nam_m = obj_name[1]
            self.num_line = obj_name[2]

        except Exception as e:
            print(str(e))

    @pyqtSlot()
    def run(self):
        try:
            with open(self.filename, 'a') as file:
                temp_str = str(datetime.now())[:-3] + ' - [' + str(self.nam_f) + '].' + self.nam_m + \
                    '[' + str(self.num_line) + '] - ' + self.msg + '\n'
                file.write(temp_str)

        except Exception as err:
            print(str(err))


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
                            self.sock.send(b'Connection complite')
                            txt_log = 'Соединение с сервером установлено'
                            self.signals.result_log.emit(txt_log)

                        elif msg[:3] == b'KAM':
                            temp_list = msg.decode(encoding='utf-8').split(',')
                            camera = int(temp_list[1])
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
            txt_log = 'Соединение с сервером..'
            self.signals.result_log.emit(txt_log)
            self.flag_connect = True

        except Exception as e:
            self.flag_connect = False
            txt_log = 'Соединение потеряно'
            self.sock.close()
            self.signals.result_log.emit(txt_log)
            self.signals.error_read.emit(e)

    def sendData(self, msg):
        self.sock.send(msg)
        txt_log = 'Посылка отправлена на сервер'
        self.signals.result_log.emit(txt_log)

    def closeConnect(self):
        self.cycle = False
        self.sock.close()
        txt_log = 'Разрыв соединения'
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
                    txt_log = 'Попытка подключения Базовой станции №' + str(self.adr_dev)
                else:
                    txt_log = 'Неудачная попытка подключения Базовой станции №' + str(self.adr_dev)
                    self.signals.check_cam.emit(self.adr_dev, False)
            else:
                rq = self.client.write_registers(8192, [0], unit=self.adr_dev)
                if not rq.isError():
                    txt_log = 'Попытка отключения Базовой станции №' + str(self.adr_dev)
                else:
                    txt_log = 'Неудачная попытка отключения Базовой станции №' + str(self.adr_dev)
                    self.signals.check_cam.emit(self.adr_dev, True)
            Reader.signals.result_log.emit(txt_log)


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
        self.sens_regs = [4103, 4108, 4113]
        self.flag_write = False

    @pyqtSlot()
    def run(self):
        while self.cycle:
            try:
                if not self.is_run:
                    time.sleep(1)
                else:
                    result_list = []
                    for i in range(1, 17):
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
                                for j in range(3):
                                    temp_arr.append(['off', 'off', 'off'])

                        else:
                            txt_log = 'Базовая станция №' + str(i) + ' не отвечает'
                            self.signals.result_log.emit(txt_log)
                            for j in range(3):
                                temp_arr.append(['err', 'err', 'err'])

                        result_list.append(temp_arr)
                        time.sleep(0.1)

                    self.signals.result_temp.emit(result_list)
                    time.sleep(0.5)

            except Exception as e:
                self.signals.error_read.emit(e)

    def startProcess(self):
        self.cycle = True
        self.is_run = True
        txt_log = 'Процесс чтения запущен'
        self.signals.result_log.emit(txt_log)

    def exitProcess(self):
        self.cycle = False
        txt_log = 'Выход из процесса чтения'
        self.signals.result_log.emit(txt_log)
