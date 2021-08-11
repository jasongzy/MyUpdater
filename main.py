import os
import sys

from PyQt5.QtCore import (
    QCoreApplication,
    QEventLoop,
    QFileSystemWatcher,
    QObject,
    QProcess,
    Qt,
    QThread,
    QTimer,
    QUrl,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QCursor,
    QDesktopServices,
    QFont,
    QIcon,
    QPalette,
    QPixmap,
    QTextCursor,
)
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
)

import apps.archi_steam_farm as asf
import apps.clash_for_windows as cfw
import apps.drawio_desktop as drawio
import apps.office_tool_plus as otp
import apps.ventoy as ventoy
import apps.waifu2x_extension_gui as waifu
import apps.x_prober as xprober
import utils.file_io as file_io
from Ui_updater import Ui_MainWindow

COL_LOGO = 0
COL_NAME = 1
COL_DESC = 2
COL_LOCAL_VERSION = 3
COL_LATEST_VERSION = 4
COL_GITHUB_BUTTON = 5
COL_PATH_BUTTON = 6
COL_UPDATE_BUTTON = 7

ROW_LIST = ["asf", "cfw", "drawio", "otp", "ventoy", "waifu", "xprober"]
NAME_DICT = dict(
    zip(
        ROW_LIST,
        [
            "ArchiSteamFarm",
            "Clash for Windows",
            "draw.io Desktop",
            "Office Tool Plus",
            "Ventoy",
            "Waifu2x Extension GUI",
            "X Prober",
        ],
    )
)
RES_DIR = "res/"
LOGO_DICT = dict(
    zip(
        ROW_LIST,
        list(
            map(
                lambda x: RES_DIR + x,
                [
                    "logo_asf.png",
                    "logo_clash.png",
                    "logo_drawio.png",
                    "logo_otp.png",
                    "logo_ventoy.png",
                    "logo_waifu.png",
                    "php_elephant.png",
                ],
            )
        ),
    )
)
APP_LIST = [asf, cfw, drawio, otp, ventoy, waifu, xprober]
APP_DICT = dict(zip(ROW_LIST, APP_LIST))
CONFIG_PATH = "./config.ini"
PWD = os.getcwd()


class MyThread(QThread):
    def __init__(self, item, action="init", parent=None):
        super().__init__(parent)
        self.item = item
        self.action = action
        self.module = APP_DICT[item]

    def run(self):
        if self.action == "init":
            self.module.init()
        elif self.action == "update":
            print("下载中...")
            self.module.update(True)


class QLabelButton(QLabel):
    clicked = pyqtSignal()
    DoubleClicked = pyqtSignal()

    def __int__(self):
        super().__init__()

    # 重写鼠标单击事件
    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()

    # 重写鼠标双击事件
    def mouseDoubleClickEvent(self, e):
        self.DoubleClicked.emit()


