# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'layout_romsearch.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QButtonGroup, QCheckBox,
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMenu, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QSpacerItem, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget)

class Ui_RomSearch(object):
    def setupUi(self, RomSearch):
        if not RomSearch.objectName():
            RomSearch.setObjectName(u"RomSearch")
        RomSearch.resize(950, 785)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(RomSearch.sizePolicy().hasHeightForWidth())
        RomSearch.setSizePolicy(sizePolicy)
        RomSearch.setMinimumSize(QSize(950, 785))
        self.actionLoadConfigFile = QAction(RomSearch)
        self.actionLoadConfigFile.setObjectName(u"actionLoadConfigFile")
        self.actionExit = QAction(RomSearch)
        self.actionExit.setObjectName(u"actionExit")
        self.actionDocumentation = QAction(RomSearch)
        self.actionDocumentation.setObjectName(u"actionDocumentation")
        self.actionIssues = QAction(RomSearch)
        self.actionIssues.setObjectName(u"actionIssues")
        self.actionAbout = QAction(RomSearch)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionNewConfigFile = QAction(RomSearch)
        self.actionNewConfigFile.setObjectName(u"actionNewConfigFile")
        self.actionSaveConfigFile = QAction(RomSearch)
        self.actionSaveConfigFile.setObjectName(u"actionSaveConfigFile")
        self.centralwidget = QWidget(RomSearch)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setEnabled(True)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidgetModules = QTabWidget(self.centralwidget)
        self.tabWidgetModules.setObjectName(u"tabWidgetModules")
        self.tabConfig = QWidget()
        self.tabConfig.setObjectName(u"tabConfig")
        self.verticalLayout_2 = QVBoxLayout(self.tabConfig)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.tabWidgetConfig = QTabWidget(self.tabConfig)
        self.tabWidgetConfig.setObjectName(u"tabWidgetConfig")
        self.tabWidgetConfig.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidgetConfig.setTabsClosable(False)
        self.tabWidgetConfig.setTabBarAutoHide(False)
        self.tabConfigMain = QWidget()
        self.tabConfigMain.setObjectName(u"tabConfigMain")
        self.horizontalLayout = QHBoxLayout(self.tabConfigMain)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayoutConfigMain = QGridLayout()
        self.gridLayoutConfigMain.setObjectName(u"gridLayoutConfigMain")
        self.lineSepConfigDirsModules = QFrame(self.tabConfigMain)
        self.lineSepConfigDirsModules.setObjectName(u"lineSepConfigDirsModules")
        self.lineSepConfigDirsModules.setFrameShadow(QFrame.Shadow.Plain)
        self.lineSepConfigDirsModules.setFrameShape(QFrame.Shape.VLine)

        self.gridLayoutConfigMain.addWidget(self.lineSepConfigDirsModules, 0, 1, 1, 1)

        self.horizontalLayoutConfigRomsearchDirs = QHBoxLayout()
        self.horizontalLayoutConfigRomsearchDirs.setObjectName(u"horizontalLayoutConfigRomsearchDirs")
        self.verticalLayoutConfigRomsearchDirs = QVBoxLayout()
        self.verticalLayoutConfigRomsearchDirs.setObjectName(u"verticalLayoutConfigRomsearchDirs")
        self.labelConfigRomsearchDirsTitle = QLabel(self.tabConfigMain)
        self.labelConfigRomsearchDirsTitle.setObjectName(u"labelConfigRomsearchDirsTitle")
        font = QFont()
        font.setBold(True)
        self.labelConfigRomsearchDirsTitle.setFont(font)
        self.labelConfigRomsearchDirsTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigRomsearchDirsTitle)

        self.lineConfigRomsearchDirs = QFrame(self.tabConfigMain)
        self.lineConfigRomsearchDirs.setObjectName(u"lineConfigRomsearchDirs")
        self.lineConfigRomsearchDirs.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomsearchDirs.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.lineConfigRomsearchDirs)

        self.labelConfigRomsearchDirsDescription = QLabel(self.tabConfigMain)
        self.labelConfigRomsearchDirsDescription.setObjectName(u"labelConfigRomsearchDirsDescription")
        self.labelConfigRomsearchDirsDescription.setWordWrap(True)

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigRomsearchDirsDescription)

        self.verticalSpacerConfigRomsearchDirsUpper = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomsearchDirs.addItem(self.verticalSpacerConfigRomsearchDirsUpper)

        self.labelConfigConfigFile = QLabel(self.tabConfigMain)
        self.labelConfigConfigFile.setObjectName(u"labelConfigConfigFile")

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigConfigFile)

        self.lineEditConfigConfigFile = QLineEdit(self.tabConfigMain)
        self.lineEditConfigConfigFile.setObjectName(u"lineEditConfigConfigFile")
        self.lineEditConfigConfigFile.setReadOnly(True)

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.lineEditConfigConfigFile)

        self.labelConfigRawDir = QLabel(self.tabConfigMain)
        self.labelConfigRawDir.setObjectName(u"labelConfigRawDir")

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigRawDir)

        self.horizontalLayoutConfigRawDir = QHBoxLayout()
        self.horizontalLayoutConfigRawDir.setObjectName(u"horizontalLayoutConfigRawDir")
        self.lineEditConfigRawDir = QLineEdit(self.tabConfigMain)
        self.lineEditConfigRawDir.setObjectName(u"lineEditConfigRawDir")

        self.horizontalLayoutConfigRawDir.addWidget(self.lineEditConfigRawDir)

        self.pushButtonConfigRawDir = QPushButton(self.tabConfigMain)
        self.pushButtonConfigRawDir.setObjectName(u"pushButtonConfigRawDir")
        self.pushButtonConfigRawDir.setFlat(False)

        self.horizontalLayoutConfigRawDir.addWidget(self.pushButtonConfigRawDir)


        self.verticalLayoutConfigRomsearchDirs.addLayout(self.horizontalLayoutConfigRawDir)

        self.labelConfigRomDir = QLabel(self.tabConfigMain)
        self.labelConfigRomDir.setObjectName(u"labelConfigRomDir")

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigRomDir)

        self.horizontalLayoutConfigRomDir = QHBoxLayout()
        self.horizontalLayoutConfigRomDir.setObjectName(u"horizontalLayoutConfigRomDir")
        self.lineEditConfigRomDir = QLineEdit(self.tabConfigMain)
        self.lineEditConfigRomDir.setObjectName(u"lineEditConfigRomDir")

        self.horizontalLayoutConfigRomDir.addWidget(self.lineEditConfigRomDir)

        self.pushButtonConfigRomDir = QPushButton(self.tabConfigMain)
        self.pushButtonConfigRomDir.setObjectName(u"pushButtonConfigRomDir")
        self.pushButtonConfigRomDir.setFlat(False)

        self.horizontalLayoutConfigRomDir.addWidget(self.pushButtonConfigRomDir)


        self.verticalLayoutConfigRomsearchDirs.addLayout(self.horizontalLayoutConfigRomDir)

        self.labelConfigDatDir = QLabel(self.tabConfigMain)
        self.labelConfigDatDir.setObjectName(u"labelConfigDatDir")

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigDatDir)

        self.horizontalLayoutConfigDatDir = QHBoxLayout()
        self.horizontalLayoutConfigDatDir.setObjectName(u"horizontalLayoutConfigDatDir")
        self.lineEditConfigDatDir = QLineEdit(self.tabConfigMain)
        self.lineEditConfigDatDir.setObjectName(u"lineEditConfigDatDir")

        self.horizontalLayoutConfigDatDir.addWidget(self.lineEditConfigDatDir)

        self.pushButtonConfigDatDir = QPushButton(self.tabConfigMain)
        self.pushButtonConfigDatDir.setObjectName(u"pushButtonConfigDatDir")
        self.pushButtonConfigDatDir.setFlat(False)

        self.horizontalLayoutConfigDatDir.addWidget(self.pushButtonConfigDatDir)


        self.verticalLayoutConfigRomsearchDirs.addLayout(self.horizontalLayoutConfigDatDir)

        self.labelConfigParsedDatDir = QLabel(self.tabConfigMain)
        self.labelConfigParsedDatDir.setObjectName(u"labelConfigParsedDatDir")

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigParsedDatDir)

        self.horizontalLayoutConfigParsedDatDir = QHBoxLayout()
        self.horizontalLayoutConfigParsedDatDir.setObjectName(u"horizontalLayoutConfigParsedDatDir")
        self.lineEditConfigParsedDatDir = QLineEdit(self.tabConfigMain)
        self.lineEditConfigParsedDatDir.setObjectName(u"lineEditConfigParsedDatDir")

        self.horizontalLayoutConfigParsedDatDir.addWidget(self.lineEditConfigParsedDatDir)

        self.pushButtonConfigParsedDatDir = QPushButton(self.tabConfigMain)
        self.pushButtonConfigParsedDatDir.setObjectName(u"pushButtonConfigParsedDatDir")
        self.pushButtonConfigParsedDatDir.setFlat(False)

        self.horizontalLayoutConfigParsedDatDir.addWidget(self.pushButtonConfigParsedDatDir)


        self.verticalLayoutConfigRomsearchDirs.addLayout(self.horizontalLayoutConfigParsedDatDir)

        self.labelConfigDupeDir = QLabel(self.tabConfigMain)
        self.labelConfigDupeDir.setObjectName(u"labelConfigDupeDir")

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigDupeDir)

        self.horizontalLayoutConfigDupeDir = QHBoxLayout()
        self.horizontalLayoutConfigDupeDir.setObjectName(u"horizontalLayoutConfigDupeDir")
        self.lineEditConfigDupeDir = QLineEdit(self.tabConfigMain)
        self.lineEditConfigDupeDir.setObjectName(u"lineEditConfigDupeDir")

        self.horizontalLayoutConfigDupeDir.addWidget(self.lineEditConfigDupeDir)

        self.pushButtonConfigDupeDir = QPushButton(self.tabConfigMain)
        self.pushButtonConfigDupeDir.setObjectName(u"pushButtonConfigDupeDir")
        self.pushButtonConfigDupeDir.setFlat(False)

        self.horizontalLayoutConfigDupeDir.addWidget(self.pushButtonConfigDupeDir)


        self.verticalLayoutConfigRomsearchDirs.addLayout(self.horizontalLayoutConfigDupeDir)

        self.labelConfigCacheDir = QLabel(self.tabConfigMain)
        self.labelConfigCacheDir.setObjectName(u"labelConfigCacheDir")

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigCacheDir)

        self.horizontalLayoutConfigCacheDir = QHBoxLayout()
        self.horizontalLayoutConfigCacheDir.setObjectName(u"horizontalLayoutConfigCacheDir")
        self.lineEditConfigCacheDir = QLineEdit(self.tabConfigMain)
        self.lineEditConfigCacheDir.setObjectName(u"lineEditConfigCacheDir")

        self.horizontalLayoutConfigCacheDir.addWidget(self.lineEditConfigCacheDir)

        self.pushButtonConfigCacheDir = QPushButton(self.tabConfigMain)
        self.pushButtonConfigCacheDir.setObjectName(u"pushButtonConfigCacheDir")
        self.pushButtonConfigCacheDir.setFlat(False)

        self.horizontalLayoutConfigCacheDir.addWidget(self.pushButtonConfigCacheDir)


        self.verticalLayoutConfigRomsearchDirs.addLayout(self.horizontalLayoutConfigCacheDir)

        self.labelConfigLogDir = QLabel(self.tabConfigMain)
        self.labelConfigLogDir.setObjectName(u"labelConfigLogDir")

        self.verticalLayoutConfigRomsearchDirs.addWidget(self.labelConfigLogDir)

        self.horizontalLayoutConfigLogDir = QHBoxLayout()
        self.horizontalLayoutConfigLogDir.setObjectName(u"horizontalLayoutConfigLogDir")
        self.lineEditConfigLogDir = QLineEdit(self.tabConfigMain)
        self.lineEditConfigLogDir.setObjectName(u"lineEditConfigLogDir")

        self.horizontalLayoutConfigLogDir.addWidget(self.lineEditConfigLogDir)

        self.pushButtonConfigLogDir = QPushButton(self.tabConfigMain)
        self.pushButtonConfigLogDir.setObjectName(u"pushButtonConfigLogDir")
        self.pushButtonConfigLogDir.setFlat(False)

        self.horizontalLayoutConfigLogDir.addWidget(self.pushButtonConfigLogDir)


        self.verticalLayoutConfigRomsearchDirs.addLayout(self.horizontalLayoutConfigLogDir)

        self.verticalSpacerConfigRomsearchDirsLower = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomsearchDirs.addItem(self.verticalSpacerConfigRomsearchDirsLower)


        self.horizontalLayoutConfigRomsearchDirs.addLayout(self.verticalLayoutConfigRomsearchDirs)


        self.gridLayoutConfigMain.addLayout(self.horizontalLayoutConfigRomsearchDirs, 0, 0, 1, 1)

        self.horizontalLayoutConfigRomsearchModules = QHBoxLayout()
        self.horizontalLayoutConfigRomsearchModules.setObjectName(u"horizontalLayoutConfigRomsearchModules")
        self.verticalLayoutConfigRomsearchModules = QVBoxLayout()
        self.verticalLayoutConfigRomsearchModules.setObjectName(u"verticalLayoutConfigRomsearchModules")
        self.labelConfigRomsearchModulesTitle = QLabel(self.tabConfigMain)
        self.labelConfigRomsearchModulesTitle.setObjectName(u"labelConfigRomsearchModulesTitle")
        self.labelConfigRomsearchModulesTitle.setFont(font)
        self.labelConfigRomsearchModulesTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.labelConfigRomsearchModulesTitle)

        self.lineConfigRomsearchModules = QFrame(self.tabConfigMain)
        self.lineConfigRomsearchModules.setObjectName(u"lineConfigRomsearchModules")
        self.lineConfigRomsearchModules.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomsearchModules.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.lineConfigRomsearchModules)

        self.labelConfigRomsearchModulesDescription = QLabel(self.tabConfigMain)
        self.labelConfigRomsearchModulesDescription.setObjectName(u"labelConfigRomsearchModulesDescription")
        self.labelConfigRomsearchModulesDescription.setWordWrap(True)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.labelConfigRomsearchModulesDescription)

        self.verticalSpacerConfigRomsearchModulesUpper = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomsearchModules.addItem(self.verticalSpacerConfigRomsearchModulesUpper)

        self.checkBoxConfigRunRomDownloader = QCheckBox(self.tabConfigMain)
        self.checkBoxConfigRunRomDownloader.setObjectName(u"checkBoxConfigRunRomDownloader")
        self.checkBoxConfigRunRomDownloader.setChecked(True)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.checkBoxConfigRunRomDownloader)

        self.checkBoxConfigRunDatParser = QCheckBox(self.tabConfigMain)
        self.checkBoxConfigRunDatParser.setObjectName(u"checkBoxConfigRunDatParser")
        self.checkBoxConfigRunDatParser.setChecked(True)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.checkBoxConfigRunDatParser)

        self.checkBoxConfigRunDupeParser = QCheckBox(self.tabConfigMain)
        self.checkBoxConfigRunDupeParser.setObjectName(u"checkBoxConfigRunDupeParser")
        self.checkBoxConfigRunDupeParser.setChecked(True)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.checkBoxConfigRunDupeParser)

        self.checkBoxConfigRunRomChooser = QCheckBox(self.tabConfigMain)
        self.checkBoxConfigRunRomChooser.setObjectName(u"checkBoxConfigRunRomChooser")
        self.checkBoxConfigRunRomChooser.setChecked(True)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.checkBoxConfigRunRomChooser)

        self.checkBoxConfigRunRomMover = QCheckBox(self.tabConfigMain)
        self.checkBoxConfigRunRomMover.setObjectName(u"checkBoxConfigRunRomMover")
        self.checkBoxConfigRunRomMover.setChecked(True)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.checkBoxConfigRunRomMover)

        self.verticalSpacerConfigRomsearchModulesMiddle = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomsearchModules.addItem(self.verticalSpacerConfigRomsearchModulesMiddle)

        self.checkBoxConfigDryRun = QCheckBox(self.tabConfigMain)
        self.checkBoxConfigDryRun.setObjectName(u"checkBoxConfigDryRun")

        self.verticalLayoutConfigRomsearchModules.addWidget(self.checkBoxConfigDryRun)

        self.verticalSpacerConfigRomsearchModulesLower = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomsearchModules.addItem(self.verticalSpacerConfigRomsearchModulesLower)

        self.labelConfigRomsearchMethodTitle = QLabel(self.tabConfigMain)
        self.labelConfigRomsearchMethodTitle.setObjectName(u"labelConfigRomsearchMethodTitle")
        self.labelConfigRomsearchMethodTitle.setFont(font)
        self.labelConfigRomsearchMethodTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.labelConfigRomsearchMethodTitle)

        self.lineConfigRomsearchMethod = QFrame(self.tabConfigMain)
        self.lineConfigRomsearchMethod.setObjectName(u"lineConfigRomsearchMethod")
        self.lineConfigRomsearchMethod.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomsearchMethod.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.lineConfigRomsearchMethod)

        self.labelConfigRomsearchMethodDescription = QLabel(self.tabConfigMain)
        self.labelConfigRomsearchMethodDescription.setObjectName(u"labelConfigRomsearchMethodDescription")
        self.labelConfigRomsearchMethodDescription.setWordWrap(True)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.labelConfigRomsearchMethodDescription)

        self.verticalSpacerConfigRomsearchMethodUpper = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomsearchModules.addItem(self.verticalSpacerConfigRomsearchMethodUpper)

        self.radioButtonConfigRomsearchMethodFilterDownload = QRadioButton(self.tabConfigMain)
        self.radioButtonConfigRomsearchMethod = QButtonGroup(RomSearch)
        self.radioButtonConfigRomsearchMethod.setObjectName(u"radioButtonConfigRomsearchMethod")
        self.radioButtonConfigRomsearchMethod.addButton(self.radioButtonConfigRomsearchMethodFilterDownload)
        self.radioButtonConfigRomsearchMethodFilterDownload.setObjectName(u"radioButtonConfigRomsearchMethodFilterDownload")
        self.radioButtonConfigRomsearchMethodFilterDownload.setChecked(True)

        self.verticalLayoutConfigRomsearchModules.addWidget(self.radioButtonConfigRomsearchMethodFilterDownload)

        self.radioButtonConfigRomsearchMethodDownloadFilter = QRadioButton(self.tabConfigMain)
        self.radioButtonConfigRomsearchMethod.addButton(self.radioButtonConfigRomsearchMethodDownloadFilter)
        self.radioButtonConfigRomsearchMethodDownloadFilter.setObjectName(u"radioButtonConfigRomsearchMethodDownloadFilter")

        self.verticalLayoutConfigRomsearchModules.addWidget(self.radioButtonConfigRomsearchMethodDownloadFilter)

        self.verticalSpacerConfigRomsearchMethodLower = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomsearchModules.addItem(self.verticalSpacerConfigRomsearchMethodLower)


        self.horizontalLayoutConfigRomsearchModules.addLayout(self.verticalLayoutConfigRomsearchModules)


        self.gridLayoutConfigMain.addLayout(self.horizontalLayoutConfigRomsearchModules, 0, 2, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayoutConfigMain)

        self.tabWidgetConfig.addTab(self.tabConfigMain, "")
        self.tabConfigPlatforms = QWidget()
        self.tabConfigPlatforms.setObjectName(u"tabConfigPlatforms")
        self.horizontalLayout_2 = QHBoxLayout(self.tabConfigPlatforms)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.gridLayoutConfigPlatforms = QGridLayout()
        self.gridLayoutConfigPlatforms.setObjectName(u"gridLayoutConfigPlatforms")
        self.horizontalLayoutConfigPlatforms = QHBoxLayout()
        self.horizontalLayoutConfigPlatforms.setObjectName(u"horizontalLayoutConfigPlatforms")
        self.listWidgetConfigPlatforms = QListWidget(self.tabConfigPlatforms)
        self.listWidgetConfigPlatforms.setObjectName(u"listWidgetConfigPlatforms")
        self.listWidgetConfigPlatforms.setFrameShape(QFrame.Shape.WinPanel)
        self.listWidgetConfigPlatforms.setFrameShadow(QFrame.Shadow.Plain)
        self.listWidgetConfigPlatforms.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self.horizontalLayoutConfigPlatforms.addWidget(self.listWidgetConfigPlatforms)

        self.lineConfigPlatforms = QFrame(self.tabConfigPlatforms)
        self.lineConfigPlatforms.setObjectName(u"lineConfigPlatforms")
        self.lineConfigPlatforms.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigPlatforms.setFrameShape(QFrame.Shape.VLine)

        self.horizontalLayoutConfigPlatforms.addWidget(self.lineConfigPlatforms)

        self.verticalLayoutConfigPlatformsDescription = QVBoxLayout()
        self.verticalLayoutConfigPlatformsDescription.setObjectName(u"verticalLayoutConfigPlatformsDescription")
        self.labelConfigPlatformsDescriptionTitle = QLabel(self.tabConfigPlatforms)
        self.labelConfigPlatformsDescriptionTitle.setObjectName(u"labelConfigPlatformsDescriptionTitle")
        self.labelConfigPlatformsDescriptionTitle.setFont(font)

        self.verticalLayoutConfigPlatformsDescription.addWidget(self.labelConfigPlatformsDescriptionTitle)

        self.lineConfigPlatformsDescription = QFrame(self.tabConfigPlatforms)
        self.lineConfigPlatformsDescription.setObjectName(u"lineConfigPlatformsDescription")
        self.lineConfigPlatformsDescription.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigPlatformsDescription.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigPlatformsDescription.addWidget(self.lineConfigPlatformsDescription)

        self.labelConfigPlatformsDescriptionBody = QLabel(self.tabConfigPlatforms)
        self.labelConfigPlatformsDescriptionBody.setObjectName(u"labelConfigPlatformsDescriptionBody")
        self.labelConfigPlatformsDescriptionBody.setWordWrap(True)

        self.verticalLayoutConfigPlatformsDescription.addWidget(self.labelConfigPlatformsDescriptionBody)

        self.verticalSpacerConfigPlatformsDescription = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigPlatformsDescription.addItem(self.verticalSpacerConfigPlatformsDescription)


        self.horizontalLayoutConfigPlatforms.addLayout(self.verticalLayoutConfigPlatformsDescription)


        self.gridLayoutConfigPlatforms.addLayout(self.horizontalLayoutConfigPlatforms, 0, 0, 1, 1)


        self.horizontalLayout_2.addLayout(self.gridLayoutConfigPlatforms)

        self.tabWidgetConfig.addTab(self.tabConfigPlatforms, "")
        self.tabConfigRegionsLanguages = QWidget()
        self.tabConfigRegionsLanguages.setObjectName(u"tabConfigRegionsLanguages")
        self.horizontalLayout_3 = QHBoxLayout(self.tabConfigRegionsLanguages)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.gridLayoutConfigRegionsLanguages = QGridLayout()
        self.gridLayoutConfigRegionsLanguages.setObjectName(u"gridLayoutConfigRegionsLanguages")
        self.horizontalLayoutConfigRegionsLanguages = QHBoxLayout()
        self.horizontalLayoutConfigRegionsLanguages.setObjectName(u"horizontalLayoutConfigRegionsLanguages")
        self.verticalLayoutConfigRegionsLanguagesRegions = QVBoxLayout()
        self.verticalLayoutConfigRegionsLanguagesRegions.setObjectName(u"verticalLayoutConfigRegionsLanguagesRegions")
        self.labelConfigRegionsLanguagesRegionsTitle = QLabel(self.tabConfigRegionsLanguages)
        self.labelConfigRegionsLanguagesRegionsTitle.setObjectName(u"labelConfigRegionsLanguagesRegionsTitle")
        self.labelConfigRegionsLanguagesRegionsTitle.setFont(font)
        self.labelConfigRegionsLanguagesRegionsTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutConfigRegionsLanguagesRegions.addWidget(self.labelConfigRegionsLanguagesRegionsTitle)

        self.ConfigRegionsLanguagesRegionsTitleDivider = QFrame(self.tabConfigRegionsLanguages)
        self.ConfigRegionsLanguagesRegionsTitleDivider.setObjectName(u"ConfigRegionsLanguagesRegionsTitleDivider")
        self.ConfigRegionsLanguagesRegionsTitleDivider.setFrameShadow(QFrame.Shadow.Plain)
        self.ConfigRegionsLanguagesRegionsTitleDivider.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRegionsLanguagesRegions.addWidget(self.ConfigRegionsLanguagesRegionsTitleDivider)

        self.labelConfigRegionsLanguagesRegionsDescription = QLabel(self.tabConfigRegionsLanguages)
        self.labelConfigRegionsLanguagesRegionsDescription.setObjectName(u"labelConfigRegionsLanguagesRegionsDescription")
        self.labelConfigRegionsLanguagesRegionsDescription.setWordWrap(True)

        self.verticalLayoutConfigRegionsLanguagesRegions.addWidget(self.labelConfigRegionsLanguagesRegionsDescription)

        self.lineConfigRegionsLanguagesRegionsDescriptionDivider = QFrame(self.tabConfigRegionsLanguages)
        self.lineConfigRegionsLanguagesRegionsDescriptionDivider.setObjectName(u"lineConfigRegionsLanguagesRegionsDescriptionDivider")
        self.lineConfigRegionsLanguagesRegionsDescriptionDivider.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRegionsLanguagesRegionsDescriptionDivider.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRegionsLanguagesRegions.addWidget(self.lineConfigRegionsLanguagesRegionsDescriptionDivider)

        self.listWidgetConfigRegionsLanguagesRegions = QListWidget(self.tabConfigRegionsLanguages)
        self.listWidgetConfigRegionsLanguagesRegions.setObjectName(u"listWidgetConfigRegionsLanguagesRegions")
        self.listWidgetConfigRegionsLanguagesRegions.setFrameShape(QFrame.Shape.WinPanel)
        self.listWidgetConfigRegionsLanguagesRegions.setFrameShadow(QFrame.Shadow.Plain)
        self.listWidgetConfigRegionsLanguagesRegions.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self.verticalLayoutConfigRegionsLanguagesRegions.addWidget(self.listWidgetConfigRegionsLanguagesRegions)


        self.horizontalLayoutConfigRegionsLanguages.addLayout(self.verticalLayoutConfigRegionsLanguagesRegions)

        self.lineConfigRegionsLanguagesDivider = QFrame(self.tabConfigRegionsLanguages)
        self.lineConfigRegionsLanguagesDivider.setObjectName(u"lineConfigRegionsLanguagesDivider")
        self.lineConfigRegionsLanguagesDivider.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRegionsLanguagesDivider.setFrameShape(QFrame.Shape.VLine)

        self.horizontalLayoutConfigRegionsLanguages.addWidget(self.lineConfigRegionsLanguagesDivider)

        self.verticalLayoutConfigRegionsLanguagesLanguages = QVBoxLayout()
        self.verticalLayoutConfigRegionsLanguagesLanguages.setObjectName(u"verticalLayoutConfigRegionsLanguagesLanguages")
        self.labelConfigRegionsLanguagesLanguagesTitle = QLabel(self.tabConfigRegionsLanguages)
        self.labelConfigRegionsLanguagesLanguagesTitle.setObjectName(u"labelConfigRegionsLanguagesLanguagesTitle")
        self.labelConfigRegionsLanguagesLanguagesTitle.setFont(font)
        self.labelConfigRegionsLanguagesLanguagesTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutConfigRegionsLanguagesLanguages.addWidget(self.labelConfigRegionsLanguagesLanguagesTitle)

        self.lineConfigRegionsLanguagesLanguagesTitleDivider = QFrame(self.tabConfigRegionsLanguages)
        self.lineConfigRegionsLanguagesLanguagesTitleDivider.setObjectName(u"lineConfigRegionsLanguagesLanguagesTitleDivider")
        self.lineConfigRegionsLanguagesLanguagesTitleDivider.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRegionsLanguagesLanguagesTitleDivider.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRegionsLanguagesLanguages.addWidget(self.lineConfigRegionsLanguagesLanguagesTitleDivider)

        self.labelConfigRegionsLanguagesLanguagesDescription = QLabel(self.tabConfigRegionsLanguages)
        self.labelConfigRegionsLanguagesLanguagesDescription.setObjectName(u"labelConfigRegionsLanguagesLanguagesDescription")
        self.labelConfigRegionsLanguagesLanguagesDescription.setWordWrap(True)

        self.verticalLayoutConfigRegionsLanguagesLanguages.addWidget(self.labelConfigRegionsLanguagesLanguagesDescription)

        self.lineConfigRegionsLanguagesLanguagesDescriptionDivider = QFrame(self.tabConfigRegionsLanguages)
        self.lineConfigRegionsLanguagesLanguagesDescriptionDivider.setObjectName(u"lineConfigRegionsLanguagesLanguagesDescriptionDivider")
        self.lineConfigRegionsLanguagesLanguagesDescriptionDivider.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRegionsLanguagesLanguagesDescriptionDivider.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRegionsLanguagesLanguages.addWidget(self.lineConfigRegionsLanguagesLanguagesDescriptionDivider)

        self.listWidgetConfigRegionsLanguagesLanguages = QListWidget(self.tabConfigRegionsLanguages)
        self.listWidgetConfigRegionsLanguagesLanguages.setObjectName(u"listWidgetConfigRegionsLanguagesLanguages")
        self.listWidgetConfigRegionsLanguagesLanguages.setFrameShape(QFrame.Shape.WinPanel)
        self.listWidgetConfigRegionsLanguagesLanguages.setFrameShadow(QFrame.Shadow.Plain)
        self.listWidgetConfigRegionsLanguagesLanguages.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self.verticalLayoutConfigRegionsLanguagesLanguages.addWidget(self.listWidgetConfigRegionsLanguagesLanguages)


        self.horizontalLayoutConfigRegionsLanguages.addLayout(self.verticalLayoutConfigRegionsLanguagesLanguages)


        self.gridLayoutConfigRegionsLanguages.addLayout(self.horizontalLayoutConfigRegionsLanguages, 0, 0, 1, 1)


        self.horizontalLayout_3.addLayout(self.gridLayoutConfigRegionsLanguages)

        self.tabWidgetConfig.addTab(self.tabConfigRegionsLanguages, "")
        self.tabConfigIncludeExclude = QWidget()
        self.tabConfigIncludeExclude.setObjectName(u"tabConfigIncludeExclude")
        self.verticalLayout_3 = QVBoxLayout(self.tabConfigIncludeExclude)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.labelConfigIncludeExcludeDescription = QLabel(self.tabConfigIncludeExclude)
        self.labelConfigIncludeExcludeDescription.setObjectName(u"labelConfigIncludeExcludeDescription")
        self.labelConfigIncludeExcludeDescription.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.labelConfigIncludeExcludeDescription)

        self.lineConfigIncludeExcludeDescription = QFrame(self.tabConfigIncludeExclude)
        self.lineConfigIncludeExcludeDescription.setObjectName(u"lineConfigIncludeExcludeDescription")
        self.lineConfigIncludeExcludeDescription.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigIncludeExcludeDescription.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayout_3.addWidget(self.lineConfigIncludeExcludeDescription)

        self.tabWidgetConfigIncludeExclude = QTabWidget(self.tabConfigIncludeExclude)
        self.tabWidgetConfigIncludeExclude.setObjectName(u"tabWidgetConfigIncludeExclude")

        self.verticalLayout_3.addWidget(self.tabWidgetConfigIncludeExclude)

        self.tabWidgetConfig.addTab(self.tabConfigIncludeExclude, "")
        self.tabConfigRomDownloader = QWidget()
        self.tabConfigRomDownloader.setObjectName(u"tabConfigRomDownloader")
        self.horizontalLayout_7 = QHBoxLayout(self.tabConfigRomDownloader)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.gridLayoutConfigRomDownloader = QGridLayout()
        self.gridLayoutConfigRomDownloader.setObjectName(u"gridLayoutConfigRomDownloader")
        self.gridLayoutConfigRomDownloaderRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigRomDownloader.addItem(self.gridLayoutConfigRomDownloaderRight, 0, 3, 1, 1)

        self.gridLayoutConfigRomDownloaderLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigRomDownloader.addItem(self.gridLayoutConfigRomDownloaderLeft, 0, 1, 1, 1)

        self.verticalLayoutConfigRomDownloaderMiddle = QVBoxLayout()
        self.verticalLayoutConfigRomDownloaderMiddle.setObjectName(u"verticalLayoutConfigRomDownloaderMiddle")
        self.verticalSpacerConfigRomDownloaderTop = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomDownloaderMiddle.addItem(self.verticalSpacerConfigRomDownloaderTop)

        self.lineConfigRomDownloaderRemoteNameDividerTop = QFrame(self.tabConfigRomDownloader)
        self.lineConfigRomDownloaderRemoteNameDividerTop.setObjectName(u"lineConfigRomDownloaderRemoteNameDividerTop")
        self.lineConfigRomDownloaderRemoteNameDividerTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomDownloaderRemoteNameDividerTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.lineConfigRomDownloaderRemoteNameDividerTop)

        self.labelConfigRomDownloaderRemoteNameTitle = QLabel(self.tabConfigRomDownloader)
        self.labelConfigRomDownloaderRemoteNameTitle.setObjectName(u"labelConfigRomDownloaderRemoteNameTitle")
        self.labelConfigRomDownloaderRemoteNameTitle.setFont(font)
        self.labelConfigRomDownloaderRemoteNameTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.labelConfigRomDownloaderRemoteNameTitle)

        self.labelConfigRomDownloaderRemoteNameDescription = QLabel(self.tabConfigRomDownloader)
        self.labelConfigRomDownloaderRemoteNameDescription.setObjectName(u"labelConfigRomDownloaderRemoteNameDescription")
        self.labelConfigRomDownloaderRemoteNameDescription.setWordWrap(True)

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.labelConfigRomDownloaderRemoteNameDescription)

        self.lineEditConfigRomDownloaderRemoteName = QLineEdit(self.tabConfigRomDownloader)
        self.lineEditConfigRomDownloaderRemoteName.setObjectName(u"lineEditConfigRomDownloaderRemoteName")
        self.lineEditConfigRomDownloaderRemoteName.setFrame(True)

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.lineEditConfigRomDownloaderRemoteName)

        self.lineConfigRomDownloaderRemoteNameDividerBottom = QFrame(self.tabConfigRomDownloader)
        self.lineConfigRomDownloaderRemoteNameDividerBottom.setObjectName(u"lineConfigRomDownloaderRemoteNameDividerBottom")
        self.lineConfigRomDownloaderRemoteNameDividerBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomDownloaderRemoteNameDividerBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.lineConfigRomDownloaderRemoteNameDividerBottom)

        self.checkBoxConfigRomDownloaderSyncAll = QCheckBox(self.tabConfigRomDownloader)
        self.checkBoxConfigRomDownloaderSyncAll.setObjectName(u"checkBoxConfigRomDownloaderSyncAll")
        self.checkBoxConfigRomDownloaderSyncAll.setChecked(True)

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.checkBoxConfigRomDownloaderSyncAll)

        self.lineConfigRomDownloaderDryRunTop = QFrame(self.tabConfigRomDownloader)
        self.lineConfigRomDownloaderDryRunTop.setObjectName(u"lineConfigRomDownloaderDryRunTop")
        self.lineConfigRomDownloaderDryRunTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomDownloaderDryRunTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.lineConfigRomDownloaderDryRunTop)

        self.checkBoxConfigRomDownloaderDryRun = QCheckBox(self.tabConfigRomDownloader)
        self.checkBoxConfigRomDownloaderDryRun.setObjectName(u"checkBoxConfigRomDownloaderDryRun")

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.checkBoxConfigRomDownloaderDryRun)

        self.lineConfigRomDownloaderDruRunBottom = QFrame(self.tabConfigRomDownloader)
        self.lineConfigRomDownloaderDruRunBottom.setObjectName(u"lineConfigRomDownloaderDruRunBottom")
        self.lineConfigRomDownloaderDruRunBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomDownloaderDruRunBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomDownloaderMiddle.addWidget(self.lineConfigRomDownloaderDruRunBottom)

        self.verticalSpacerConfigRomDownloaderBottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomDownloaderMiddle.addItem(self.verticalSpacerConfigRomDownloaderBottom)


        self.gridLayoutConfigRomDownloader.addLayout(self.verticalLayoutConfigRomDownloaderMiddle, 0, 2, 1, 1)


        self.horizontalLayout_7.addLayout(self.gridLayoutConfigRomDownloader)

        self.tabWidgetConfig.addTab(self.tabConfigRomDownloader, "")
        self.tabConfigDupeParser = QWidget()
        self.tabConfigDupeParser.setObjectName(u"tabConfigDupeParser")
        self.horizontalLayout_4 = QHBoxLayout(self.tabConfigDupeParser)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.gridLayoutConfigDupeParser = QGridLayout()
        self.gridLayoutConfigDupeParser.setObjectName(u"gridLayoutConfigDupeParser")
        self.gridLayoutConfigDupeParserRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigDupeParser.addItem(self.gridLayoutConfigDupeParserRight, 0, 3, 1, 1)

        self.gridLayoutConfigDupeParserLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigDupeParser.addItem(self.gridLayoutConfigDupeParserLeft, 0, 1, 1, 1)

        self.verticalLayoutConfigDupeParserMiddle = QVBoxLayout()
        self.verticalLayoutConfigDupeParserMiddle.setObjectName(u"verticalLayoutConfigDupeParserMiddle")
        self.verticalSpacerConfigDupeParserTop = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigDupeParserMiddle.addItem(self.verticalSpacerConfigDupeParserTop)

        self.lineConfigDupeParserUseDatTop = QFrame(self.tabConfigDupeParser)
        self.lineConfigDupeParserUseDatTop.setObjectName(u"lineConfigDupeParserUseDatTop")
        self.lineConfigDupeParserUseDatTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigDupeParserUseDatTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigDupeParserMiddle.addWidget(self.lineConfigDupeParserUseDatTop)

        self.checkBoxConfigDupeParserUseDat = QCheckBox(self.tabConfigDupeParser)
        self.checkBoxConfigDupeParserUseDat.setObjectName(u"checkBoxConfigDupeParserUseDat")
        self.checkBoxConfigDupeParserUseDat.setChecked(True)

        self.verticalLayoutConfigDupeParserMiddle.addWidget(self.checkBoxConfigDupeParserUseDat)

        self.lineConfigDupeParserUseRetoolTop = QFrame(self.tabConfigDupeParser)
        self.lineConfigDupeParserUseRetoolTop.setObjectName(u"lineConfigDupeParserUseRetoolTop")
        self.lineConfigDupeParserUseRetoolTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigDupeParserUseRetoolTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigDupeParserMiddle.addWidget(self.lineConfigDupeParserUseRetoolTop)

        self.checkBoxConfigDupeParserUseRetool = QCheckBox(self.tabConfigDupeParser)
        self.checkBoxConfigDupeParserUseRetool.setObjectName(u"checkBoxConfigDupeParserUseRetool")
        self.checkBoxConfigDupeParserUseRetool.setChecked(True)

        self.verticalLayoutConfigDupeParserMiddle.addWidget(self.checkBoxConfigDupeParserUseRetool)

        self.lineConfigDupeParserUseRetoolBottom = QFrame(self.tabConfigDupeParser)
        self.lineConfigDupeParserUseRetoolBottom.setObjectName(u"lineConfigDupeParserUseRetoolBottom")
        self.lineConfigDupeParserUseRetoolBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigDupeParserUseRetoolBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigDupeParserMiddle.addWidget(self.lineConfigDupeParserUseRetoolBottom)

        self.verticalSpacerConfigDupeParserBottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigDupeParserMiddle.addItem(self.verticalSpacerConfigDupeParserBottom)


        self.gridLayoutConfigDupeParser.addLayout(self.verticalLayoutConfigDupeParserMiddle, 0, 2, 1, 1)


        self.horizontalLayout_4.addLayout(self.gridLayoutConfigDupeParser)

        self.tabWidgetConfig.addTab(self.tabConfigDupeParser, "")
        self.tabConfigGameFinder = QWidget()
        self.tabConfigGameFinder.setObjectName(u"tabConfigGameFinder")
        self.horizontalLayout_9 = QHBoxLayout(self.tabConfigGameFinder)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.gridLayoutConfigGameFinder = QGridLayout()
        self.gridLayoutConfigGameFinder.setObjectName(u"gridLayoutConfigGameFinder")
        self.gridLayoutConfigGameFinderLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigGameFinder.addItem(self.gridLayoutConfigGameFinderLeft, 0, 1, 1, 1)

        self.verticalLayoutConfigGameFinderMiddle = QVBoxLayout()
        self.verticalLayoutConfigGameFinderMiddle.setObjectName(u"verticalLayoutConfigGameFinderMiddle")
        self.verticalSpacerConfigGameFinderTop = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigGameFinderMiddle.addItem(self.verticalSpacerConfigGameFinderTop)

        self.lineConfigGameFinderFilterDupesDividerTop = QFrame(self.tabConfigGameFinder)
        self.lineConfigGameFinderFilterDupesDividerTop.setObjectName(u"lineConfigGameFinderFilterDupesDividerTop")
        self.lineConfigGameFinderFilterDupesDividerTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigGameFinderFilterDupesDividerTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigGameFinderMiddle.addWidget(self.lineConfigGameFinderFilterDupesDividerTop)

        self.checkBoxConfigGameFinderFilterDupes = QCheckBox(self.tabConfigGameFinder)
        self.checkBoxConfigGameFinderFilterDupes.setObjectName(u"checkBoxConfigGameFinderFilterDupes")
        self.checkBoxConfigGameFinderFilterDupes.setChecked(True)

        self.verticalLayoutConfigGameFinderMiddle.addWidget(self.checkBoxConfigGameFinderFilterDupes)

        self.lineConfigGameFinderFilterDupesDividerBottom = QFrame(self.tabConfigGameFinder)
        self.lineConfigGameFinderFilterDupesDividerBottom.setObjectName(u"lineConfigGameFinderFilterDupesDividerBottom")
        self.lineConfigGameFinderFilterDupesDividerBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigGameFinderFilterDupesDividerBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigGameFinderMiddle.addWidget(self.lineConfigGameFinderFilterDupesDividerBottom)

        self.verticalSpacerConfigGameFinderBottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigGameFinderMiddle.addItem(self.verticalSpacerConfigGameFinderBottom)


        self.gridLayoutConfigGameFinder.addLayout(self.verticalLayoutConfigGameFinderMiddle, 0, 2, 1, 1)

        self.gridLayoutConfigGameFinderRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigGameFinder.addItem(self.gridLayoutConfigGameFinderRight, 0, 3, 1, 1)


        self.horizontalLayout_9.addLayout(self.gridLayoutConfigGameFinder)

        self.tabWidgetConfig.addTab(self.tabConfigGameFinder, "")
        self.tabConfigRomParser = QWidget()
        self.tabConfigRomParser.setObjectName(u"tabConfigRomParser")
        self.horizontalLayout_10 = QHBoxLayout(self.tabConfigRomParser)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.gridLayoutConfigRomParser = QGridLayout()
        self.gridLayoutConfigRomParser.setObjectName(u"gridLayoutConfigRomParser")
        self.gridLayoutConfigRomParserRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigRomParser.addItem(self.gridLayoutConfigRomParserRight, 0, 3, 1, 1)

        self.gridLayouConfigRomParserLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigRomParser.addItem(self.gridLayouConfigRomParserLeft, 0, 1, 1, 1)

        self.verticalLayoutConfigRomParserMiddle = QVBoxLayout()
        self.verticalLayoutConfigRomParserMiddle.setObjectName(u"verticalLayoutConfigRomParserMiddle")
        self.verticalSpacerConfigRomParserTop = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomParserMiddle.addItem(self.verticalSpacerConfigRomParserTop)

        self.lineConfigRomParserUseDatTop = QFrame(self.tabConfigRomParser)
        self.lineConfigRomParserUseDatTop.setObjectName(u"lineConfigRomParserUseDatTop")
        self.lineConfigRomParserUseDatTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomParserUseDatTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomParserMiddle.addWidget(self.lineConfigRomParserUseDatTop)

        self.checkBoxConfigRomParserUseDat = QCheckBox(self.tabConfigRomParser)
        self.checkBoxConfigRomParserUseDat.setObjectName(u"checkBoxConfigRomParserUseDat")
        self.checkBoxConfigRomParserUseDat.setChecked(True)

        self.verticalLayoutConfigRomParserMiddle.addWidget(self.checkBoxConfigRomParserUseDat)

        self.lineConfigRomParserUseFilenamelTop = QFrame(self.tabConfigRomParser)
        self.lineConfigRomParserUseFilenamelTop.setObjectName(u"lineConfigRomParserUseFilenamelTop")
        self.lineConfigRomParserUseFilenamelTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomParserUseFilenamelTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomParserMiddle.addWidget(self.lineConfigRomParserUseFilenamelTop)

        self.checkBoxConfigRomParserUseFilename = QCheckBox(self.tabConfigRomParser)
        self.checkBoxConfigRomParserUseFilename.setObjectName(u"checkBoxConfigRomParserUseFilename")
        self.checkBoxConfigRomParserUseFilename.setChecked(True)

        self.verticalLayoutConfigRomParserMiddle.addWidget(self.checkBoxConfigRomParserUseFilename)

        self.lineConfigRomParserUseFilenameBottom = QFrame(self.tabConfigRomParser)
        self.lineConfigRomParserUseFilenameBottom.setObjectName(u"lineConfigRomParserUseFilenameBottom")
        self.lineConfigRomParserUseFilenameBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomParserUseFilenameBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomParserMiddle.addWidget(self.lineConfigRomParserUseFilenameBottom)

        self.verticalSpacerConfigRomParserBottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomParserMiddle.addItem(self.verticalSpacerConfigRomParserBottom)


        self.gridLayoutConfigRomParser.addLayout(self.verticalLayoutConfigRomParserMiddle, 0, 2, 1, 1)


        self.horizontalLayout_10.addLayout(self.gridLayoutConfigRomParser)

        self.tabWidgetConfig.addTab(self.tabConfigRomParser, "")
        self.tabConfigRomChooser = QWidget()
        self.tabConfigRomChooser.setObjectName(u"tabConfigRomChooser")
        self.horizontalLayout_11 = QHBoxLayout(self.tabConfigRomChooser)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.gridLayoutConfigRomChooser = QGridLayout()
        self.gridLayoutConfigRomChooser.setObjectName(u"gridLayoutConfigRomChooser")
        self.lineConfigRomChooserDivider = QFrame(self.tabConfigRomChooser)
        self.lineConfigRomChooserDivider.setObjectName(u"lineConfigRomChooserDivider")
        self.lineConfigRomChooserDivider.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomChooserDivider.setFrameShape(QFrame.Shape.VLine)

        self.gridLayoutConfigRomChooser.addWidget(self.lineConfigRomChooserDivider, 0, 1, 1, 1)

        self.verticalLayoutConfigRomChooserSettings = QVBoxLayout()
        self.verticalLayoutConfigRomChooserSettings.setObjectName(u"verticalLayoutConfigRomChooserSettings")
        self.verticalSpacerConfigRomChooserSettingsTop = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomChooserSettings.addItem(self.verticalSpacerConfigRomChooserSettingsTop)

        self.lineConfigRomChooserUseBestVersionDividerTop = QFrame(self.tabConfigRomChooser)
        self.lineConfigRomChooserUseBestVersionDividerTop.setObjectName(u"lineConfigRomChooserUseBestVersionDividerTop")
        self.lineConfigRomChooserUseBestVersionDividerTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomChooserUseBestVersionDividerTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.lineConfigRomChooserUseBestVersionDividerTop)

        self.checkBoxConfigRomChooserUseBestVersion = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserUseBestVersion.setObjectName(u"checkBoxConfigRomChooserUseBestVersion")
        self.checkBoxConfigRomChooserUseBestVersion.setChecked(True)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.checkBoxConfigRomChooserUseBestVersion)

        self.lineConfigRomChooserUseBestVersionDividerBottom = QFrame(self.tabConfigRomChooser)
        self.lineConfigRomChooserUseBestVersionDividerBottom.setObjectName(u"lineConfigRomChooserUseBestVersionDividerBottom")
        self.lineConfigRomChooserUseBestVersionDividerBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomChooserUseBestVersionDividerBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.lineConfigRomChooserUseBestVersionDividerBottom)

        self.checkBoxConfigRomChooserAllowMultipleRegions = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserAllowMultipleRegions.setObjectName(u"checkBoxConfigRomChooserAllowMultipleRegions")
        self.checkBoxConfigRomChooserAllowMultipleRegions.setChecked(False)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.checkBoxConfigRomChooserAllowMultipleRegions)

        self.lineConfigRomChooserFilterRegionsDividerTop = QFrame(self.tabConfigRomChooser)
        self.lineConfigRomChooserFilterRegionsDividerTop.setObjectName(u"lineConfigRomChooserFilterRegionsDividerTop")
        self.lineConfigRomChooserFilterRegionsDividerTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomChooserFilterRegionsDividerTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.lineConfigRomChooserFilterRegionsDividerTop)

        self.checkBoxConfigRomChooserFilterRegions = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserFilterRegions.setObjectName(u"checkBoxConfigRomChooserFilterRegions")
        self.checkBoxConfigRomChooserFilterRegions.setChecked(True)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.checkBoxConfigRomChooserFilterRegions)

        self.lineConfigRomChooserFilterRegionsDividerBottom = QFrame(self.tabConfigRomChooser)
        self.lineConfigRomChooserFilterRegionsDividerBottom.setObjectName(u"lineConfigRomChooserFilterRegionsDividerBottom")
        self.lineConfigRomChooserFilterRegionsDividerBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomChooserFilterRegionsDividerBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.lineConfigRomChooserFilterRegionsDividerBottom)

        self.checkBoxConfigRomChooserFilterLanguages = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserFilterLanguages.setObjectName(u"checkBoxConfigRomChooserFilterLanguages")
        self.checkBoxConfigRomChooserFilterLanguages.setChecked(True)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.checkBoxConfigRomChooserFilterLanguages)

        self.lineConfigRomChooserFilterLanguagesDividerBottom = QFrame(self.tabConfigRomChooser)
        self.lineConfigRomChooserFilterLanguagesDividerBottom.setObjectName(u"lineConfigRomChooserFilterLanguagesDividerBottom")
        self.lineConfigRomChooserFilterLanguagesDividerBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomChooserFilterLanguagesDividerBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.lineConfigRomChooserFilterLanguagesDividerBottom)

        self.verticalSpacerConfigRomChooserSettingsMiddle = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomChooserSettings.addItem(self.verticalSpacerConfigRomChooserSettingsMiddle)

        self.checkBoxConfigRomChooserDryRun = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDryRun.setObjectName(u"checkBoxConfigRomChooserDryRun")

        self.verticalLayoutConfigRomChooserSettings.addWidget(self.checkBoxConfigRomChooserDryRun)

        self.verticalSpacerConfigRomChooserSettingsBottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomChooserSettings.addItem(self.verticalSpacerConfigRomChooserSettingsBottom)


        self.gridLayoutConfigRomChooser.addLayout(self.verticalLayoutConfigRomChooserSettings, 0, 0, 1, 1)

        self.verticalLayoutConfigRomChooserDatFilters = QVBoxLayout()
        self.verticalLayoutConfigRomChooserDatFilters.setObjectName(u"verticalLayoutConfigRomChooserDatFilters")
        self.labelConfigRomChooserDatFiltersTitle = QLabel(self.tabConfigRomChooser)
        self.labelConfigRomChooserDatFiltersTitle.setObjectName(u"labelConfigRomChooserDatFiltersTitle")
        self.labelConfigRomChooserDatFiltersTitle.setFont(font)
        self.labelConfigRomChooserDatFiltersTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutConfigRomChooserDatFilters.addWidget(self.labelConfigRomChooserDatFiltersTitle)

        self.lineConfigRomChooserDatFiltersDivider = QFrame(self.tabConfigRomChooser)
        self.lineConfigRomChooserDatFiltersDivider.setObjectName(u"lineConfigRomChooserDatFiltersDivider")
        self.lineConfigRomChooserDatFiltersDivider.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigRomChooserDatFiltersDivider.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigRomChooserDatFilters.addWidget(self.lineConfigRomChooserDatFiltersDivider)

        self.labelConfigRomChooserDatFiltersDescription = QLabel(self.tabConfigRomChooser)
        self.labelConfigRomChooserDatFiltersDescription.setObjectName(u"labelConfigRomChooserDatFiltersDescription")
        self.labelConfigRomChooserDatFiltersDescription.setWordWrap(True)

        self.verticalLayoutConfigRomChooserDatFilters.addWidget(self.labelConfigRomChooserDatFiltersDescription)

        self.verticalSpacerConfigRomChooserDatFiltersTop = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomChooserDatFilters.addItem(self.verticalSpacerConfigRomChooserDatFiltersTop)

        self.horizontalLayoutConfigRomChooserDatFiltersAll = QHBoxLayout()
        self.horizontalLayoutConfigRomChooserDatFiltersAll.setObjectName(u"horizontalLayoutConfigRomChooserDatFiltersAll")
        self.verticalLayoutConfigRomChooserDatFiltersLeft = QVBoxLayout()
        self.verticalLayoutConfigRomChooserDatFiltersLeft.setObjectName(u"verticalLayoutConfigRomChooserDatFiltersLeft")
        self.checkBoxConfigRomChooserDatFiltersGames = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersGames.setObjectName(u"checkBoxConfigRomChooserDatFiltersGames")

        self.verticalLayoutConfigRomChooserDatFiltersLeft.addWidget(self.checkBoxConfigRomChooserDatFiltersGames)

        self.checkBoxConfigRomChooserDatFiltersAddons = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersAddons.setObjectName(u"checkBoxConfigRomChooserDatFiltersAddons")
        self.checkBoxConfigRomChooserDatFiltersAddons.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersLeft.addWidget(self.checkBoxConfigRomChooserDatFiltersAddons)

        self.checkBoxConfigRomChooserDatFiltersApplications = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersApplications.setObjectName(u"checkBoxConfigRomChooserDatFiltersApplications")
        self.checkBoxConfigRomChooserDatFiltersApplications.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersLeft.addWidget(self.checkBoxConfigRomChooserDatFiltersApplications)

        self.checkBoxConfigRomChooserDatFiltersAudio = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersAudio.setObjectName(u"checkBoxConfigRomChooserDatFiltersAudio")
        self.checkBoxConfigRomChooserDatFiltersAudio.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersLeft.addWidget(self.checkBoxConfigRomChooserDatFiltersAudio)

        self.checkBoxConfigRomChooserDatFiltersBadDumps = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersBadDumps.setObjectName(u"checkBoxConfigRomChooserDatFiltersBadDumps")
        self.checkBoxConfigRomChooserDatFiltersBadDumps.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersLeft.addWidget(self.checkBoxConfigRomChooserDatFiltersBadDumps)

        self.checkBoxConfigRomChooserDatFiltersConsole = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersConsole.setObjectName(u"checkBoxConfigRomChooserDatFiltersConsole")
        self.checkBoxConfigRomChooserDatFiltersConsole.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersLeft.addWidget(self.checkBoxConfigRomChooserDatFiltersConsole)

        self.checkBoxConfigRomChooserDatFiltersBonusDiscs = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersBonusDiscs.setObjectName(u"checkBoxConfigRomChooserDatFiltersBonusDiscs")
        self.checkBoxConfigRomChooserDatFiltersBonusDiscs.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersLeft.addWidget(self.checkBoxConfigRomChooserDatFiltersBonusDiscs)

        self.checkBoxConfigRomChooserDatFiltersCoverdiscs = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersCoverdiscs.setObjectName(u"checkBoxConfigRomChooserDatFiltersCoverdiscs")
        self.checkBoxConfigRomChooserDatFiltersCoverdiscs.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersLeft.addWidget(self.checkBoxConfigRomChooserDatFiltersCoverdiscs)


        self.horizontalLayoutConfigRomChooserDatFiltersAll.addLayout(self.verticalLayoutConfigRomChooserDatFiltersLeft)

        self.verticalLayoutConfigRomChooserDatFiltersRight = QVBoxLayout()
        self.verticalLayoutConfigRomChooserDatFiltersRight.setObjectName(u"verticalLayoutConfigRomChooserDatFiltersRight")
        self.checkBoxConfigRomChooserDatFiltersDemos = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersDemos.setObjectName(u"checkBoxConfigRomChooserDatFiltersDemos")
        self.checkBoxConfigRomChooserDatFiltersDemos.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersDemos)

        self.checkBoxConfigRomChooserDatFiltersEducational = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersEducational.setObjectName(u"checkBoxConfigRomChooserDatFiltersEducational")
        self.checkBoxConfigRomChooserDatFiltersEducational.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersEducational)

        self.checkBoxConfigRomChooserDatFiltersManuals = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersManuals.setObjectName(u"checkBoxConfigRomChooserDatFiltersManuals")
        self.checkBoxConfigRomChooserDatFiltersManuals.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersManuals)

        self.checkBoxConfigRomChooserDatFiltersMultimedia = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersMultimedia.setObjectName(u"checkBoxConfigRomChooserDatFiltersMultimedia")
        self.checkBoxConfigRomChooserDatFiltersMultimedia.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersMultimedia)

        self.checkBoxConfigRomChooserDatFiltersPirate = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersPirate.setObjectName(u"checkBoxConfigRomChooserDatFiltersPirate")
        self.checkBoxConfigRomChooserDatFiltersPirate.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersPirate)

        self.checkBoxConfigRomChooserDatFiltersPreproduction = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersPreproduction.setObjectName(u"checkBoxConfigRomChooserDatFiltersPreproduction")
        self.checkBoxConfigRomChooserDatFiltersPreproduction.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersPreproduction)

        self.checkBoxConfigRomChooserDatFiltersPromotional = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersPromotional.setObjectName(u"checkBoxConfigRomChooserDatFiltersPromotional")
        self.checkBoxConfigRomChooserDatFiltersPromotional.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersPromotional)

        self.checkBoxConfigRomChooserDatFiltersUnlicensed = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersUnlicensed.setObjectName(u"checkBoxConfigRomChooserDatFiltersUnlicensed")
        self.checkBoxConfigRomChooserDatFiltersUnlicensed.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersUnlicensed)

        self.checkBoxConfigRomChooserDatFiltersVideo = QCheckBox(self.tabConfigRomChooser)
        self.checkBoxConfigRomChooserDatFiltersVideo.setObjectName(u"checkBoxConfigRomChooserDatFiltersVideo")
        self.checkBoxConfigRomChooserDatFiltersVideo.setChecked(True)

        self.verticalLayoutConfigRomChooserDatFiltersRight.addWidget(self.checkBoxConfigRomChooserDatFiltersVideo)


        self.horizontalLayoutConfigRomChooserDatFiltersAll.addLayout(self.verticalLayoutConfigRomChooserDatFiltersRight)


        self.verticalLayoutConfigRomChooserDatFilters.addLayout(self.horizontalLayoutConfigRomChooserDatFiltersAll)

        self.verticalSpacerConfigRomChooserDatFiltersBottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigRomChooserDatFilters.addItem(self.verticalSpacerConfigRomChooserDatFiltersBottom)


        self.gridLayoutConfigRomChooser.addLayout(self.verticalLayoutConfigRomChooserDatFilters, 0, 2, 1, 1)


        self.horizontalLayout_11.addLayout(self.gridLayoutConfigRomChooser)

        self.tabWidgetConfig.addTab(self.tabConfigRomChooser, "")
        self.tabConfigDiscord = QWidget()
        self.tabConfigDiscord.setObjectName(u"tabConfigDiscord")
        self.horizontalLayout_8 = QHBoxLayout(self.tabConfigDiscord)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.gridLayoutConfigDiscord = QGridLayout()
        self.gridLayoutConfigDiscord.setObjectName(u"gridLayoutConfigDiscord")
        self.gridLayoutConfigDiscordLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigDiscord.addItem(self.gridLayoutConfigDiscordLeft, 0, 1, 1, 1)

        self.verticalLayoutConfigDiscordMiddle = QVBoxLayout()
        self.verticalLayoutConfigDiscordMiddle.setObjectName(u"verticalLayoutConfigDiscordMiddle")
        self.verticalSpacerConfigDiscordTop = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigDiscordMiddle.addItem(self.verticalSpacerConfigDiscordTop)

        self.lineConfigDiscordWebhookUrlDividerTop = QFrame(self.tabConfigDiscord)
        self.lineConfigDiscordWebhookUrlDividerTop.setObjectName(u"lineConfigDiscordWebhookUrlDividerTop")
        self.lineConfigDiscordWebhookUrlDividerTop.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigDiscordWebhookUrlDividerTop.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigDiscordMiddle.addWidget(self.lineConfigDiscordWebhookUrlDividerTop)

        self.labelConfigDiscordWebhookUrlTitle = QLabel(self.tabConfigDiscord)
        self.labelConfigDiscordWebhookUrlTitle.setObjectName(u"labelConfigDiscordWebhookUrlTitle")
        self.labelConfigDiscordWebhookUrlTitle.setFont(font)
        self.labelConfigDiscordWebhookUrlTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayoutConfigDiscordMiddle.addWidget(self.labelConfigDiscordWebhookUrlTitle)

        self.labelConfigDiscordWebhookUrlDescription = QLabel(self.tabConfigDiscord)
        self.labelConfigDiscordWebhookUrlDescription.setObjectName(u"labelConfigDiscordWebhookUrlDescription")
        self.labelConfigDiscordWebhookUrlDescription.setWordWrap(True)

        self.verticalLayoutConfigDiscordMiddle.addWidget(self.labelConfigDiscordWebhookUrlDescription)

        self.lineEditConfigDiscordWebhookUrl = QLineEdit(self.tabConfigDiscord)
        self.lineEditConfigDiscordWebhookUrl.setObjectName(u"lineEditConfigDiscordWebhookUrl")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.lineEditConfigDiscordWebhookUrl.sizePolicy().hasHeightForWidth())
        self.lineEditConfigDiscordWebhookUrl.setSizePolicy(sizePolicy1)
        self.lineEditConfigDiscordWebhookUrl.setMinimumSize(QSize(800, 0))
        self.lineEditConfigDiscordWebhookUrl.setFrame(True)

        self.verticalLayoutConfigDiscordMiddle.addWidget(self.lineEditConfigDiscordWebhookUrl)

        self.lineConfigDiscordWebhookUrlDividerBottom = QFrame(self.tabConfigDiscord)
        self.lineConfigDiscordWebhookUrlDividerBottom.setObjectName(u"lineConfigDiscordWebhookUrlDividerBottom")
        self.lineConfigDiscordWebhookUrlDividerBottom.setFrameShadow(QFrame.Shadow.Plain)
        self.lineConfigDiscordWebhookUrlDividerBottom.setFrameShape(QFrame.Shape.HLine)

        self.verticalLayoutConfigDiscordMiddle.addWidget(self.lineConfigDiscordWebhookUrlDividerBottom)

        self.verticalSpacerConfigDiscordBottom = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutConfigDiscordMiddle.addItem(self.verticalSpacerConfigDiscordBottom)


        self.gridLayoutConfigDiscord.addLayout(self.verticalLayoutConfigDiscordMiddle, 0, 2, 1, 1)

        self.gridLayoutConfigDiscordRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayoutConfigDiscord.addItem(self.gridLayoutConfigDiscordRight, 0, 3, 1, 1)


        self.horizontalLayout_8.addLayout(self.gridLayoutConfigDiscord)

        self.tabWidgetConfig.addTab(self.tabConfigDiscord, "")

        self.verticalLayout_2.addWidget(self.tabWidgetConfig)

        self.tabWidgetModules.addTab(self.tabConfig, "")

        self.verticalLayout.addWidget(self.tabWidgetModules)

        self.verticalLayoutBottomButtons = QVBoxLayout()
        self.verticalLayoutBottomButtons.setObjectName(u"verticalLayoutBottomButtons")
        self.horizontalLayoutBottomButtons = QHBoxLayout()
        self.horizontalLayoutBottomButtons.setObjectName(u"horizontalLayoutBottomButtons")
        self.pushButtonExit = QPushButton(self.centralwidget)
        self.pushButtonExit.setObjectName(u"pushButtonExit")
        self.pushButtonExit.setMinimumSize(QSize(130, 30))

        self.horizontalLayoutBottomButtons.addWidget(self.pushButtonExit)

        self.horizontalSpacerBottomButtons = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutBottomButtons.addItem(self.horizontalSpacerBottomButtons)

        self.pushButtonRunRomsearch = QPushButton(self.centralwidget)
        self.pushButtonRunRomsearch.setObjectName(u"pushButtonRunRomsearch")
        self.pushButtonRunRomsearch.setMinimumSize(QSize(130, 30))

        self.horizontalLayoutBottomButtons.addWidget(self.pushButtonRunRomsearch)


        self.verticalLayoutBottomButtons.addLayout(self.horizontalLayoutBottomButtons)


        self.verticalLayout.addLayout(self.verticalLayoutBottomButtons)

        RomSearch.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(RomSearch)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 950, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        RomSearch.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(RomSearch)
        self.statusbar.setObjectName(u"statusbar")
        RomSearch.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNewConfigFile)
        self.menuFile.addAction(self.actionLoadConfigFile)
        self.menuFile.addAction(self.actionSaveConfigFile)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionDocumentation)
        self.menuHelp.addAction(self.actionIssues)
        self.menuHelp.addAction(self.actionAbout)

        self.retranslateUi(RomSearch)

        self.tabWidgetModules.setCurrentIndex(0)
        self.tabWidgetConfig.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(RomSearch)
    # setupUi

    def retranslateUi(self, RomSearch):
        RomSearch.setWindowTitle(QCoreApplication.translate("RomSearch", u"ROMSearch", None))
        self.actionLoadConfigFile.setText(QCoreApplication.translate("RomSearch", u"Load config file", None))
