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
        SettingsDialog.resize(568, 356)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SettingsDialog.sizePolicy().hasHeightForWidth())
        SettingsDialog.setSizePolicy(sizePolicy)
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
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.checkBoxSkipExisting.sizePolicy().hasHeightForWidth())
        self.checkBoxSkipExisting.setSizePolicy(sizePolicy2)
        self.checkBoxSkipExisting.setFont(font)
        self.checkBoxSkipExisting.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        self.checkBoxSkipExisting.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.checkBoxSkipExisting.setChecked(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.checkBoxSkipExisting)

        self.comboBoxCoverMode = QComboBox(SettingsDialog)
        self.comboBoxCoverMode.addItem("")
        self.comboBoxCoverMode.addItem("")
        self.comboBoxCoverMode.setObjectName(u"comboBoxCoverMode")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.comboBoxCoverMode.sizePolicy().hasHeightForWidth())
        self.comboBoxCoverMode.setSizePolicy(sizePolicy3)
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
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.spinBoxCoverResolution.sizePolicy().hasHeightForWidth())
        self.spinBoxCoverResolution.setSizePolicy(sizePolicy4)
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
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.lineEditPathPattern.sizePolicy().hasHeightForWidth())
        self.lineEditPathPattern.setSizePolicy(sizePolicy5)
        self.lineEditPathPattern.setFont(font)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEditPathPattern)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout.setItem(4, QFormLayout.ItemRole.LabelRole, self.verticalSpacer)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout.setItem(5, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

        self.formLayout.setItem(6, QFormLayout.ItemRole.LabelRole, self.verticalSpacer_3)

        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        sizePolicy2.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy2)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.formLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.buttonBox)


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
    # retranslateUi

