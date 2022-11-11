import LogPrg
import time
from Thread import Runner
from ReadSettings import COMSettings, DataCam, DataSens, Registers
from Archive import ReadArchive
from datetime import datetime
from MainUi import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool


class WindowSignals(QObject):
    signalStart = pyqtSignal()
    signalWrite = pyqtSignal(int, bool)
    signalExit = pyqtSignal()


class ChangeUi(QMainWindow):
    def __init__(self):
        super(ChangeUi, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logger = LogPrg.get_logger(__name__)
        self.signals = WindowSignals()
        self.set_port = COMSettings(self.logger)
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
            self.signals.signalWrite.connect(self.reader.startWrite)
            self.threadpool.start(self.reader)

        except Exception as e:
            self.logger.error(e)

    def startThread(self):
        self.signals.signalStart.emit()

    def exitThread(self):
        self.signals.signalExit.emit()

    def readLog(self, text):
        self.ui.info_label.setText(text)
        self.logger.info(text)
        print(text)

    def readError(self, temp):
        print(temp)
        self.logger.error(temp)

    def initCheck(self):
        try:
            self.ui.cam1_checkBox.stateChanged.connect(lambda: self.check_cams(1, self.ui.cam1_checkBox.isChecked()))
            self.ui.cam2_checkBox.stateChanged.connect(lambda: self.check_cams(2, self.ui.cam2_checkBox.isChecked()))
            self.ui.cam3_checkBox.stateChanged.connect(lambda: self.check_cams(3, self.ui.cam3_checkBox.isChecked()))
            self.ui.cam4_checkBox.stateChanged.connect(lambda: self.check_cams(4, self.ui.cam4_checkBox.isChecked()))
            self.ui.cam5_checkBox.stateChanged.connect(lambda: self.check_cams(5, self.ui.cam5_checkBox.isChecked()))
            self.ui.cam6_checkBox.stateChanged.connect(lambda: self.check_cams(6, self.ui.cam6_checkBox.isChecked()))
            self.ui.cam7_checkBox.stateChanged.connect(lambda: self.check_cams(7, self.ui.cam7_checkBox.isChecked()))
            self.ui.cam8_checkBox.stateChanged.connect(lambda: self.check_cams(8, self.ui.cam8_checkBox.isChecked()))

        except Exception as e:
            self.logger.error(e)

    def check_cams(self, adr, state):
        try:
            self.signals.signalWrite.emit(adr, state)

        except Exception as e:
            self.logger.error(e)

    def readResult(self, arr):
        try:
            self.arr = arr
            print(self.arr)
            txt_log = 'Parcel received: ' + str(datetime.now())[:-7]
            self.ui.info_label.setText(txt_log)
            self.logger.info(txt_log)

            self.dataCam = DataCam()
            for i in range(8):
                self.dataCam.cam.append(DataSens())
                for j in range(3):
                    self.dataCam.cam[i].sens.append(Registers())
                    self.dataCam.cam[i].sens[j].temp = arr[i][j][0]
                    self.dataCam.cam[i].sens[j].serial = arr[i][j][1]
                    self.dataCam.cam[i].sens[j].bat = arr[i][j][2]

            self.convertMsgTemp()

        except Exception as e:
            self.logger.error(e)

    def convertMsgTemp(self):
        try:
            if len(self.dataCam.cam[0].sens[0].temp) < 5:
                self.ui.cam1_sens1temp_lcdNum.display(self.dataCam.cam[0].sens[0].temp)
            else:
                self.ui.cam1_sens1temp_lcdNum.display(str(self.dopCodeBintoDec(self.dataCam.cam[0].sens[0].temp)/16))

            if len(self.dataCam.cam[0].sens[1].temp) < 5:
                self.ui.cam1_sens2temp_lcdNum.display(self.dataCam.cam[0].sens[1].temp)
            else:
                self.ui.cam1_sens2temp_lcdNum.display(str(self.dopCodeBintoDec(self.dataCam.cam[0].sens[1].temp)/16))

            if len(self.dataCam.cam[0].sens[2].temp) < 5:
                self.ui.cam1_sens3temp_lcdNum.display(self.dataCam.cam[0].sens[2].temp)
            else:
                self.ui.cam1_sens3temp_lcdNum.display(str(self.dopCodeBintoDec(self.dataCam.cam[0].sens[2].temp)/16))

        except Exception as e:
            self.logger.error(e)

    def dopCodeBintoDec(self, value, bits=16):
        """Переводит бинарную строку в двоичном коде в десятичное число"""
        if value[:1] == '1':
            val_temp = -(2 ** bits - int(value, 2))
        else:
            val_temp = int(value, 2)

        return val_temp

    # def archiveRead(self):
    #     try:
    #         self.archive = ReadArchive()
    #
    #     except Exception as e:
    #         self.logger.error(e)
    #
    # def saveFiletoArch(self):
    #     try:
    #         name_arch = str(datetime.now().day).zfill(2) + '.' + str(datetime.now().month).zfill(2) +\
    #                     '.' + str(datetime.now().year) + '.csv'
    #         time_arch = datetime.now().strftime('%H:%M:%S')
    #         cam1 = str(self.dataInt.cam1) + ';'
    #         cam2 = str(self.dataInt.cam2) + ';'
    #         cam3 = str(self.dataInt.cam3) + ';'
    #         cam4 = str(self.dataInt.cam4) + ';'
    #         cam5 = str(self.dataInt.cam5) + ';'
    #         cam6 = str(self.dataInt.cam6) + ';'
    #         cam7 = str(self.dataInt.cam7) + ';'
    #         cam8 = str(self.dataInt.cam8) + '\n'
    #         with open ('archive/'+name_arch, 'a') as file_arch:
    #             file_arch.write(time_arch + ';' + 'Температура;' + cam1 + cam2 + cam3 + cam4 + cam5 + cam6 + cam7 + cam8)
    #             file_arch.write(';' + 'Напряжение;' + '\n')
    #
    #     except Exception as e:
    #         self.logger.error(e)