class MyMainWindow(QMainWindow, Ui_MainWindow):
    # 将标准输出重定向到UI所用的*信号*
    consolePrint = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)

        # 将标准输出重定向到UI
        self.stdoutbak = sys.stdout
        self.stderrbak = sys.stderr
        sys.stdout = self
        self.consolePrint.connect(self.print_UI)

        # 窗体背景色
        palette = QPalette()
        palette.setColor(QPalette.Background, Qt.white)
        self.setPalette(palette)
        self.tableWidget.setAlternatingRowColors(True)

        # 行宽、列高均分整个窗口
        # self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 表格不可编辑、不可选中
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
        # self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 选中单位为一行
        self.tableWidget.setFocusPolicy(Qt.NoFocus)
        # self.tableWidget.setShowGrid(True)

        # 动态生成更新按钮和线程的字典，以便之后调用
        self.update_button_dict = {}
        self.thread_init_dict = {}
        self.thread_update_dict = {}
        for item in ROW_LIST:
            self.update_button_dict[item] = QLabelButton()
            self.thread_init_dict[item] = MyThread(item, "init")
            # 用 lambda 传递额外的参数
            # self.thread_dict[item].finished.connect(lambda: self.update_ui(item))
            # // ~~但不知为何，在循环中进行connect会导致所有额外参数(item)都相同~~
            # // ~~手动写每一句connect是可行的~~
            # !更新: 是由于Python的惰性求值特性。见https://zhuanlan.zhihu.com/p/37063984
            # 因此此处改用QObject.sender()的方案
            self.thread_init_dict[item].finished.connect(self.update_ui)
            self.thread_update_dict[item] = MyThread(item, "update")
            self.thread_update_dict[item].finished.connect(self.update_ui_all)
            # 初始化各个APP的基本信息，但不检查更新
            APP_DICT[item].init(False)
        # 添加表格内容
        row_index = 0  # 避免在循环内调用ROW_LIST.index(item)获取行号
        for item in ROW_LIST:
            self.tableWidget.insertRow(row_index)
            self.tableWidget.setRowHeight(row_index, 64)
            # name
            name = QTableWidgetItem(" " * 3 + NAME_DICT[item])
            self.tableWidget.setItem(row_index, COL_NAME, name)
            # logo
            label_logo = QLabelButton()
            label_logo.setPixmap(QPixmap(LOGO_DICT[item]).scaledToWidth(40))
            label_logo.setAlignment(Qt.AlignCenter)
            self.tableWidget.setCellWidget(row_index, COL_LOGO, label_logo)
            label_logo.DoubleClicked.connect(
                lambda exe=APP_DICT[item].app.exe_path: (
                    os.chdir(os.path.dirname(exe)),
                    QDesktopServices.openUrl(QUrl.fromLocalFile(exe)),
                    os.chdir(PWD),
                )
            )
            # github_button
            label_github = QLabelButton()
            label_github.setPixmap(QPixmap(RES_DIR + "github.svg").scaledToWidth(35))
            label_github.setCursor(QCursor(Qt.PointingHandCursor))
            label_github.setAlignment(Qt.AlignCenter)
            label_github.setToolTip(APP_DICT[item].app.repo_url)
            self.tableWidget.setCellWidget(row_index, COL_GITHUB_BUTTON, label_github)
            # 为lambda添加默认参数以解决惰性求值问题
            label_github.clicked.connect(
                lambda url=APP_DICT[item].app.repo_url: QDesktopServices.openUrl(
                    QUrl(url)
                )
            )
            # path_button
            label_dir = QLabelButton()
            label_dir.setPixmap(QPixmap(RES_DIR + "folder.svg").scaledToWidth(35))
            label_dir.setCursor(QCursor(Qt.PointingHandCursor))
            label_dir.setAlignment(Qt.AlignCenter)
            self.tableWidget.setCellWidget(row_index, COL_PATH_BUTTON, label_dir)
            label_dir.clicked.connect(
                lambda path=APP_DICT[item].app.local_dir: QDesktopServices.openUrl(
                    QUrl.fromLocalFile(path)
                )
            )
            # update_button
            label_update = self.update_button_dict[item]
            label_update.setPixmap(QPixmap(RES_DIR + "update.svg").scaledToWidth(35))
            label_update.setCursor(QCursor(Qt.PointingHandCursor))
            label_update.setAlignment(Qt.AlignCenter)
            label_update.setEnabled(False)
            self.tableWidget.setCellWidget(row_index, COL_UPDATE_BUTTON, label_update)
            label_update.clicked.connect(
                lambda item=item: self.thread_update_dict[item].start()
            )
            # 描述
            desc = QTableWidgetItem(APP_DICT[item].app.repo)
            desc_font = QFont()
            desc_font.setFamily("Microsoft YaHei UI")
            desc_font.setPixelSize(14)
            desc.setFont(desc_font)
            self.tableWidget.setItem(row_index, COL_DESC, desc)
            # 记得手动更新row_index
            row_index += 1

        # 手动调整列宽
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            COL_LOGO, QHeaderView.Interactive
        )
        self.tableWidget.setColumnWidth(COL_LOGO, 80)
        # name、desc列自适应
        # 版本和按钮列固定宽度
        for col_index in range(COL_LOCAL_VERSION, COL_LATEST_VERSION + 1):
            self.tableWidget.horizontalHeader().setSectionResizeMode(
                col_index, QHeaderView.Interactive
            )
            self.tableWidget.setColumnWidth(col_index, 100)
        for col_index in range(COL_GITHUB_BUTTON, COL_UPDATE_BUTTON + 1):
            self.tableWidget.horizontalHeader().setSectionResizeMode(
                col_index, QHeaderView.Interactive
            )
            self.tableWidget.setColumnWidth(col_index, 50)

        # 刷新按钮
        self.refreshButton.clicked.connect(self.onButtonClicked)
        # self.refreshButton.setIcon(QIcon(RES_DIR + "refresh.svg"))
        # self.refreshButton.setIconSize(QSize(60, 60))
        self.checked_list = []  # 记录检查完毕的item
        self.counter_num = 0

        # 实时监测config.ini的改动
        self.config_watcher = QFileSystemWatcher()
        self.config_watcher.addPath(CONFIG_PATH)
        self.config_watcher.fileChanged.connect(self.config_changed)

        # 定时器用于在窗口显示后执行任务
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.window_showed)
        self.timer.start(1000)

        # __init__到此结束

    # 将标准输出重定向到UI所用的*事件*
    # 在外部调用print时，sys.stdout.write()被重定向到了self.write()
    def write(self, info):
        self.stdoutbak.write(info)
        self.consolePrint.emit(info)
        # !由于涉及多线程，直接在这里更新UI可能导致意外和错误
        # 包括但不限于打印出的字符错乱
        # 因此，更安全的方式是向UI发送信号，在槽函数中更新UI
        # self.terminalText.moveCursor(QTextCursor.End)
        # self.terminalText.insertPlainText(info)
        # QCoreApplication.processEvents(QEventLoop.ExcludeUserInputEvents | QEventLoop.ExcludeSocketNotifiers)

    # 将标准输出重定向到UI所用的*槽函数*
    def print_UI(self, info: str):
        self.terminalText.moveCursor(QTextCursor.End)
        self.terminalText.insertPlainText(info)
        QCoreApplication.processEvents(
            QEventLoop.ExcludeUserInputEvents | QEventLoop.ExcludeSocketNotifiers
        )

    def thread_start_all(self):
        for item in ROW_LIST:
            self.thread_init_dict[item].start()

    def thread_stop_all(self):
        for item in ROW_LIST:
            # self.thread_init_dict[item].terminate()
            self.thread_init_dict[item].quit()

    def update_ui(self, item="", info=True):
        if not item:
            item = QObject.sender(self).item
        row_index = ROW_LIST.index(item)
        app = APP_DICT[item].app
        version_font = QFont()
        version_font.setFamily("Arial")
        version_font.setPixelSize(16)

        # local_version
        local_version = QTableWidgetItem(app.local_version)
        local_version.setFont(version_font)
        local_version.setTextAlignment(Qt.AlignCenter)
        self.tableWidget.setItem(row_index, COL_LOCAL_VERSION, local_version)
        # latest_version
        latest_version = QTableWidgetItem(app.latest_version)
        latest_version.setFont(version_font)
        latest_version.setTextAlignment(int(Qt.AlignLeft | Qt.AlignVCenter))
        self.tableWidget.setItem(row_index, COL_LATEST_VERSION, latest_version)
        is_latest = app.is_latest()
        if is_latest == 1:
            latest_version.setIcon(QIcon(RES_DIR + "equal.svg"))
            self.update_button_dict[item].setEnabled(False)
        elif is_latest == 0:
            latest_version.setIcon(QIcon(RES_DIR + "right.svg"))
            self.update_button_dict[item].setEnabled(True)
            self.counter_num += 1
            # self.set_row_background_color(row_index, 197, 237, 226)
        elif is_latest == -1:
            local_version.setText("未知")
            latest_version.setIcon(QIcon(RES_DIR + "right.svg"))
            self.update_button_dict[item].setEnabled(True)
            self.counter_num += 1
        else:
            latest_version.setIcon(QIcon(RES_DIR + "error.svg"))
            self.update_button_dict[item].setEnabled(False)
            # self.set_row_background_color(row_index, 250, 214, 214)
            print("%s：无法找到最新版本下载地址！" % NAME_DICT[item])

        self.counter.setText(
            '<html><head/><body><p><span style=" color:#fe4365;">%d</span></p></body></html>'
            % self.counter_num
        )
        self.checked_list.append(item)
        if info:
            if set(ROW_LIST).issubset(self.checked_list):
                print("全部检查完毕！")

    # def set_row_background_color(self, row_index, r, g, b):
    #     self.tableWidget.cellWidget(row_index, COL_LOGO).setStyleSheet(
    #         "QLabelButton{background-color:rgb(%d,%d,%d);}" % (r, g, b)
    #     )
    #     for col_index in range(COL_NAME, COL_LATEST_VERSION):
    #         self.tableWidget.item(row_index, col_index).setBackground(QColor(r, g, b))

    def update_ui_all(self):
        self.counter_num = 0
        for item in ROW_LIST:
            self.update_ui(item, False)

    def config_changed(self):
        self.config_watcher.removePath(CONFIG_PATH)
        choice = QMessageBox.information(
            self,
            "配置文件已修改",
            "新配置将在软件重启后生效\n是否重新启动？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if choice == QMessageBox.Yes:
            MainApp.quit()
            # 重启
            QProcess.startDetached(QApplication.applicationFilePath())
        else:
            self.config_watcher.addPath(CONFIG_PATH)

    def window_showed(self):
        self.timer.stop()
        print("启动完成，自动检查更新...")
        self.thread_start_all()

    def onButtonClicked(self):
        self.thread_stop_all()
        print("检查更新中...")
        self.checked_list = []
        self.counter_num = 0
        self.thread_start_all()


if __name__ == "__main__":
    MainApp = QApplication(sys.argv)
    if file_io.update_config(CONFIG_PATH):
        QMessageBox.critical(None, "错误", "配置文件存在严重错误，\n请修正后再启动！")
        QDesktopServices.openUrl(QUrl.fromLocalFile(CONFIG_PATH))
        sys.exit()
    for id in ROW_LIST:
        enabled = file_io.get_config(id, "enabled", False)
        if enabled == "0":
            ROW_LIST.remove(id)
            APP_LIST.remove(globals()[id])
            NAME_DICT.pop(id)
            LOGO_DICT.pop(id)
            APP_DICT.pop(id)
    MainWindow = MyMainWindow()
    MainWindow.show()
    sys.exit(MainApp.exec_())
