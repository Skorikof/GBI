import LogPrg
import time
from Thread import Runner
from ReadSettings import DataCheck, DataSensBin, DataSensInt, COMSettings
from Archive import ReadArchive
from datetime import datetime
from MainUi import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThreadPool


class WindowSignals(QObject):
    signalStart = pyqtSignal()
    signalExit = pyqtSignal()


class ChangeUi(QMainWindow):
    def __init__(self):
        super(ChangeUi, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logger = LogPrg.get_logger(__name__)
        self.signals = WindowSignals()
        self.set_port = COMSettings(self.logger)
        self.dataCheck = DataCheck()
        self.initCheck()

    def threadInit(self):
        try:
            self.threadpool = QThreadPool()
            self.reader = Runner(self.set_port.client)
            self.reader.signals.result_temp.connect(self.readResult)
            self.reader.signals.error_read.connect(self.readError)
            self.reader.signals.result_log.connect(self.readLog)
            self.signals.signalStart.connect(self.reader.startProcess)
            self.signals.signalExit.connect(self.reader.exitProcess)
            self.threadpool.start(self.reader)

        except Exception as e:
            self.logger.error(e)

    def startThread(self):
        self.signals.signalStart.emit()

    def exitThread(self):
        self.signals.signalExit.emit()

    def initCheck(self):
        try:
            self.ui.cam1_checkBox.stateChanged.connect(lambda: self.result_check(1, self.ui.cam1_checkBox.isChecked()))
            self.ui.cam2_checkBox.stateChanged.connect(lambda: self.result_check(2, self.ui.cam2_checkBox.isChecked()))
            self.ui.cam3_checkBox.stateChanged.connect(lambda: self.result_check(3, self.ui.cam3_checkBox.isChecked()))
            self.ui.cam4_checkBox.stateChanged.connect(lambda: self.result_check(4, self.ui.cam4_checkBox.isChecked()))
            self.ui.cam5_checkBox.stateChanged.connect(lambda: self.result_check(5, self.ui.cam5_checkBox.isChecked()))
            self.ui.cam6_checkBox.stateChanged.connect(lambda: self.result_check(6, self.ui.cam6_checkBox.isChecked()))
            self.ui.cam7_checkBox.stateChanged.connect(lambda: self.result_check(7, self.ui.cam7_checkBox.isChecked()))
            self.ui.cam8_checkBox.stateChanged.connect(lambda: self.result_check(8, self.ui.cam8_checkBox.isChecked()))

        except Exception as e:
            self.logger.error(e)

    def result_check(self, adr, state):
        try:
            if state:
                self.signals.signalStart.emit(adr)

        except Exception as e:
            self.logger.error(e)

    def readLog(self, text):
        self.ui.info_label.setText(text)
        self.logger.info(text)
        print(text)

    def readResult(self, list_value):
        txt_log = 'Parcel received: ' + str(datetime.now())[:-7]
        self.ui.info_label.setText(txt_log)
        print(list_value)
        self.logger.info(txt_log)
        self.logger.info(list_value)
        self.parsMsgBin(list_value)
        self.convertMsg(list_value)

    def readError(self, temp):
        print(temp)
        self.logger.error(temp)

    def parsMsgBin(self, msgBin):
        try:
            self.dataBin = DataSensBin()
            self.dataBin.cam1 = msgBin[0]
            self.dataBin.cam2 = msgBin[1]
            self.dataBin.cam3 = msgBin[2]
            self.dataBin.cam4 = msgBin[3]
            self.dataBin.cam5 = msgBin[4]
            self.dataBin.cam6 = msgBin[5]
            self.dataBin.cam7 = msgBin[6]
            self.dataBin.cam8 = msgBin[7]

        except Exception as e:
            self.logger.error(e)

    def convertMsg(self, bin_list):
        try:
            self.dataInt = DataSensInt()
            temp_arr = []
            for i in range(8):
                temp_list = []
                for j in range(3):
                    temp_val = self.dopCodeBintoDec(bin_list[i][j]) / 2
                    temp_list.append(temp_val)
                temp_arr.append(temp_list)

            print(temp_arr)

            self.dataInt.cam1 = temp_arr[0]
            self.dataInt.cam2 = temp_arr[1]
            self.dataInt.cam3 = temp_arr[2]
            self.dataInt.cam4 = temp_arr[3]
            self.dataInt.cam5 = temp_arr[4]
            self.dataInt.cam6 = temp_arr[5]
            self.dataInt.cam7 = temp_arr[6]
            self.dataInt.cam8 = temp_arr[7]
            self.fillingTemp()
            self.saveFiletoArch()

        except Exception as e:
            self.logger.error(e)

    def fillingTemp(self):
        try:
            self.ui.cam1_sens1temp_lcdNum.display(self.dataInt.cam1[0])
            self.ui.cam1_sens2temp_lcdNum.display(self.dataInt.cam1[1])
            self.ui.cam1_sens3temp_lcdNum.display(self.dataInt.cam1[2])

            self.ui.cam2_sens1temp_lcdNum.display(self.dataInt.cam2[0])
            self.ui.cam2_sens2temp_lcdNum.display(self.dataInt.cam2[1])
            self.ui.cam2_sens3temp_lcdNum.display(self.dataInt.cam2[2])

            self.ui.cam3_sens1temp_lcdNum.display(self.dataInt.cam3[0])
            self.ui.cam3_sens2temp_lcdNum.display(self.dataInt.cam3[1])
            self.ui.cam3_sens3temp_lcdNum.display(self.dataInt.cam3[2])

            self.ui.cam4_sens1temp_lcdNum.display(self.dataInt.cam4[0])
            self.ui.cam4_sens2temp_lcdNum.display(self.dataInt.cam4[1])
            self.ui.cam4_sens3temp_lcdNum.display(self.dataInt.cam4[2])

            self.ui.cam5_sens1temp_lcdNum.display(self.dataInt.cam5[0])
            self.ui.cam5_sens2temp_lcdNum.display(self.dataInt.cam5[1])
            self.ui.cam5_sens3temp_lcdNum.display(self.dataInt.cam5[2])

            self.ui.cam6_sens1temp_lcdNum.display(self.dataInt.cam6[0])
            self.ui.cam6_sens2temp_lcdNum.display(self.dataInt.cam6[1])
            self.ui.cam6_sens3temp_lcdNum.display(self.dataInt.cam6[2])

            self.ui.cam7_sens1temp_lcdNum.display(self.dataInt.cam7[0])
            self.ui.cam7_sens2temp_lcdNum.display(self.dataInt.cam7[1])
            self.ui.cam7_sens3temp_lcdNum.display(self.dataInt.cam7[2])

            self.ui.cam8_sens1temp_lcdNum.display(self.dataInt.cam8[0])
            self.ui.cam8_sens2temp_lcdNum.display(self.dataInt.cam8[1])
            self.ui.cam8_sens3temp_lcdNum.display(self.dataInt.cam8[2])

        except Exception as e:
            self.logger.error(e)

    def dopCodeBintoDec(self, value, bits=16):
        """Переводит бинарную строку в двоичном коде в десятичное число"""
        if value[:1] == '1':
            val_temp = -(2 ** bits - int(value, 2))
        else:
            val_temp = int(value, 2)

        return val_temp

    def archiveRead(self):
        try:
            self.archive = ReadArchive()

        except Exception as e:
            self.logger.error(e)

    def saveFiletoArch(self):
        try:
            name_arch = str(datetime.now().day).zfill(2) + '.' + str(datetime.now().month).zfill(2) +\
                        '.' + str(datetime.now().year) + '.csv'
            time_arch = datetime.now().strftime('%H:%M:%S')
            cam1 = str(self.dataInt.cam1) + ';'
            cam2 = str(self.dataInt.cam2) + ';'
            cam3 = str(self.dataInt.cam3) + ';'
            cam4 = str(self.dataInt.cam4) + ';'
            cam5 = str(self.dataInt.cam5) + ';'
            cam6 = str(self.dataInt.cam6) + ';'
            cam7 = str(self.dataInt.cam7) + ';'
            cam8 = str(self.dataInt.cam8) + '\n'
            with open ('archive/'+name_arch, 'a') as file_arch:
                file_arch.write(time_arch + ';' + 'Температура;' + cam1 + cam2 + cam3 + cam4 + cam5 + cam6 + cam7 + cam8)
                file_arch.write(';' + 'Напряжение;' + '\n')

        except Exception as e:
            self.logger.error(e)