#if QT_CONFIG(statustip)
        self.actionLoadConfigFile.setStatusTip(QCoreApplication.translate("RomSearch", u"Load config,yml file from disk", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.actionLoadConfigFile.setShortcut(QCoreApplication.translate("RomSearch", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("RomSearch", u"Exit", None))
#if QT_CONFIG(statustip)
        self.actionExit.setStatusTip(QCoreApplication.translate("RomSearch", u"Exit ROMSearch", None))
#endif // QT_CONFIG(statustip)
        self.actionDocumentation.setText(QCoreApplication.translate("RomSearch", u"Documentation", None))
#if QT_CONFIG(statustip)
        self.actionDocumentation.setStatusTip(QCoreApplication.translate("RomSearch", u"View online documentation", None))
#endif // QT_CONFIG(statustip)
        self.actionIssues.setText(QCoreApplication.translate("RomSearch", u"Issues", None))
#if QT_CONFIG(statustip)
        self.actionIssues.setStatusTip(QCoreApplication.translate("RomSearch", u"Open a GitHub issue", None))
#endif // QT_CONFIG(statustip)
        self.actionAbout.setText(QCoreApplication.translate("RomSearch", u"About", None))
#if QT_CONFIG(statustip)
        self.actionAbout.setStatusTip(QCoreApplication.translate("RomSearch", u"See About page", None))
#endif // QT_CONFIG(statustip)
        self.actionNewConfigFile.setText(QCoreApplication.translate("RomSearch", u"New config file", None))
#if QT_CONFIG(statustip)
        self.actionNewConfigFile.setStatusTip(QCoreApplication.translate("RomSearch", u"Create new config,yml file", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(shortcut)
        self.actionNewConfigFile.setShortcut(QCoreApplication.translate("RomSearch", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionSaveConfigFile.setText(QCoreApplication.translate("RomSearch", u"Save config file", None))
#if QT_CONFIG(shortcut)
        self.actionSaveConfigFile.setShortcut(QCoreApplication.translate("RomSearch", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.labelConfigRomsearchDirsTitle.setText(QCoreApplication.translate("RomSearch", u"ROMSearch Directory Locations", None))
        self.labelConfigRomsearchDirsDescription.setText(QCoreApplication.translate("RomSearch", u"Locations for the config files and various directories. Raw file and ROM directory must be set, the others will default to the current working directory", None))
#if QT_CONFIG(statustip)
        self.labelConfigConfigFile.setStatusTip(QCoreApplication.translate("RomSearch", u"Name of the config file", None))
#endif // QT_CONFIG(statustip)
        self.labelConfigConfigFile.setText(QCoreApplication.translate("RomSearch", u"Config File", None))
#if QT_CONFIG(tooltip)
        self.lineEditConfigConfigFile.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.lineEditConfigConfigFile.setStatusTip(QCoreApplication.translate("RomSearch", u"Name of the config file", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(statustip)
        self.labelConfigRawDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for the raw, downloaded files", None))
#endif // QT_CONFIG(statustip)
        self.labelConfigRawDir.setText(QCoreApplication.translate("RomSearch", u"Raw File Directory", None))
#if QT_CONFIG(statustip)
        self.lineEditConfigRawDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for the raw, downloaded files", None))
#endif // QT_CONFIG(statustip)
        self.lineEditConfigRawDir.setText("")
        self.lineEditConfigRawDir.setPlaceholderText(QCoreApplication.translate("RomSearch", u"raw", None))
        self.pushButtonConfigRawDir.setText(QCoreApplication.translate("RomSearch", u"Browse", None))
#if QT_CONFIG(statustip)
        self.labelConfigRomDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for the final, sorted ROM files", None))
#endif // QT_CONFIG(statustip)
        self.labelConfigRomDir.setText(QCoreApplication.translate("RomSearch", u"ROM Directory", None))
#if QT_CONFIG(statustip)
        self.lineEditConfigRomDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for the final, sorted ROM files", None))
#endif // QT_CONFIG(statustip)
        self.lineEditConfigRomDir.setText("")
        self.lineEditConfigRomDir.setPlaceholderText(QCoreApplication.translate("RomSearch", u"roms", None))
        self.pushButtonConfigRomDir.setText(QCoreApplication.translate("RomSearch", u"Browse", None))
#if QT_CONFIG(statustip)
        self.labelConfigDatDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for raw .dat files", None))
#endif // QT_CONFIG(statustip)
        self.labelConfigDatDir.setText(QCoreApplication.translate("RomSearch", u"DAT Directory", None))
#if QT_CONFIG(statustip)
        self.lineEditConfigDatDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for raw .dat files", None))
#endif // QT_CONFIG(statustip)
        self.lineEditConfigDatDir.setText(QCoreApplication.translate("RomSearch", u"dats", None))
        self.lineEditConfigDatDir.setPlaceholderText("")
        self.pushButtonConfigDatDir.setText(QCoreApplication.translate("RomSearch", u"Browse", None))
#if QT_CONFIG(statustip)
        self.labelConfigParsedDatDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for parsed .dat files and clonelists", None))
#endif // QT_CONFIG(statustip)
        self.labelConfigParsedDatDir.setText(QCoreApplication.translate("RomSearch", u"Parsed DAT/Clonelist Directory", None))
#if QT_CONFIG(statustip)
        self.lineEditConfigParsedDatDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for parsed .dat files and clonelists", None))
#endif // QT_CONFIG(statustip)
        self.lineEditConfigParsedDatDir.setText(QCoreApplication.translate("RomSearch", u"parsed_dats", None))
        self.lineEditConfigParsedDatDir.setPlaceholderText("")
        self.pushButtonConfigParsedDatDir.setText(QCoreApplication.translate("RomSearch", u"Browse", None))
#if QT_CONFIG(statustip)
        self.labelConfigDupeDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for dupe files", None))
#endif // QT_CONFIG(statustip)
        self.labelConfigDupeDir.setText(QCoreApplication.translate("RomSearch", u"Dupe Directory", None))
#if QT_CONFIG(statustip)
        self.lineEditConfigDupeDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for dupe files", None))
#endif // QT_CONFIG(statustip)
        self.lineEditConfigDupeDir.setText(QCoreApplication.translate("RomSearch", u"dupes", None))
        self.lineEditConfigDupeDir.setPlaceholderText("")
        self.pushButtonConfigDupeDir.setText(QCoreApplication.translate("RomSearch", u"Browse", None))
#if QT_CONFIG(statustip)
        self.labelConfigCacheDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for the moved files cache", None))
#endif // QT_CONFIG(statustip)
        self.labelConfigCacheDir.setText(QCoreApplication.translate("RomSearch", u"Cache Directory", None))
#if QT_CONFIG(statustip)
        self.lineEditConfigCacheDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for the moved files cache", None))
#endif // QT_CONFIG(statustip)
        self.lineEditConfigCacheDir.setText(QCoreApplication.translate("RomSearch", u"cache", None))
        self.lineEditConfigCacheDir.setPlaceholderText("")
        self.pushButtonConfigCacheDir.setText(QCoreApplication.translate("RomSearch", u"Browse", None))
#if QT_CONFIG(statustip)
        self.labelConfigLogDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for log files", None))
#endif // QT_CONFIG(statustip)
        self.labelConfigLogDir.setText(QCoreApplication.translate("RomSearch", u"Log Directory", None))
#if QT_CONFIG(statustip)
        self.lineEditConfigLogDir.setStatusTip(QCoreApplication.translate("RomSearch", u"Location for log files", None))
#endif // QT_CONFIG(statustip)
        self.lineEditConfigLogDir.setText(QCoreApplication.translate("RomSearch", u"logs", None))
        self.lineEditConfigLogDir.setPlaceholderText("")
        self.pushButtonConfigLogDir.setText(QCoreApplication.translate("RomSearch", u"Browse", None))
        self.labelConfigRomsearchModulesTitle.setText(QCoreApplication.translate("RomSearch", u"Which ROMSearch modules would you like to run?", None))
        self.labelConfigRomsearchModulesDescription.setText(QCoreApplication.translate("RomSearch", u"Check to include the various ROMSearch modules. By default, all are selected", None))
#if QT_CONFIG(tooltip)
        self.checkBoxConfigRunRomDownloader.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.checkBoxConfigRunRomDownloader.setStatusTip(QCoreApplication.translate("RomSearch", u"Run the ROMDownloader?", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRunRomDownloader.setText(QCoreApplication.translate("RomSearch", u"Run ROMDownloader", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRunDatParser.setStatusTip(QCoreApplication.translate("RomSearch", u"Run the DATParser?", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRunDatParser.setText(QCoreApplication.translate("RomSearch", u"Run DATParser", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRunDupeParser.setStatusTip(QCoreApplication.translate("RomSearch", u"Run the DupeParser?", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRunDupeParser.setText(QCoreApplication.translate("RomSearch", u"Run DupeParser", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRunRomChooser.setStatusTip(QCoreApplication.translate("RomSearch", u"Run the ROMChooser?", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRunRomChooser.setText(QCoreApplication.translate("RomSearch", u"Run ROMChooser", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRunRomMover.setStatusTip(QCoreApplication.translate("RomSearch", u"Run the ROMMover?", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRunRomMover.setText(QCoreApplication.translate("RomSearch", u"Run ROMMover", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigDryRun.setStatusTip(QCoreApplication.translate("RomSearch", u"If checked, will not make any changes to filesystem. Default unchecked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigDryRun.setText(QCoreApplication.translate("RomSearch", u"Dry Run", None))
        self.labelConfigRomsearchMethodTitle.setText(QCoreApplication.translate("RomSearch", u"What ROMSearch method would you like to use?", None))
        self.labelConfigRomsearchMethodDescription.setText(QCoreApplication.translate("RomSearch", u"You can either filter all files from the dat file (default), or download first then filter (completionist)", None))
#if QT_CONFIG(statustip)
        self.radioButtonConfigRomsearchMethodFilterDownload.setStatusTip(QCoreApplication.translate("RomSearch", u"Filter files from dat first, then download (default)", None))
#endif // QT_CONFIG(statustip)
        self.radioButtonConfigRomsearchMethodFilterDownload.setText(QCoreApplication.translate("RomSearch", u"Filter, then download", None))
#if QT_CONFIG(statustip)
        self.radioButtonConfigRomsearchMethodDownloadFilter.setStatusTip(QCoreApplication.translate("RomSearch", u"Download files first, then filter from the file list (completionist mode)", None))
#endif // QT_CONFIG(statustip)
        self.radioButtonConfigRomsearchMethodDownloadFilter.setText(QCoreApplication.translate("RomSearch", u"Download, then filter", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigMain), QCoreApplication.translate("RomSearch", u"Main", None))
        self.labelConfigPlatformsDescriptionTitle.setText(QCoreApplication.translate("RomSearch", u"Which platforms would you like to download ROMs for?", None))
        self.labelConfigPlatformsDescriptionBody.setText(QCoreApplication.translate("RomSearch", u"The order here simply determines the order that ROMSearch will loop over. Check the box to include that platform, uncheck it to exclude", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigPlatforms), QCoreApplication.translate("RomSearch", u"Platforms", None))
        self.labelConfigRegionsLanguagesRegionsTitle.setText(QCoreApplication.translate("RomSearch", u"Which regions would you like to download ROMs for?", None))
        self.labelConfigRegionsLanguagesRegionsDescription.setText(QCoreApplication.translate("RomSearch", u"Order is important here! Higher in the list means more preferred. Drag boxes to rearrange. Check the box to include that platform, uncheck it to exclude", None))
        self.labelConfigRegionsLanguagesLanguagesTitle.setText(QCoreApplication.translate("RomSearch", u"Which languages would you like to consider?", None))
        self.labelConfigRegionsLanguagesLanguagesDescription.setText(QCoreApplication.translate("RomSearch", u"Order is important here! Higher in the list means more preferred. Drag boxes to rearrange. Check the box to include that language, uncheck it to exclude", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigRegionsLanguages), QCoreApplication.translate("RomSearch", u"Regions/Languages", None))
        self.labelConfigIncludeExcludeDescription.setText(QCoreApplication.translate("RomSearch", u"Includes/excludes for each platform. Platforms will only appear here if they have been checked in the Platforms tab. Begin each separate entry with a new line", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigIncludeExclude), QCoreApplication.translate("RomSearch", u"Includes/Excludes", None))
        self.labelConfigRomDownloaderRemoteNameTitle.setText(QCoreApplication.translate("RomSearch", u"Remote Name", None))
        self.labelConfigRomDownloaderRemoteNameDescription.setText(QCoreApplication.translate("RomSearch", u"Remote name that Rclone uses. Must be set to use ROMDownloader", None))
        self.lineEditConfigRomDownloaderRemoteName.setText("")
        self.lineEditConfigRomDownloaderRemoteName.setPlaceholderText(QCoreApplication.translate("RomSearch", u"remote", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomDownloaderSyncAll.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to sync everything when running ROMDownloader or whether to filter files based on includes/excludes. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomDownloaderSyncAll.setText(QCoreApplication.translate("RomSearch", u"Sync All", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomDownloaderDryRun.setStatusTip(QCoreApplication.translate("RomSearch", u"If checked, will not make any changes to filesystem. Default unchecked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomDownloaderDryRun.setText(QCoreApplication.translate("RomSearch", u"Dry Run", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigRomDownloader), QCoreApplication.translate("RomSearch", u"ROMDownloader", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigDupeParserUseDat.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to use the dat file to figure out dupes. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigDupeParserUseDat.setText(QCoreApplication.translate("RomSearch", u"Use .dat", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigDupeParserUseRetool.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to use the retool clonelist to figure out dupes. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigDupeParserUseRetool.setText(QCoreApplication.translate("RomSearch", u"Use retool", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigDupeParser), QCoreApplication.translate("RomSearch", u"DupeParser", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigGameFinderFilterDupes.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to filter dupes based on the DupeParser catalog. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigGameFinderFilterDupes.setText(QCoreApplication.translate("RomSearch", u"Filter dupes", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigGameFinder), QCoreApplication.translate("RomSearch", u"GameFinder", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomParserUseDat.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to use the dat file to parse ROM information. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomParserUseDat.setText(QCoreApplication.translate("RomSearch", u"Use .dat", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomParserUseFilename.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to use the filename to parse ROM information. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomParserUseFilename.setText(QCoreApplication.translate("RomSearch", u"Use filename", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigRomParser), QCoreApplication.translate("RomSearch", u"ROMParser", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserUseBestVersion.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to only use the best ROM version per-region. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserUseBestVersion.setText(QCoreApplication.translate("RomSearch", u"Use best version?", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserAllowMultipleRegions.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to allow multiple regions, or to just use the most preferred region. Default unchecked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserAllowMultipleRegions.setText(QCoreApplication.translate("RomSearch", u"Allow multiple regions?", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserFilterRegions.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to remove ROMs that don't fall into the selected region choices. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserFilterRegions.setText(QCoreApplication.translate("RomSearch", u"Filter regions?", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserFilterLanguages.setStatusTip(QCoreApplication.translate("RomSearch", u"Whether to remove ROMs that don't fall into the selected language choices. Default checked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserFilterLanguages.setText(QCoreApplication.translate("RomSearch", u"Filter languages?", None))
#if QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserDryRun.setStatusTip(QCoreApplication.translate("RomSearch", u"If checked, will not make any changes to filesystem. Default unchecked", None))
#endif // QT_CONFIG(statustip)
        self.checkBoxConfigRomChooserDryRun.setText(QCoreApplication.translate("RomSearch", u"Dry Run", None))
        self.labelConfigRomChooserDatFiltersTitle.setText(QCoreApplication.translate("RomSearch", u"Filter .dat categories", None))
        self.labelConfigRomChooserDatFiltersDescription.setText(QCoreApplication.translate("RomSearch", u"If the box is checked, ROM categories with that tag will be removed. By default, we remove anything that is not flagged as a game", None))
        self.checkBoxConfigRomChooserDatFiltersGames.setText(QCoreApplication.translate("RomSearch", u"Games", None))
        self.checkBoxConfigRomChooserDatFiltersAddons.setText(QCoreApplication.translate("RomSearch", u"Add-Ons", None))
        self.checkBoxConfigRomChooserDatFiltersApplications.setText(QCoreApplication.translate("RomSearch", u"Applications", None))
        self.checkBoxConfigRomChooserDatFiltersAudio.setText(QCoreApplication.translate("RomSearch", u"Audio", None))
        self.checkBoxConfigRomChooserDatFiltersBadDumps.setText(QCoreApplication.translate("RomSearch", u"Bad Dumps", None))
        self.checkBoxConfigRomChooserDatFiltersConsole.setText(QCoreApplication.translate("RomSearch", u"Console", None))
        self.checkBoxConfigRomChooserDatFiltersBonusDiscs.setText(QCoreApplication.translate("RomSearch", u"Bonus Discs", None))
        self.checkBoxConfigRomChooserDatFiltersCoverdiscs.setText(QCoreApplication.translate("RomSearch", u"Coverdiscs", None))
        self.checkBoxConfigRomChooserDatFiltersDemos.setText(QCoreApplication.translate("RomSearch", u"Demos", None))
        self.checkBoxConfigRomChooserDatFiltersEducational.setText(QCoreApplication.translate("RomSearch", u"Educational", None))
        self.checkBoxConfigRomChooserDatFiltersManuals.setText(QCoreApplication.translate("RomSearch", u"Manuals", None))
        self.checkBoxConfigRomChooserDatFiltersMultimedia.setText(QCoreApplication.translate("RomSearch", u"Multimedia", None))
        self.checkBoxConfigRomChooserDatFiltersPirate.setText(QCoreApplication.translate("RomSearch", u"Pirate", None))
        self.checkBoxConfigRomChooserDatFiltersPreproduction.setText(QCoreApplication.translate("RomSearch", u"Preproduction", None))
        self.checkBoxConfigRomChooserDatFiltersPromotional.setText(QCoreApplication.translate("RomSearch", u"Promotional", None))
        self.checkBoxConfigRomChooserDatFiltersUnlicensed.setText(QCoreApplication.translate("RomSearch", u"Unlicensed", None))
        self.checkBoxConfigRomChooserDatFiltersVideo.setText(QCoreApplication.translate("RomSearch", u"Video", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigRomChooser), QCoreApplication.translate("RomSearch", u"ROMChooser", None))
        self.labelConfigDiscordWebhookUrlTitle.setText(QCoreApplication.translate("RomSearch", u"Webhook URL", None))
        self.labelConfigDiscordWebhookUrlDescription.setText(QCoreApplication.translate("RomSearch", u"URL for Discord webhooks. Must be set for notifications to be sent", None))
        self.lineEditConfigDiscordWebhookUrl.setText("")
        self.lineEditConfigDiscordWebhookUrl.setPlaceholderText(QCoreApplication.translate("RomSearch", u"https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX", None))
        self.tabWidgetConfig.setTabText(self.tabWidgetConfig.indexOf(self.tabConfigDiscord), QCoreApplication.translate("RomSearch", u"Discord", None))
        self.tabWidgetModules.setTabText(self.tabWidgetModules.indexOf(self.tabConfig), QCoreApplication.translate("RomSearch", u"Config", None))
#if QT_CONFIG(statustip)
        self.pushButtonExit.setStatusTip(QCoreApplication.translate("RomSearch", u"Exit ROMSearch", None))
#endif // QT_CONFIG(statustip)
        self.pushButtonExit.setText(QCoreApplication.translate("RomSearch", u"Exit", None))
#if QT_CONFIG(statustip)
        self.pushButtonRunRomsearch.setStatusTip(QCoreApplication.translate("RomSearch", u"Run ROMSearch! Will automatically save the config file", None))
#endif // QT_CONFIG(statustip)
        self.pushButtonRunRomsearch.setText(QCoreApplication.translate("RomSearch", u"Run ROMSearch", None))
        self.menuFile.setTitle(QCoreApplication.translate("RomSearch", u"File", None))
        self.menuHelp.setTitle(QCoreApplication.translate("RomSearch", u"Help", None))
    # retranslateUi

