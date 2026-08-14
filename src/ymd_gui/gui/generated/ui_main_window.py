# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenuBar,
    QPlainTextEdit, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

from ymd_gui.gui.widgets.animated_background import AnimatedBackground

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(611, 887)
        MainWindow.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        MainWindow.setStyleSheet(u"/* ========================================\n"
"   \u041e\u0421\u041d\u041e\u0412\u0410\n"
"   ======================================== */\n"
"\n"
"QWidget {\n"
"    color: #F2F2F2;\n"
"}\n"
"\n"
"QLabel {\n"
"    color: #EDEDED;\n"
"    background: transparent;\n"
"}\n"
"\n"
"\n"
"/* \u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a */\n"
"\n"
"QLabel#labelTitle {\n"
"    color: #FFFFFF;\n"
"    background: transparent;\n"
"\n"
"    font-size: 24px;\n"
"    font-weight: 700;\n"
"}\n"
"\n"
"\n"
"/* ========================================\n"
"   \u041f\u041e\u041b\u042f\n"
"   ======================================== */\n"
"\n"
"QLineEdit,\n"
"QComboBox,\n"
"QPlainTextEdit {\n"
"    color: #F4F4F4;\n"
"\n"
"    background-color: rgba(28, 28, 28, 225);\n"
"\n"
"    border: 1px solid rgba(255, 255, 255, 22);\n"
"    border-radius: 10px;\n"
"\n"
"    padding: 7px 10px;\n"
"\n"
"    selection-background-color: #FFCC00;\n"
"    selection-color: #111111;\n"
"}\n"
"\n"
"\n"
"QLineEdit:hover,\n"
"QComboBox:hover,"
                        "\n"
"QPlainTextEdit:hover {\n"
"    background-color: rgba(35, 35, 35, 235);\n"
"\n"
"    border: 1px solid rgba(255, 255, 255, 50);\n"
"}\n"
"\n"
"\n"
"QLineEdit:focus,\n"
"QComboBox:focus {\n"
"    background-color: rgba(38, 38, 38, 245);\n"
"\n"
"    border: 1px solid #FFCC00;\n"
"}\n"
"\n"
"\n"
"/* Placeholder */\n"
"\n"
"QLineEdit {\n"
"    color: #F3F3F3;\n"
"}\n"
"\n"
"\n"
"/* ========================================\n"
"   COMBO BOX\n"
"   ======================================== */\n"
"\n"
"QComboBox {\n"
"    padding-right: 30px;\n"
"}\n"
"\n"
"\n"
"QComboBox::drop-down {\n"
"    border: none;\n"
"    width: 28px;\n"
"}\n"
"\n"
"\n"
"QComboBox::down-arrow {\n"
"    width: 8px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    color: #F2F2F2;\n"
"\n"
"    background-color: #1B1B1B;\n"
"\n"
"    border: 1px solid #343434;\n"
"    border-radius: 9px;\n"
"\n"
"    selection-background-color: #FFCC00;\n"
"    selection-color: #111111;\n"
"\n"
"    padding: 5px;\n"
"}\n"
"\n"
""
                        "\n"
"/* ========================================\n"
"   \u041e\u0411\u042b\u0427\u041d\u042b\u0415 \u041a\u041d\u041e\u041f\u041a\u0418\n"
"   ======================================== */\n"
"\n"
"QPushButton {\n"
"    color: #F2F2F2;\n"
"\n"
"    background-color: rgba(42, 42, 42, 235);\n"
"\n"
"    border: 1px solid rgba(255, 255, 255, 28);\n"
"    border-radius: 10px;\n"
"\n"
"    padding: 8px 16px;\n"
"\n"
"    font-weight: 500;\n"
"}\n"
"\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #353535;\n"
"\n"
"    border: 1px solid rgba(255, 255, 255, 65);\n"
"}\n"
"\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #222222;\n"
"\n"
"    border: 1px solid rgba(255, 204, 0, 130);\n"
"}\n"
"\n"
"\n"
"QPushButton:disabled {\n"
"    color: #777777;\n"
"\n"
"    background-color: rgba(30, 30, 30, 180);\n"
"\n"
"    border: 1px solid rgba(255, 255, 255, 15);\n"
"}\n"
"\n"
"\n"
"/* ========================================\n"
"   \u041e\u0421\u041d\u041e\u0412\u041d\u042b\u0415 \u0416\u0401\u041b\u0422\u042b"
                        "\u0415 \u041a\u041d\u041e\u041f\u041a\u0418\n"
"   ======================================== */\n"
"\n"
"QPushButton#pushButtonDownload,\n"
"QPushButton#pushButtonAuthorization {\n"
"    color: #111111;\n"
"\n"
"    background-color: #FFCC00;\n"
"\n"
"    border: none;\n"
"    border-radius: 11px;\n"
"\n"
"    padding: 9px 22px;\n"
"\n"
"    font-weight: 700;\n"
"}\n"
"\n"
"\n"
"QPushButton#pushButtonDownload:hover,\n"
"QPushButton#pushButtonAuthorization:hover {\n"
"    background-color: #FFDA33;\n"
"}\n"
"\n"
"\n"
"QPushButton#pushButtonDownload:pressed,\n"
"QPushButton#pushButtonAuthorization:pressed {\n"
"    background-color: #E7B900;\n"
"}\n"
"\n"
"\n"
"QPushButton#pushButtonDownload:disabled,\n"
"QPushButton#pushButtonAuthorization:disabled {\n"
"    color: #6A6040;\n"
"\n"
"    background-color: #847124;\n"
"}\n"
"\n"
"\n"
"/* ========================================\n"
"   PROGRESS BAR\n"
"   ======================================== */\n"
"\n"
"QProgressBar {\n"
"    color: #EEEEEE;\n"
"\n"
"    backgr"
                        "ound-color: rgba(32, 32, 32, 230);\n"
"\n"
"    border: 1px solid rgba(255, 255, 255, 22);\n"
"    border-radius: 9px;\n"
"\n"
"    text-align: center;\n"
"\n"
"    min-height: 20px;\n"
"\n"
"    font-weight: 600;\n"
"}\n"
"\n"
"\n"
"QProgressBar::chunk {\n"
"    border-radius: 8px;\n"
"\n"
"    background: qlineargradient(\n"
"        x1: 0,\n"
"        y1: 0,\n"
"        x2: 1,\n"
"        y2: 0,\n"
"        stop: 0 #F0B900,\n"
"        stop: 0.55 #FFCC00,\n"
"        stop: 1 #FFE052\n"
"    );\n"
"}\n"
"\n"
"\n"
"/* ========================================\n"
"   \u0416\u0423\u0420\u041d\u0410\u041b\n"
"   ======================================== */\n"
"\n"
"QPlainTextEdit#plainTextEditLog {\n"
"    color: #EAEAEA;\n"
"\n"
"    background-color: rgba(18, 18, 18, 225);\n"
"\n"
"    border: 1px solid rgba(255, 255, 255, 25);\n"
"    border-radius: 12px;\n"
"\n"
"    padding: 9px;\n"
"\n"
"    selection-background-color: #FFCC00;\n"
"    selection-color: #111111;\n"
"}\n"
"\n"
"\n"
"QPlainTextEdit#plainTextEdi"
                        "tLog:hover {\n"
"    background-color: rgba(22, 22, 22, 235);\n"
"\n"
"    border: 1px solid rgba(255, 255, 255, 40);\n"
"}\n"
"\n"
"\n"
"/* ========================================\n"
"   SCROLLBAR\n"
"   ======================================== */\n"
"\n"
"QScrollBar:vertical {\n"
"    background: transparent;\n"
"\n"
"    width: 10px;\n"
"\n"
"    margin: 4px 2px;\n"
"}\n"
"\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background-color: #454545;\n"
"\n"
"    min-height: 30px;\n"
"\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"\n"
"QScrollBar::handle:vertical:hover {\n"
"    background-color: #666666;\n"
"}\n"
"\n"
"\n"
"QScrollBar::add-line:vertical,\n"
"QScrollBar::sub-line:vertical {\n"
"    height: 0px;\n"
"}\n"
"\n"
"\n"
"/* ========================================\n"
"   TOOLTIP\n"
"   ======================================== */\n"
"\n"
"QToolTip {\n"
"    color: #F2F2F2;\n"
"\n"
"    background-color: #242424;\n"
"\n"
"    border: 1px solid #444444;\n"
"    border-radius: 6px;\n"
"\n"
"    padding: 6px"
                        ";\n"
"}\n"
"\n"
"QLabel#labelURL,\n"
"QLabel#labelFolder,\n"
"QLabel#labelQuality,\n"
"QLabel#labelAuthorization,\n"
"QLabel#labelLog {\n"
"    color: #CFCFCF;\n"
"    font-weight: 500;\n"
"}\n"
"\n"
"QMessageBox {\n"
"    background-color: #1B1B1B;\n"
"}\n"
"\n"
"QMessageBox QLabel {\n"
"    color: #F2F2F2;\n"
"    background: transparent;\n"
"}\n"
"\n"
"QMessageBox QPushButton {\n"
"    color: #111111;\n"
"    background-color: #FFCC00;\n"
"    border: none;\n"
"    border-radius: 10px;\n"
"    padding: 7px 18px;\n"
"    min-width: 70px;\n"
"    font-weight: 700;\n"
"}\n"
"\n"
"QMessageBox QPushButton:hover {\n"
"    background-color: #FFDA33;\n"
"}\n"
"\n"
"QMessageBox QPushButton:pressed {\n"
"    background-color: #E7B900;\n"
"}")
        self.centralwidget = AnimatedBackground(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(8)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(18, 16, 18, 16)
        self.labelTitle = QLabel(self.centralwidget)
        self.labelTitle.setObjectName(u"labelTitle")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelTitle.sizePolicy().hasHeightForWidth())
        self.labelTitle.setSizePolicy(sizePolicy)
        font = QFont()
        font.setFamilies([u"Raleway"])
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        self.labelTitle.setFont(font)
        self.labelTitle.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.labelTitle.setFrameShape(QFrame.Shape.NoFrame)
        self.labelTitle.setTextFormat(Qt.TextFormat.AutoText)
        self.labelTitle.setScaledContents(False)
        self.labelTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelTitle.setWordWrap(False)
        self.labelTitle.setMargin(0)
        self.labelTitle.setIndent(-1)

        self.verticalLayout.addWidget(self.labelTitle)

        self.labelURL = QLabel(self.centralwidget)
        self.labelURL.setObjectName(u"labelURL")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.labelURL.sizePolicy().hasHeightForWidth())
        self.labelURL.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(16)
        font1.setWeight(QFont.Medium)
        self.labelURL.setFont(font1)

        self.verticalLayout.addWidget(self.labelURL)

        self.lineEditURL = QLineEdit(self.centralwidget)
        self.lineEditURL.setObjectName(u"lineEditURL")
        font2 = QFont()
        font2.setPointSize(16)
        self.lineEditURL.setFont(font2)
        self.lineEditURL.setClearButtonEnabled(True)

        self.verticalLayout.addWidget(self.lineEditURL)

        self.labelFolder = QLabel(self.centralwidget)
        self.labelFolder.setObjectName(u"labelFolder")
        sizePolicy1.setHeightForWidth(self.labelFolder.sizePolicy().hasHeightForWidth())
        self.labelFolder.setSizePolicy(sizePolicy1)
        self.labelFolder.setFont(font1)

        self.verticalLayout.addWidget(self.labelFolder)

        self.widgetFolder = QWidget(self.centralwidget)
        self.widgetFolder.setObjectName(u"widgetFolder")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.widgetFolder.sizePolicy().hasHeightForWidth())
        self.widgetFolder.setSizePolicy(sizePolicy2)
        self.horizontalLayout_6 = QHBoxLayout(self.widgetFolder)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayoutFolder = QHBoxLayout()
        self.horizontalLayoutFolder.setSpacing(8)
        self.horizontalLayoutFolder.setObjectName(u"horizontalLayoutFolder")
        self.lineEditFolder = QLineEdit(self.widgetFolder)
        self.lineEditFolder.setObjectName(u"lineEditFolder")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.lineEditFolder.sizePolicy().hasHeightForWidth())
        self.lineEditFolder.setSizePolicy(sizePolicy3)
        self.lineEditFolder.setFont(font2)
        self.lineEditFolder.setClearButtonEnabled(True)

        self.horizontalLayoutFolder.addWidget(self.lineEditFolder)

        self.pushButtonFolder = QPushButton(self.widgetFolder)
        self.pushButtonFolder.setObjectName(u"pushButtonFolder")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.pushButtonFolder.sizePolicy().hasHeightForWidth())
        self.pushButtonFolder.setSizePolicy(sizePolicy4)
        self.pushButtonFolder.setFont(font1)
        self.pushButtonFolder.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayoutFolder.addWidget(self.pushButtonFolder)


        self.horizontalLayout_6.addLayout(self.horizontalLayoutFolder)


        self.verticalLayout.addWidget(self.widgetFolder)

        self.widgetQuality = QWidget(self.centralwidget)
        self.widgetQuality.setObjectName(u"widgetQuality")
        self.horizontalLayout_7 = QHBoxLayout(self.widgetQuality)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayoutQuality = QHBoxLayout()
        self.horizontalLayoutQuality.setSpacing(8)
        self.horizontalLayoutQuality.setObjectName(u"horizontalLayoutQuality")
        self.labelQuality = QLabel(self.widgetQuality)
        self.labelQuality.setObjectName(u"labelQuality")
        self.labelQuality.setMinimumSize(QSize(130, 0))
        self.labelQuality.setFont(font1)

        self.horizontalLayoutQuality.addWidget(self.labelQuality)

        self.comboBoxQuality = QComboBox(self.widgetQuality)
        self.comboBoxQuality.addItem("")
        self.comboBoxQuality.addItem("")
        self.comboBoxQuality.addItem("")
        self.comboBoxQuality.addItem("")
        self.comboBoxQuality.addItem("")
        self.comboBoxQuality.addItem("")
        self.comboBoxQuality.setObjectName(u"comboBoxQuality")
        self.comboBoxQuality.setMinimumSize(QSize(160, 0))
        self.comboBoxQuality.setFont(font2)
        self.comboBoxQuality.setEditable(False)

        self.horizontalLayoutQuality.addWidget(self.comboBoxQuality)

        self.horizontalSpacerQuality = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutQuality.addItem(self.horizontalSpacerQuality)


        self.horizontalLayout_7.addLayout(self.horizontalLayoutQuality)


        self.verticalLayout.addWidget(self.widgetQuality)

        self.widgetAuthorization = QWidget(self.centralwidget)
        self.widgetAuthorization.setObjectName(u"widgetAuthorization")
        self.horizontalLayout_4 = QHBoxLayout(self.widgetAuthorization)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayoutAuthorization = QHBoxLayout()
        self.horizontalLayoutAuthorization.setSpacing(8)
        self.horizontalLayoutAuthorization.setObjectName(u"horizontalLayoutAuthorization")
        self.labelAuthorization = QLabel(self.widgetAuthorization)
        self.labelAuthorization.setObjectName(u"labelAuthorization")
        self.labelAuthorization.setMinimumSize(QSize(130, 0))
        self.labelAuthorization.setFont(font1)

        self.horizontalLayoutAuthorization.addWidget(self.labelAuthorization)

        self.pushButtonAuthorization = QPushButton(self.widgetAuthorization)
        self.pushButtonAuthorization.setObjectName(u"pushButtonAuthorization")
        self.pushButtonAuthorization.setMinimumSize(QSize(160, 0))
        font3 = QFont()
        font3.setPointSize(16)
        font3.setBold(True)
        self.pushButtonAuthorization.setFont(font3)
        self.pushButtonAuthorization.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayoutAuthorization.addWidget(self.pushButtonAuthorization)

        self.horizontalSpacerAuthorization = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutAuthorization.addItem(self.horizontalSpacerAuthorization)


        self.horizontalLayout_4.addLayout(self.horizontalLayoutAuthorization)


        self.verticalLayout.addWidget(self.widgetAuthorization)

        self.widgetDownload = QWidget(self.centralwidget)
        self.widgetDownload.setObjectName(u"widgetDownload")
        self.horizontalLayout_5 = QHBoxLayout(self.widgetDownload)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayoutDownload = QHBoxLayout()
        self.horizontalLayoutDownload.setSpacing(8)
        self.horizontalLayoutDownload.setObjectName(u"horizontalLayoutDownload")
        self.horizontalSpacerDownload = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutDownload.addItem(self.horizontalSpacerDownload)

        self.pushButtonDownload = QPushButton(self.widgetDownload)
        self.pushButtonDownload.setObjectName(u"pushButtonDownload")
        sizePolicy2.setHeightForWidth(self.pushButtonDownload.sizePolicy().hasHeightForWidth())
        self.pushButtonDownload.setSizePolicy(sizePolicy2)
        self.pushButtonDownload.setFont(font3)
        self.pushButtonDownload.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.horizontalLayoutDownload.addWidget(self.pushButtonDownload)

        self.horizontalSpacerDownload_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutDownload.addItem(self.horizontalSpacerDownload_2)


        self.horizontalLayout_5.addLayout(self.horizontalLayoutDownload)


        self.verticalLayout.addWidget(self.widgetDownload)

        self.progressBarDownload = QProgressBar(self.centralwidget)
        self.progressBarDownload.setObjectName(u"progressBarDownload")
        font4 = QFont()
        font4.setPointSize(16)
        font4.setWeight(QFont.DemiBold)
        self.progressBarDownload.setFont(font4)
        self.progressBarDownload.setValue(0)

        self.verticalLayout.addWidget(self.progressBarDownload)

        self.labelLog = QLabel(self.centralwidget)
        self.labelLog.setObjectName(u"labelLog")
        self.labelLog.setFont(font1)
        self.labelLog.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout.addWidget(self.labelLog)

        self.plainTextEditLog = QPlainTextEdit(self.centralwidget)
        self.plainTextEditLog.setObjectName(u"plainTextEditLog")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.plainTextEditLog.sizePolicy().hasHeightForWidth())
        self.plainTextEditLog.setSizePolicy(sizePolicy5)
        self.plainTextEditLog.setReadOnly(True)

        self.verticalLayout.addWidget(self.plainTextEditLog)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 611, 22))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Yandex Music Downloader", None))
        self.labelTitle.setText(QCoreApplication.translate("MainWindow", u"Yandex Music Downloader", None))
        self.labelURL.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0441\u044b\u043b\u043a\u0430", None))
        self.lineEditURL.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u0442\u0440\u0435\u043a, \u0430\u043b\u044c\u0431\u043e\u043c \u0438\u043b\u0438 \u043f\u043b\u0435\u0439\u043b\u0438\u0441\u0442", None))
        self.labelFolder.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0430\u043f\u043a\u0430", None))
        self.lineEditFolder.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u043f\u0430\u043f\u043a\u0443 \u0434\u043b\u044f \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f", None))
        self.pushButtonFolder.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0431\u0440\u0430\u0442\u044c...", None))
        self.labelQuality.setText(QCoreApplication.translate("MainWindow", u"\u041a\u0430\u0447\u0435\u0441\u0442\u0432\u043e", None))
        self.comboBoxQuality.setItemText(0, QCoreApplication.translate("MainWindow", u"\u041b\u0443\u0447\u0448\u0435\u0435 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u043e\u0435 (FLAC / MP3)", None))
        self.comboBoxQuality.setItemText(1, QCoreApplication.translate("MainWindow", u"MP3 320 kbps", None))
        self.comboBoxQuality.setItemText(2, QCoreApplication.translate("MainWindow", u"MP3 256 kbps", None))
        self.comboBoxQuality.setItemText(3, QCoreApplication.translate("MainWindow", u"MP3 192 kbps", None))
        self.comboBoxQuality.setItemText(4, QCoreApplication.translate("MainWindow", u"AAC 192 kbps", None))
        self.comboBoxQuality.setItemText(5, QCoreApplication.translate("MainWindow", u"AAC 64 kbps", None))

        self.comboBoxQuality.setCurrentText(QCoreApplication.translate("MainWindow", u"\u041b\u0443\u0447\u0448\u0435\u0435 \u0434\u043e\u0441\u0442\u0443\u043f\u043d\u043e\u0435 (FLAC / MP3)", None))
        self.labelAuthorization.setText(QCoreApplication.translate("MainWindow", u"\u0410\u0432\u0442\u043e\u0440\u0438\u0437\u0430\u0446\u0438\u044f", None))
        self.pushButtonAuthorization.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043b\u0443\u0447\u0438\u0442\u044c \u0442\u043e\u043a\u0435\u043d", None))
        self.pushButtonDownload.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043a\u0430\u0447\u0430\u0442\u044c", None))
        self.labelLog.setText(QCoreApplication.translate("MainWindow", u"\u0416\u0443\u0440\u043d\u0430\u043b", None))
    # retranslateUi

