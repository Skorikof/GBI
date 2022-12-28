import sys
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
            if self.set_port.active_log == '1':
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
        window.startParam()
        window.threadInit()
        window.initCheck()
        if window.set_port.activ_online == '1':
            window.initSocket()

    except Exception as e:
        window.saveLog('error', str(e))

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
