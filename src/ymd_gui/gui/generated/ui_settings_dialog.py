# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QFormLayout, QLabel,
    QLineEdit, QSizePolicy, QSpacerItem, QSpinBox,
    QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.resize(603, 356)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SettingsDialog.sizePolicy().hasHeightForWidth())
        SettingsDialog.setSizePolicy(sizePolicy)
        SettingsDialog.setStyleSheet(u"QDialog {\n"
"    background-color: #0B0B0B;\n"
"    color: #F2F2F2;\n"
"}\n"
"\n"
"\n"
"/* \u041f\u043e\u0434\u043f\u0438\u0441\u0438 */\n"
"\n"
"QLabel,\n"
"QCheckBox {\n"
"    color: #EDEDED;\n"
"    background: transparent;\n"
"\n"
"    spacing: 8px;\n"
"\n"
"    min-height: 28px;\n"
"    padding-top: 2px;\n"
"    padding-bottom: 2px;\n"
"}\n"
"\n"
"QCheckBox::indicator {\n"
"    width: 18px;\n"
"    height: 18px;\n"
"}\n"
"\n"
"\n"
"/* \u041f\u043e\u043b\u044f */\n"
"\n"
"QLineEdit,\n"
"QComboBox,\n"
"QSpinBox {\n"
"    color: #F2F2F2;\n"
"\n"
"    background-color: #222222;\n"
"\n"
"    border: 1px solid #3A3A3A;\n"
"    border-radius: 9px;\n"
"\n"
"    padding: 7px 10px;\n"
"\n"
"    selection-background-color: #FFCC00;\n"
"    selection-color: #111111;\n"
"}\n"
"\n"
"\n"
"QLineEdit:hover,\n"
"QComboBox:hover,\n"
"QSpinBox:hover {\n"
"    background-color: #282828;\n"
"    border: 1px solid #555555;\n"
"}\n"
"\n"
"\n"
"QLineEdit:focus,\n"
"QComboBox:focus,\n"
"QSpinBox:focus {\n"
"    border: 1px solid "
                        "#FFCC00;\n"
"}\n"
"\n"
"\n"
"/* ComboBox */\n"
"\n"
"QComboBox {\n"
"    padding-right: 32px;\n"
"}\n"
"\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"\n"
"    width: 30px;\n"
"\n"
"    background: transparent;\n"
"\n"
"    border: none;\n"
"    border-left: 1px solid rgba(255, 255, 255, 25);\n"
"\n"
"    border-top-right-radius: 9px;\n"
"    border-bottom-right-radius: 9px;\n"
"}\n"
"\n"
"QComboBox::drop-down:hover {\n"
"    background-color: rgba(255, 255, 255, 20);\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: url(:/icons/spin_down.svg);\n"
"\n"
"    width: 10px;\n"
"    height: 6px;\n"
"}\n"
"\n"
"QComboBox::down-arrow:on {\n"
"    top: 1px;\n"
"}\n"
"\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    color: #F2F2F2;\n"
"\n"
"    background-color: #1B1B1B;\n"
"\n"
"    border: 1px solid #3A3A3A;\n"
"\n"
"    selection-background-color: #FFCC00;\n"
"    selection-color: #111111;\n"
"}\n"
"\n"
"\n"
"/* SpinBox */\n"
"\n"
"QSpinBox {\n"
"    pa"
                        "dding-right: 28px;\n"
"}\n"
"\n"
"QSpinBox::up-button {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: top right;\n"
"\n"
"    width: 26px;\n"
"\n"
"    background: transparent;\n"
"\n"
"    border: none;\n"
"    border-left: 1px solid #3A3A3A;\n"
"\n"
"    border-top-right-radius: 8px;\n"
"}\n"
"\n"
"QSpinBox::down-button {\n"
"    subcontrol-origin: border;\n"
"    subcontrol-position: bottom right;\n"
"\n"
"    width: 26px;\n"
"\n"
"    background: transparent;\n"
"\n"
"    border: none;\n"
"    border-left: 1px solid #3A3A3A;\n"
"\n"
"    border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"QSpinBox::up-button:hover,\n"
"QSpinBox::down-button:hover {\n"
"    background-color: #333333;\n"
"}\n"
"\n"
"QSpinBox::up-arrow {\n"
"    image: url(:/icons/spin_up.svg);\n"
"    width: 10px;\n"
"    height: 6px;\n"
"}\n"
"\n"
"QSpinBox::down-arrow {\n"
"    image: url(:/icons/spin_down.svg);\n"
"    width: 10px;\n"
"    height: 6px;\n"
"}\n"
"\n"
"\n"
"/* \u041a\u043d\u043e\u043f\u043a\u0438 */\n"
"\n"
"Q"
                        "DialogButtonBox QPushButton {\n"
"    color: #111111;\n"
"\n"
"    background-color: #FFCC00;\n"
"\n"
"    border: none;\n"
"    border-radius: 9px;\n"
"\n"
"    min-width: 80px;\n"
"\n"
"    padding: 7px 16px;\n"
"\n"
"    font-weight: 600;\n"
"}\n"
"\n"
"\n"
"QDialogButtonBox QPushButton:hover {\n"
"    background-color: #FFDA33;\n"
"}\n"
"\n"
"\n"
"QDialogButtonBox QPushButton:pressed {\n"
"    background-color: #E7B900;\n"
"}")
        self.formLayout_2 = QFormLayout(SettingsDialog)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.labelSkipExisting = QLabel(SettingsDialog)
        self.labelSkipExisting.setObjectName(u"labelSkipExisting")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.labelSkipExisting.sizePolicy().hasHeightForWidth())
        self.labelSkipExisting.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setPointSize(16)
        self.labelSkipExisting.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelSkipExisting)

        self.checkBoxSkipExisting = QCheckBox(SettingsDialog)
        self.checkBoxSkipExisting.setObjectName(u"checkBoxSkipExisting")
        sizePolicy.setHeightForWidth(self.checkBoxSkipExisting.sizePolicy().hasHeightForWidth())
        self.checkBoxSkipExisting.setSizePolicy(sizePolicy)
        self.checkBoxSkipExisting.setMinimumSize(QSize(0, 32))
        self.checkBoxSkipExisting.setFont(font)
        self.checkBoxSkipExisting.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.checkBoxSkipExisting.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBoxSkipExisting.setChecked(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.checkBoxSkipExisting)

        self.comboBoxCoverMode = QComboBox(SettingsDialog)
        self.comboBoxCoverMode.addItem("")
        self.comboBoxCoverMode.addItem("")
        self.comboBoxCoverMode.setObjectName(u"comboBoxCoverMode")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.comboBoxCoverMode.sizePolicy().hasHeightForWidth())
        self.comboBoxCoverMode.setSizePolicy(sizePolicy2)
        self.comboBoxCoverMode.setFont(font)
        self.comboBoxCoverMode.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.comboBoxCoverMode.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContentsOnFirstShow)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboBoxCoverMode)

        self.labelCoverMode = QLabel(SettingsDialog)
        self.labelCoverMode.setObjectName(u"labelCoverMode")
        sizePolicy1.setHeightForWidth(self.labelCoverMode.sizePolicy().hasHeightForWidth())
        self.labelCoverMode.setSizePolicy(sizePolicy1)
        self.labelCoverMode.setFont(font)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelCoverMode)

        self.labelCoverResolution = QLabel(SettingsDialog)
        self.labelCoverResolution.setObjectName(u"labelCoverResolution")
        sizePolicy1.setHeightForWidth(self.labelCoverResolution.sizePolicy().hasHeightForWidth())
        self.labelCoverResolution.setSizePolicy(sizePolicy1)
        self.labelCoverResolution.setFont(font)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelCoverResolution)

        self.spinBoxCoverResolution = QSpinBox(SettingsDialog)
        self.spinBoxCoverResolution.setObjectName(u"spinBoxCoverResolution")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.spinBoxCoverResolution.sizePolicy().hasHeightForWidth())
        self.spinBoxCoverResolution.setSizePolicy(sizePolicy3)
        self.spinBoxCoverResolution.setFont(font)
        self.spinBoxCoverResolution.setInputMethodHints(Qt.InputMethodHint.ImhDigitsOnly|Qt.InputMethodHint.ImhLatinOnly)
        self.spinBoxCoverResolution.setAccelerated(False)
        self.spinBoxCoverResolution.setMinimum(100)
        self.spinBoxCoverResolution.setMaximum(2000)
        self.spinBoxCoverResolution.setValue(400)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinBoxCoverResolution)

        self.labelPathPattern = QLabel(SettingsDialog)
        self.labelPathPattern.setObjectName(u"labelPathPattern")
        sizePolicy1.setHeightForWidth(self.labelPathPattern.sizePolicy().hasHeightForWidth())
        self.labelPathPattern.setSizePolicy(sizePolicy1)
        self.labelPathPattern.setFont(font)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelPathPattern)

        self.lineEditPathPattern = QLineEdit(SettingsDialog)
        self.lineEditPathPattern.setObjectName(u"lineEditPathPattern")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.lineEditPathPattern.sizePolicy().hasHeightForWidth())
        self.lineEditPathPattern.setSizePolicy(sizePolicy4)
        self.lineEditPathPattern.setFont(font)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEditPathPattern)

        self.labelParallelDownloads = QLabel(SettingsDialog)
        self.labelParallelDownloads.setObjectName(u"labelParallelDownloads")
        sizePolicy1.setHeightForWidth(self.labelParallelDownloads.sizePolicy().hasHeightForWidth())
        self.labelParallelDownloads.setSizePolicy(sizePolicy1)
        self.labelParallelDownloads.setFont(font)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelParallelDownloads)

        self.spinBoxParallelDownloads = QSpinBox(SettingsDialog)
        self.spinBoxParallelDownloads.setObjectName(u"spinBoxParallelDownloads")
        sizePolicy3.setHeightForWidth(self.spinBoxParallelDownloads.sizePolicy().hasHeightForWidth())
        self.spinBoxParallelDownloads.setSizePolicy(sizePolicy3)
        self.spinBoxParallelDownloads.setFont(font)
        self.spinBoxParallelDownloads.setMinimum(1)
        self.spinBoxParallelDownloads.setMaximum(8)
        self.spinBoxParallelDownloads.setValue(3)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinBoxParallelDownloads)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout.setItem(5, QFormLayout.ItemRole.LabelRole, self.verticalSpacer)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout.setItem(6, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.formLayout.setItem(7, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_3)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy5)
        self.buttonBox.setFont(font)
        self.buttonBox.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.buttonBox.setMouseTracking(False)
        self.buttonBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setCenterButtons(False)

        self.formLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.buttonBox)


        self.formLayout_2.setLayout(0, QFormLayout.ItemRole.SpanningRole, self.formLayout)


        self.retranslateUi(SettingsDialog)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"\u041d\u0430\u0441\u0442\u0440\u043e\u0439\u043a\u0438", None))
        self.labelSkipExisting.setText(QCoreApplication.translate("SettingsDialog", u"\u041f\u0440\u043e\u043f\u0443\u0441\u043a\u0430\u0442\u044c \u0441\u043a\u0430\u0447\u0430\u043d\u043d\u044b\u0435", None))
        self.checkBoxSkipExisting.setText("")
        self.comboBoxCoverMode.setItemText(0, QCoreApplication.translate("SettingsDialog", u"\u0412\u0441\u0442\u0440\u0430\u0438\u0432\u0430\u0442\u044c \u0432 \u0430\u0443\u0434\u0438\u043e\u0444\u0430\u0439\u043b", None))
        self.comboBoxCoverMode.setItemText(1, QCoreApplication.translate("SettingsDialog", u"\u0421\u043e\u0445\u0440\u0430\u043d\u044f\u0442\u044c \u043e\u0442\u0434\u0435\u043b\u044c\u043d\u044b\u043c \u0444\u0430\u0439\u043b\u043e\u043c", None))

        self.labelCoverMode.setText(QCoreApplication.translate("SettingsDialog", u"\u041e\u0431\u043b\u043e\u0436\u043a\u0430", None))
        self.labelCoverResolution.setText(QCoreApplication.translate("SettingsDialog", u"\u0420\u0430\u0437\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043e\u0431\u043b\u043e\u0436\u043a\u0438", None))
        self.spinBoxCoverResolution.setSpecialValueText("")
        self.spinBoxCoverResolution.setSuffix(QCoreApplication.translate("SettingsDialog", u" px", None))
        self.labelPathPattern.setText(QCoreApplication.translate("SettingsDialog", u"\u0428\u0430\u0431\u043b\u043e\u043d \u0438\u043c\u0435\u043d\u0438", None))
#if QT_CONFIG(tooltip)
        self.lineEditPathPattern.setToolTip(QCoreApplication.translate("SettingsDialog", u"<html><head/><body><p>#number-padded</p><p>#album-artist</p><p>#track-artist</p><p>#artist-id</p><p>#album-id</p><p>#track-id</p><p>#number</p><p>#title</p><p>#album</p><p>#year</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.lineEditPathPattern.setText(QCoreApplication.translate("SettingsDialog", u"#album-artist - #title #track-id", None))
        self.labelParallelDownloads.setText(QCoreApplication.translate("SettingsDialog", u"\u041f\u0430\u0440\u0430\u043b\u043b\u0435\u043b\u044c\u043d\u044b\u0435 \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0438", None))
    # retranslateUi

