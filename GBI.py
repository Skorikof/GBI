import sys
from Controller import ChangeUi
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QStyle, QAction, QMenu, qApp


class ApplicationWindow(ChangeUi):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.initTray()
        self.tray_icon.show()

    def initTray(self):
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
            self.tray_icon.setToolTip('Температура бетона')
            show_action = QAction("Развернуть программу", self)
            quit_action = QAction("Выход из программы", self)
            hide_action = QAction("Свернуть программу", self)
            show_action.triggered.connect(self.showNormal)
            hide_action.triggered.connect(self.hide)
            quit_action.triggered.connect(self.closeEvent)
            tray_menu = QMenu()
            tray_menu.addAction(show_action)
            tray_menu.addAction(hide_action)
            tray_menu.addAction(quit_action)
            self.tray_icon.setContextMenu(tray_menu)

        except Exception as e:
            self.saveLog('error', str(e))

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
            qApp.quit()

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
