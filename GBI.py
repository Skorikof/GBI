import sys
import time
from Controller import ChangeUi
from PyQt5.QtWidgets import QApplication


class ApplicationWindow(ChangeUi):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

    def closeEvent(self, event):
        try:
            print('Threads working: ', str(self.threadpool.activeThreadCount()))
            self.exitThread()
            self.closeConnect()
            self.threadpool.waitForDone()
            print('Threads working: ', str(self.threadpool.activeThreadCount()))
            self.set_port.client.close()
            self.saveLog('info', 'Выход из программы')

        except Exception as e:
            self.saveLog('error', str(e))

def main():
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()
    txt_log = 'Программа запущена'
    print(txt_log)
    try:
        if not window.set_port.initPort():
            txt_log = 'Отсутствует подключение по порту: ' + window.set_port.portNumber
            print(txt_log)
            window.ui.info_label.setText(txt_log)
        else:
            window.threadInit()
            window.initCheck()
            window.startParam()
            #window.initSocket()

    except Exception as e:
        window.saveLog('error', str(e))

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
