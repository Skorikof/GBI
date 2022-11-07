import sys
import time
import LogPrg
from View import ChangeUi
from PyQt5.QtWidgets import QApplication


class ApplicationWindow(ChangeUi):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.logger = LogPrg.get_logger(__name__)

    def closeEvent(self, event):
        try:
            print('Threads working: ', str(self.threadpool.activeThreadCount()))
            self.exitThread()
            self.threadpool.waitForDone()
            print('Threads working: ', str(self.threadpool.activeThreadCount()))
            self.set_port.client.close()
            self.logger.info('Exit programm')

        except Exception as e:
            self.logger.error(e)

def main():
    app = QApplication(sys.argv)
    window = ApplicationWindow()
    window.show()
    try:
        if not window.set_port.initPort():
            window.ui.info_label.setText('Отсутствует подключение по порту: ' + window.set_port.portNumber)
        else:
            txt_log = 'Programm starting!'
            print(txt_log)
            window.logger.info(txt_log)

    except Exception as e:
        window.logger.error(e)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
