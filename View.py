import sys
import LogPrg
from Thread import Reader, Writer, Connection
from ReadSettings import COMSettings, DataPortal, DataCam, DataSens, Registers
from datetime import datetime
from MainUi import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal, QThreadPool


class WindowSignals(QObject):
    signalStart = pyqtSignal()
    signalConnect = pyqtSignal(str, int)
    signalPause = pyqtSignal()
    signalWrite = pyqtSignal(bool, int, bool)
    signalExit = pyqtSignal()
    signalDisconnect = pyqtSignal()


class ChangeUi(QMainWindow):
    def __init__(self):
        super(ChangeUi, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logger = LogPrg.get_logger(__name__)
        self.signals = WindowSignals()
        self.set_port = COMSettings(self.logger)
        self.initCheck()
        self.initSocket()

    def initSocket(self):
        try:
            self.connect = Connection(self.set_port.IP_adr, self.set_port.local_port)
            self.signals.signalConnect.connect(self.connect.startConnect)
            self.signals.signalDisconnect.connect(self.connect.closeConnect)
            self.threadpool.start(self.connect)
            self.startConnect()

        except Exception as e:
            self.logger.error(e)

    def startConnect(self):
        self.signals.signalConnect.emit(self.set_port.IP_adr, self.set_port.local_port)

    def closeConnect(self):
        self.signals.signalDisconnect.emit()

    def threadInit(self):
        try:
            self.threadpool = QThreadPool()
            self.reader = Reader(self.set_port.client)
            self.reader.signals.result_temp.connect(self.readResult)
            self.reader.signals.check_cam.connect(self.cancel_check)
            self.reader.signals.error_read.connect(self.readError)
            self.reader.signals.result_log.connect(self.readLog)
            self.signals.signalStart.connect(self.reader.startProcess)
            self.signals.signalExit.connect(self.reader.exitProcess)
            self.threadpool.start(self.reader)
            self.startThread()

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
            self.writer = Writer(self.set_port.client, adr, state)
            self.threadpool.start(self.writer)

        except Exception as e:
            self.logger.error(e)

    def cancel_check(self, adr, command):
        try:
            if adr == 1:
                if command:
                    self.ui.cam1_checkBox.setChecked(True)
                else:
                    self.ui.cam1_checkBox.setChecked(False)
            if adr == 2:
                if command:
                    self.ui.cam2_checkBox.setChecked(True)
                else:
                    self.ui.cam2_checkBox.setChecked(False)
            if adr == 3:
                if command:
                    self.ui.cam3_checkBox.setChecked(True)
                else:
                    self.ui.cam3_checkBox.setChecked(False)
            if adr == 4:
                if command:
                    self.ui.cam4_checkBox.setChecked(True)
                else:
                    self.ui.cam4_checkBox.setChecked(False)
            if adr == 5:
                if command:
                    self.ui.cam5_checkBox.setChecked(True)
                else:
                    self.ui.cam5_checkBox.setChecked(False)
            if adr == 6:
                if command:
                    self.ui.cam6_checkBox.setChecked(True)
                else:
                    self.ui.cam6_checkBox.setChecked(False)
            if adr == 7:
                if command:
                    self.ui.cam7_checkBox.setChecked(True)
                else:
                    self.ui.cam7_checkBox.setChecked(False)
            if adr == 8:
                if command:
                    self.ui.cam8_checkBox.setChecked(True)
                else:
                    self.ui.cam8_checkBox.setChecked(False)

        except Exception as e:
            self.logger.error(e)

    def readResult(self, arr):
        try:
            self.arr = arr
            print(self.arr)
            txt_log = 'Parcel received: ' + str(datetime.now())[:-7]
            self.ui.info_label.setText(txt_log)
            self.logger.info(txt_log)

            self.dataPortal = DataPortal()
            for i in range(4):
                self.dataPortal.portal.append(DataCam())
                for j in range(8):
                    self.dataPortal.portal[i].cam.append(DataSens())
                    for k in range(3):
                        self.dataPortal.portal[i].cam[j].sens.append(Registers())
                        self.dataPortal.portal[i].cam[j].sens[k].temp = self.dopCodeBintoDec('Temp', arr[i][j][0])
                        self.dataPortal.portal[i].cam[j].sens[k].serial = arr[i][j][1]
                        self.dataPortal.portal[i].cam[j].sens[k].bat = self.dopCodeBintoDec('Bat', arr[i][j][2])

            self.monitorSerialPort1()
            self.monitorTempPort1()
            self.monitorBatPort1()

        except Exception as e:
            self.logger.error(e)

    def monitorSerialPort1(self):
        try:
            self.ui.cam1_sens1serial_label.setText(self.dataPortal.portal[0].cam[0].sens[0].serial)
            self.ui.cam1_sens2serial_label.setText(self.dataPortal.portal[0].cam[0].sens[1].serial)
            self.ui.cam1_sens3serial_label.setText(self.dataPortal.portal[0].cam[0].sens[2].serial)

            self.ui.cam2_sens1serial_label.setText(self.dataPortal.portal[0].cam[1].sens[0].serial)
            self.ui.cam2_sens2serial_label.setText(self.dataPortal.portal[0].cam[1].sens[1].serial)
            self.ui.cam2_sens3serial_label.setText(self.dataPortal.portal[0].cam[1].sens[2].serial)

            self.ui.cam3_sens1serial_label.setText(self.dataPortal.portal[0].cam[2].sens[0].serial)
            self.ui.cam3_sens2serial_label.setText(self.dataPortal.portal[0].cam[2].sens[1].serial)
            self.ui.cam3_sens3serial_label.setText(self.dataPortal.portal[0].cam[2].sens[2].serial)

            self.ui.cam4_sens1serial_label.setText(self.dataPortal.portal[0].cam[3].sens[0].serial)
            self.ui.cam4_sens2serial_label.setText(self.dataPortal.portal[0].cam[3].sens[1].serial)
            self.ui.cam4_sens3serial_label.setText(self.dataPortal.portal[0].cam[3].sens[2].serial)

            self.ui.cam5_sens1serial_label.setText(self.dataPortal.portal[0].cam[4].sens[0].serial)
            self.ui.cam5_sens2serial_label.setText(self.dataPortal.portal[0].cam[4].sens[1].serial)
            self.ui.cam5_sens3serial_label.setText(self.dataPortal.portal[0].cam[4].sens[2].serial)

            self.ui.cam6_sens1serial_label.setText(self.dataPortal.portal[0].cam[5].sens[0].serial)
            self.ui.cam6_sens2serial_label.setText(self.dataPortal.portal[0].cam[5].sens[1].serial)
            self.ui.cam6_sens3serial_label.setText(self.dataPortal.portal[0].cam[5].sens[2].serial)

            self.ui.cam7_sens1serial_label.setText(self.dataPortal.portal[0].cam[6].sens[0].serial)
            self.ui.cam7_sens2serial_label.setText(self.dataPortal.portal[0].cam[6].sens[1].serial)
            self.ui.cam7_sens3serial_label.setText(self.dataPortal.portal[0].cam[6].sens[2].serial)

            self.ui.cam8_sens1serial_label.setText(self.dataPortal.portal[0].cam[7].sens[0].serial)
            self.ui.cam8_sens2serial_label.setText(self.dataPortal.portal[0].cam[7].sens[1].serial)
            self.ui.cam8_sens3serial_label.setText(self.dataPortal.portal[0].cam[7].sens[2].serial)

        except Exception as e:
            self.logger.error(e)

    def monitorTempPort1(self):
        try:
            self.ui.cam1_sens1temp_lcdNum.display(self.dataPortal.portal[0].cam[0].sens[0].temp)
            self.ui.cam1_sens2temp_lcdNum.display(self.dataPortal.portal[0].cam[0].sens[1].temp)
            self.ui.cam1_sens3temp_lcdNum.display(self.dataPortal.portal[0].cam[0].sens[2].temp)

            self.ui.cam2_sens1temp_lcdNum.display(self.dataPortal.portal[0].cam[1].sens[0].temp)
            self.ui.cam2_sens2temp_lcdNum.display(self.dataPortal.portal[0].cam[1].sens[1].temp)
            self.ui.cam2_sens3temp_lcdNum.display(self.dataPortal.portal[0].cam[1].sens[2].temp)

            self.ui.cam3_sens1temp_lcdNum.display(self.dataPortal.portal[0].cam[2].sens[0].temp)
            self.ui.cam3_sens2temp_lcdNum.display(self.dataPortal.portal[0].cam[2].sens[1].temp)
            self.ui.cam3_sens3temp_lcdNum.display(self.dataPortal.portal[0].cam[2].sens[2].temp)

            self.ui.cam4_sens1temp_lcdNum.display(self.dataPortal.portal[0].cam[3].sens[0].temp)
            self.ui.cam4_sens2temp_lcdNum.display(self.dataPortal.portal[0].cam[3].sens[1].temp)
            self.ui.cam4_sens3temp_lcdNum.display(self.dataPortal.portal[0].cam[3].sens[2].temp)

            self.ui.cam5_sens1temp_lcdNum.display(self.dataPortal.portal[0].cam[4].sens[0].temp)
            self.ui.cam5_sens2temp_lcdNum.display(self.dataPortal.portal[0].cam[4].sens[1].temp)
            self.ui.cam5_sens3temp_lcdNum.display(self.dataPortal.portal[0].cam[4].sens[2].temp)

            self.ui.cam6_sens1temp_lcdNum.display(self.dataPortal.portal[0].cam[5].sens[0].temp)
            self.ui.cam6_sens2temp_lcdNum.display(self.dataPortal.portal[0].cam[5].sens[1].temp)
            self.ui.cam6_sens3temp_lcdNum.display(self.dataPortal.portal[0].cam[5].sens[2].temp)

            self.ui.cam7_sens1temp_lcdNum.display(self.dataPortal.portal[0].cam[6].sens[0].temp)
            self.ui.cam7_sens2temp_lcdNum.display(self.dataPortal.portal[0].cam[6].sens[1].temp)
            self.ui.cam7_sens3temp_lcdNum.display(self.dataPortal.portal[0].cam[6].sens[2].temp)

            self.ui.cam8_sens1temp_lcdNum.display(self.dataPortal.portal[0].cam[7].sens[0].temp)
            self.ui.cam8_sens2temp_lcdNum.display(self.dataPortal.portal[0].cam[7].sens[1].temp)
            self.ui.cam8_sens3temp_lcdNum.display(self.dataPortal.portal[0].cam[7].sens[2].temp)

        except Exception as e:
            self.logger.error(e)

    def monitorBatPort1(self):
        try:
            self.ui.cam1_sens1bat_lcdNum.display(self.dataPortal.portal[0].cam[0].sens[0].bat)
            self.ui.cam1_sens2bat_lcdNum.display(self.dataPortal.portal[0].cam[0].sens[1].bat)
            self.ui.cam1_sens3bat_lcdNum.display(self.dataPortal.portal[0].cam[0].sens[2].bat)

            self.ui.cam2_sens1bat_lcdNum.display(self.dataPortal.portal[0].cam[1].sens[0].bat)
            self.ui.cam2_sens2bat_lcdNum.display(self.dataPortal.portal[0].cam[1].sens[1].bat)
            self.ui.cam2_sens3bat_lcdNum.display(self.dataPortal.portal[0].cam[1].sens[2].bat)

            self.ui.cam3_sens1bat_lcdNum.display(self.dataPortal.portal[0].cam[2].sens[0].bat)
            self.ui.cam3_sens2bat_lcdNum.display(self.dataPortal.portal[0].cam[2].sens[1].bat)
            self.ui.cam3_sens3bat_lcdNum.display(self.dataPortal.portal[0].cam[2].sens[2].bat)

            self.ui.cam4_sens1bat_lcdNum.display(self.dataPortal.portal[0].cam[3].sens[0].bat)
            self.ui.cam4_sens2bat_lcdNum.display(self.dataPortal.portal[0].cam[3].sens[1].bat)
            self.ui.cam4_sens3bat_lcdNum.display(self.dataPortal.portal[0].cam[3].sens[2].bat)

            self.ui.cam5_sens1bat_lcdNum.display(self.dataPortal.portal[0].cam[4].sens[0].bat)
            self.ui.cam5_sens2bat_lcdNum.display(self.dataPortal.portal[0].cam[4].sens[1].bat)
            self.ui.cam5_sens3bat_lcdNum.display(self.dataPortal.portal[0].cam[4].sens[2].bat)

            self.ui.cam6_sens1bat_lcdNum.display(self.dataPortal.portal[0].cam[5].sens[0].bat)
            self.ui.cam6_sens2bat_lcdNum.display(self.dataPortal.portal[0].cam[5].sens[1].bat)
            self.ui.cam6_sens3bat_lcdNum.display(self.dataPortal.portal[0].cam[5].sens[2].bat)

            self.ui.cam7_sens1bat_lcdNum.display(self.dataPortal.portal[0].cam[6].sens[0].bat)
            self.ui.cam7_sens2bat_lcdNum.display(self.dataPortal.portal[0].cam[6].sens[1].bat)
            self.ui.cam7_sens3bat_lcdNum.display(self.dataPortal.portal[0].cam[6].sens[2].bat)

            self.ui.cam8_sens1bat_lcdNum.display(self.dataPortal.portal[0].cam[7].sens[0].bat)
            self.ui.cam8_sens2bat_lcdNum.display(self.dataPortal.portal[0].cam[7].sens[1].bat)
            self.ui.cam8_sens3bat_lcdNum.display(self.dataPortal.portal[0].cam[7].sens[2].bat)

        except Exception as e:
            self.logger.error(e)

    def dopCodeBintoDec(self, command, value, bits=16):
        """Переводит бинарную строку в двоичном коде в десятичное число"""
        if value == 'err':
            return 'err'
        if value == 'off':
            return 'off'
        if value[0] == '1':
            val_temp = -(2 ** bits - int(value, 2))
        else:
            val_temp = int(value, 2)

        if command == 'Temp':
            val_temp = round(val_temp / 16, 1)
            if val_temp < -50:
                return '-----'

        if command == 'Bat':
            val_temp = round(val_temp * 0.1, 1)

        return str(val_temp)