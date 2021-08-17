import sys
import threading
import time
import cv2
import FileManager

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QSizePolicy, QPushButton
from PyQt5 import QtGui

from ImageUtils import cvImgToQtImg, draw_area, isSpotInRect
from Camera import VideoThread, CameraSetup

CAMERA_W = 400
CAMERA_H = 300

IMAGE_PATH = "Images\\"

TIMER_FONT = 'Arial'
CONFIRM_BUTTON_FONT = 'Arial'

Option_INC_TIME_NORMAL_LABEL_TEXT = "일반 사람에 대한 증가 시간 (자연수)(초) : "
Option_INC_TIME_SPECIAL_LABEL_TEXT = "사회적 약자에 대한 증가 시간 (자연수)(초) : "
Option_TIME_CROSSWALK_GREEN_LABEL_TEXT = "횡단보도 기본 시간 (자연수)(초) : "
Option_TIME_CARLANE_GREEN_LABEL_TEXT = "차량이동 기본 시간 (자연수)(초) : "
Option_TIME_CHAGNE_TERM_LABEL_TEXT = "신호 변경 시간 간격 (자연수)(초) : "


# https://blog.xcoda.net/104
# AutoMagically Resize The Input Image Size To ( CAMERA_W * CAMERA_H )

class Main(QWidget):
    def __init__(self):
        super().__init__()

        self.isPreparingCamera = False
        self.config = FileManager.configManager()

        self.isTimerRun = False
        self.timerThread = threading.Thread(target=self.TimerMethod)
        self.changeTerm = self.config.getConfig()['CHANGE_TERM']
        self.timeStack = 0
        self.carlaneTime = self.config.getConfig()['CARLANE_TIME']
        self.crosswalkTime = self.config.getConfig()['CROSSWALK_TIME']
        self.isCrosswalkTime = False
        self.isCarlaneTime = False

        self.Left_Camera_Carlane_Button = QPushButton()
        self.Right_Camera_Carlane_Button = QPushButton()
        self.Option_TIME_CHANGE_TERM_Input = QLineEdit()
        self.Option_TIME_CARLANE_GREEN_Input = QLineEdit()
        self.Option_TIME_CROSSWALK_GREEN_Input = QLineEdit()
        self.Right_Camera_Crosswalk_Button = QPushButton()
        self.Left_Camera_Crosswalk_Button = QPushButton()
        self.Change_CarTime_Button = QPushButton()
        self.Change_CrosswalkTime_Button = QPushButton()
        self.Option_INC_TIME_SPECIAL_Input = QLineEdit()
        self.ConfirmButton = QPushButton()
        self.TimerLabel = QLabel()
        self.Option_INC_TIME_NORMAL_Input = QLineEdit()

        self.setWindowTitle(":: The CROSS :: Smart Traffic Control System")

        self.CAMERA_PREPARING_IMG_L = cvImgToQtImg(cv2.imread(IMAGE_PATH + "camera_preparing.png"), CAMERA_W)
        self.CAMERA_PREPARING_IMG_R = cvImgToQtImg(cv2.imread(IMAGE_PATH + "camera_preparing.png"), CAMERA_W)

        self.CAMERA_NO_SIGNAL_IMG_L = cvImgToQtImg(cv2.imread(IMAGE_PATH + "camera_no_signal.png"), CAMERA_W)
        self.CAMERA_NO_SIGNAL_IMG_R = cvImgToQtImg(cv2.imread(IMAGE_PATH + "camera_no_signal.png"), CAMERA_W)

        self.CROSSWALK_GREEN_ON_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "crosswalk_green_on.png"))
        self.CROSSWALK_GREEN_OFF_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "crosswalk_green_off.png"))
        self.CROSSWALK_RED_ON_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "crosswalk_red_on.png"))
        self.CROSSWALK_RED_OFF_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "crosswalk_red_off.png"))

        self.GREEN_ON_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "green_on.png"))
        self.GREEN_OFF_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "green_off.png"))
        self.RED_ON_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "red_on.png"))
        self.RED_OFF_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "red_off.png"))
        self.YELLOW_ON_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "yellow_on.png"))
        self.YELLOW_OFF_IMG = cvImgToQtImg(cv2.imread(IMAGE_PATH + "yellow_off.png"))

        self.CarLane_Green = QLabel()
        self.CarLane_Green.setPixmap(self.GREEN_OFF_IMG.pixmap())
        self.CarLane_Yellow = QLabel()
        self.CarLane_Yellow.setPixmap(self.YELLOW_OFF_IMG.pixmap())
        self.CarLane_Red = QLabel()
        self.CarLane_Red.setPixmap(self.RED_OFF_IMG.pixmap())
        self.Crosswalk_Green = QLabel()
        self.Crosswalk_Green.setPixmap(self.CROSSWALK_GREEN_OFF_IMG.pixmap())
        self.Crosswalk_Red = QLabel()
        self.Crosswalk_Red.setPixmap(self.CROSSWALK_RED_OFF_IMG.pixmap())

        self.CameraRight = QLabel()
        self.CameraRight.setPixmap(self.CAMERA_NO_SIGNAL_IMG_R.pixmap())
        self.CameraLeft = QLabel()
        self.CameraLeft.setPixmap(self.CAMERA_NO_SIGNAL_IMG_L.pixmap())
        self.thread = VideoThread(-1, -1)
        self.initUI()

    def initUI(self):
        UpPanel = QHBoxLayout()
        DownPanel = QHBoxLayout()

        CameraPanel = QHBoxLayout()

        SignalPanel = QVBoxLayout()
        CrosswalkPanel = QHBoxLayout()
        CarLanePanel = QHBoxLayout()

        OptionPanel = QHBoxLayout()
        OptionList = QVBoxLayout()
        ControlPanel = QVBoxLayout()

        CameraPanel.addWidget(self.CameraLeft)
        CameraPanel.addWidget(self.CameraRight)

        CrosswalkPanel.addWidget(self.Crosswalk_Red)
        CrosswalkPanel.addWidget(self.Crosswalk_Green)

        self.TimerLabel.setFont(QFont(TIMER_FONT, 60))
        self.TimerLabel.setText("0")
        CrosswalkPanel.addStretch(1)
        CrosswalkPanel.addWidget(self.TimerLabel)
        CrosswalkPanel.addStretch(1)

        CarLanePanel.addWidget(self.CarLane_Red)
        CarLanePanel.addWidget(self.CarLane_Yellow)
        CarLanePanel.addWidget(self.CarLane_Green)

        SignalPanel.addLayout(CrosswalkPanel)
        SignalPanel.addLayout(CarLanePanel)

        UpPanel.addLayout(CameraPanel, 6)
        UpPanel.addLayout(SignalPanel, 4)

        # =======================================================
        # ==================== OPTION PANEL =====================
        # =======================================================

        Option_INC_TIME_NORMAL = QHBoxLayout()
        Option_INC_TIME_NORMAL_LABEL = QLabel()
        Option_INC_TIME_NORMAL_LABEL.setText(Option_INC_TIME_NORMAL_LABEL_TEXT)
        self.Option_INC_TIME_NORMAL_Input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.Option_INC_TIME_NORMAL_Input.setText(str(self.config.getConfig()['INCREASE_TIME_NORMAL']))
        Option_INC_TIME_NORMAL.addWidget(Option_INC_TIME_NORMAL_LABEL)
        Option_INC_TIME_NORMAL.addWidget(self.Option_INC_TIME_NORMAL_Input)
        OptionList.addLayout(Option_INC_TIME_NORMAL)

        Option_INC_TIME_SPECIAL = QHBoxLayout()
        Option_INC_TIME_SPECIAL_LABEL = QLabel()
        Option_INC_TIME_SPECIAL_LABEL.setText(Option_INC_TIME_SPECIAL_LABEL_TEXT)
        self.Option_INC_TIME_SPECIAL_Input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.Option_INC_TIME_SPECIAL_Input.setText(str(self.config.getConfig()['INCREASE_TIME_SPECIAL']))
        Option_INC_TIME_SPECIAL.addWidget(Option_INC_TIME_SPECIAL_LABEL)
        Option_INC_TIME_SPECIAL.addWidget(self.Option_INC_TIME_SPECIAL_Input)
        OptionList.addLayout(Option_INC_TIME_SPECIAL)

        Option_TIME_CROSSWALK_GREEN = QHBoxLayout()
        Option_TIME_CROSSWALK_GREEN_LABEL = QLabel()
        Option_TIME_CROSSWALK_GREEN_LABEL.setText(Option_TIME_CROSSWALK_GREEN_LABEL_TEXT)
        self.Option_TIME_CROSSWALK_GREEN_Input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.Option_TIME_CROSSWALK_GREEN_Input.setText(str(self.config.getConfig()['CROSSWALK_TIME']))
        Option_TIME_CROSSWALK_GREEN.addWidget(Option_TIME_CROSSWALK_GREEN_LABEL)
        Option_TIME_CROSSWALK_GREEN.addWidget(self.Option_TIME_CROSSWALK_GREEN_Input)
        OptionList.addLayout(Option_TIME_CROSSWALK_GREEN)

        Option_TIME_CARLANE_GREEN = QHBoxLayout()
        Option_TIME_CARLANE_GREEN_LABEL = QLabel()
        Option_TIME_CARLANE_GREEN_LABEL.setText(Option_TIME_CARLANE_GREEN_LABEL_TEXT)
        self.Option_TIME_CARLANE_GREEN_Input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.Option_TIME_CARLANE_GREEN_Input.setText(str(self.config.getConfig()['CARLANE_TIME']))
        Option_TIME_CARLANE_GREEN.addWidget(Option_TIME_CARLANE_GREEN_LABEL)
        Option_TIME_CARLANE_GREEN.addWidget(self.Option_TIME_CARLANE_GREEN_Input)
        OptionList.addLayout(Option_TIME_CARLANE_GREEN)

        Option_TIME_CHAGNE_TERM = QHBoxLayout()
        Option_TIME_CHAGNE_TERM_LABEL = QLabel()
        Option_TIME_CHAGNE_TERM_LABEL.setText(Option_TIME_CHAGNE_TERM_LABEL_TEXT)
        self.Option_TIME_CHANGE_TERM_Input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.Option_TIME_CHANGE_TERM_Input.setText(str(self.config.getConfig()['CHANGE_TERM']))
        Option_TIME_CHAGNE_TERM.addWidget(Option_TIME_CHAGNE_TERM_LABEL)
        Option_TIME_CHAGNE_TERM.addWidget(self.Option_TIME_CHANGE_TERM_Input)
        OptionList.addLayout(Option_TIME_CHAGNE_TERM)

        # OptionList Attach To OptionPanel
        OptionPanel.addLayout(OptionList, 8)

        # =======================================================
        # ==================== CONTROL PANEL ====================
        # =======================================================

        self.Change_CrosswalkTime_Button.setText("횡단보도 신호로 변경")
        self.Change_CarTime_Button.setText("도로주행 신호로 변경")

        self.Change_CrosswalkTime_Button.clicked.connect(self.Change_CrosswalkTime_Button_Event)
        self.Change_CarTime_Button.clicked.connect(self.Change_CarTime_Button_Event)

        self.Left_Camera_Crosswalk_Button.setText("좌측 카메라 횡단보도 영역설정")
        self.Right_Camera_Crosswalk_Button.setText("우측 카메라 횡단보도 영역설정")

        self.Left_Camera_Crosswalk_Button.clicked.connect(self.Left_Camera_Crosswalk_Button_Event)
        self.Right_Camera_Crosswalk_Button.clicked.connect(self.Right_Camera_Crosswalk_Button_Event)

        self.Left_Camera_Carlane_Button.setText("좌측 카메라 차량도로 영역설정")
        self.Right_Camera_Carlane_Button.setText("우측 카메라 차량도로 영역설정")

        self.Left_Camera_Carlane_Button.clicked.connect(self.Left_Camera_Carlane_Button_Event)
        self.Right_Camera_Carlane_Button.clicked.connect(self.Right_Camera_Carlane_Button_Event)

        Control_Crosswalk_Panel = QHBoxLayout()
        Control_Crosswalk_Panel.addWidget(self.Change_CarTime_Button)
        Control_Crosswalk_Panel.addWidget(self.Change_CrosswalkTime_Button)

        Control_Camera_Crosswalk_Panel = QHBoxLayout()
        Control_Camera_Crosswalk_Panel.addWidget(self.Left_Camera_Crosswalk_Button)
        Control_Camera_Crosswalk_Panel.addWidget(self.Right_Camera_Crosswalk_Button)

        Control_Camera_Carlane_Panel = QHBoxLayout()
        Control_Camera_Carlane_Panel.addWidget(self.Left_Camera_Carlane_Button)
        Control_Camera_Carlane_Panel.addWidget(self.Right_Camera_Carlane_Button)

        ControlPanel.addLayout(Control_Crosswalk_Panel)
        ControlPanel.addLayout(Control_Camera_Crosswalk_Panel)
        ControlPanel.addLayout(Control_Camera_Carlane_Panel)

        # =======================================================
        # ==================== CONFIRM BUTTON ===================
        # =======================================================

        self.ConfirmButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ConfirmButton.setText("설정 저장")
        self.ConfirmButton.setFont(QFont(CONFIRM_BUTTON_FONT, 20))
        self.ConfirmButton.clicked.connect(self.confirmButtonClicked)
        OptionPanel.addWidget(self.ConfirmButton, 2)

        DownPanel.addLayout(OptionPanel, 63)
        DownPanel.addLayout(ControlPanel, 37)

        allPanel = QVBoxLayout()
        allPanel.addLayout(UpPanel)
        allPanel.addLayout(DownPanel)

        self.setLayout(allPanel)
        self.setFixedSize(self.sizeHint())

        # Set Up Camera
        self.refreshCamera()
        self.startTimer()
        self.show()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.stopCamera()
        self.stopTimer()

    #   imgLeft & imgRight must be cvImage
    def processing(self, imgLeft, imgRight, left_pos, right_pos,
                   ambulance_pos_left, cane_pos_left, wheelchair_pos_left, baby_carriage_pos_left,
                   ambulance_pos_right, cane_pos_right, wheelchair_pos_right, baby_carriage_pos_right):

        if self.isPreparingCamera is True:
            return

        isPersonExist = False
        isDisablePersonExist = False
        # TODO : Reference Siren From Other Code!
        isSiren = False
        isAmbulanceExist = False

        if len(imgLeft) == 0:
            imgLeft = self.CAMERA_NO_SIGNAL_IMG_L
        else:
            CrossArea = self.config.getConfig()['LEFT_CAMERA_CROSSWALK_POS']
            CarLaneArea = self.config.getConfig()['LEFT_CAMERA_CARLANE_POS']

            if isPersonExist is False and isSpotInRect(CrossArea, left_pos):
                isPersonExist = True

            if isDisablePersonExist is False:
                if isSpotInRect(CrossArea, cane_pos_left) or isSpotInRect(CrossArea, wheelchair_pos_left) or isSpotInRect(CrossArea, baby_carriage_pos_left):
                    isDisablePersonExist = True

            if isAmbulanceExist is False:
                if isSpotInRect(CarLaneArea, ambulance_pos_left):
                    isAmbulanceExist = True

            imgLeft = draw_area(imgLeft, CrossArea)
            imgLeft = draw_area(imgLeft, CarLaneArea, (255, 0, 0), (255, 0, 0))
            imgLeft = cvImgToQtImg(imgLeft, CAMERA_W)

        self.CameraLeft.setPixmap(imgLeft.pixmap())

        if len(imgRight) == 0:
            imgRight = self.CAMERA_NO_SIGNAL_IMG_R
        else:
            CrossArea = self.config.getConfig()['RIGHT_CAMERA_CROSSWALK_POS']
            CarLaneArea = self.config.getConfig()['RIGHT_CAMERA_CARLANE_POS']

            if isPersonExist is False and isSpotInRect(CrossArea, right_pos):
                isPersonExist = True

            if isDisablePersonExist is False:
                if isSpotInRect(CrossArea, cane_pos_right) or isSpotInRect(CrossArea, wheelchair_pos_right) or isSpotInRect(CrossArea, baby_carriage_pos_right):
                    isDisablePersonExist = True

            if isAmbulanceExist is False:
                if isSpotInRect(CarLaneArea, ambulance_pos_right):
                    isAmbulanceExist = True

            imgRight = draw_area(imgRight, CrossArea)
            imgRight = draw_area(imgRight, CarLaneArea, (255, 0, 0), (255, 0, 0))
            imgRight = cvImgToQtImg(imgRight, CAMERA_W)

        self.CameraRight.setPixmap(imgRight.pixmap())

    def crosswalk_TurnRed_On(self):
        self.Crosswalk_Red.setPixmap(self.CROSSWALK_RED_ON_IMG.pixmap())

    def crosswalk_TurnRed_Off(self):
        self.Crosswalk_Red.setPixmap(self.CROSSWALK_RED_OFF_IMG.pixmap())

    def crosswalk_TurnGreen_On(self):
        self.Crosswalk_Green.setPixmap(self.CROSSWALK_GREEN_ON_IMG.pixmap())

    def crosswalk_TurnGreen_Off(self):
        self.Crosswalk_Green.setPixmap(self.CROSSWALK_GREEN_OFF_IMG.pixmap())

    def carlane_TurnRed_On(self):
        self.CarLane_Red.setPixmap(self.RED_ON_IMG.pixmap())

    def carlane_TurnRed_Off(self):
        self.CarLane_Red.setPixmap(self.RED_OFF_IMG.pixmap())

    def carlane_TurnGreen_On(self):
        self.CarLane_Green.setPixmap(self.GREEN_ON_IMG.pixmap())

    def carlane_TurnGreen_Off(self):
        self.CarLane_Green.setPixmap(self.GREEN_OFF_IMG.pixmap())

    def carlane_TurnYellow_On(self):
        self.CarLane_Yellow.setPixmap(self.YELLOW_ON_IMG.pixmap())

    def carlane_TurnYellow_Off(self):
        self.CarLane_Yellow.setPixmap(self.YELLOW_OFF_IMG.pixmap())

    def printPreparingCamera(self):
        self.isPreparingCamera = True
        self.CameraLeft.setPixmap(self.CAMERA_PREPARING_IMG_L.pixmap())
        self.CameraRight.setPixmap(self.CAMERA_PREPARING_IMG_R.pixmap())

    def stopCamera(self):
        if self.thread.isRunning() is True:
            self.thread.stop()
            self.printPreparingCamera()

    def refreshCamera(self):
        self.stopCamera()
        self.printPreparingCamera()
        self.thread = VideoThread(self.config.getConfig()['LEFT_CAMERA_NUMBER'],
                                  self.config.getConfig()['RIGHT_CAMERA_NUMBER'])
        self.thread.change_pixmap_signal.connect(self.processing)
        self.thread.start()
        self.isPreparingCamera = False

    # ================= CONTROL PANEL BUTTON EVENTS =====================

    def confirmButtonClicked(self):
        # TODO: TRY-EXCEPTION USING!!!
        # GET TEXTBOX VALUES
        INCREASE_TIME_NORMAL = int(self.Option_INC_TIME_NORMAL_Input.text())
        INCREASE_TIME_SPECIAL = int(self.Option_INC_TIME_SPECIAL_Input.text())
        CROSSWALK_TIME = int(self.Option_TIME_CROSSWALK_GREEN_Input.text())
        CARLANE_TIME = int(self.Option_TIME_CARLANE_GREEN_Input.text())
        CHANGE_TERM = int(self.Option_TIME_CHANGE_TERM_Input.text())

        # SAVE AT JSON
        self.config.setConfig('INCREASE_TIME_NORMAL', INCREASE_TIME_NORMAL)
        self.config.setConfig('INCREASE_TIME_SPECIAL', INCREASE_TIME_SPECIAL)
        self.config.setConfig('CROSSWALK_TIME', CROSSWALK_TIME)
        self.config.setConfig('CARLANE_TIME', CARLANE_TIME)
        self.config.setConfig('CHANGE_TERM', CHANGE_TERM)

        # TODO: CHANGE OPTIONS TO PROGRAM
        self.crosswalkTime = self.config.getConfig()['CROSSWALK_TIME']
        self.carlaneTime = self.config.getConfig()['CARLANE_TIME']
        self.changeTerm = self.config.getConfig()['CHANGE_TERM']

    def Change_CrosswalkTime_Button_Event(self):
        if self.isCarlaneTime is True and self.isCrosswalkTime is False:
            self.timeStack = self.changeTerm
        elif self.isCarlaneTime is False and self.isCrosswalkTime is True:
            self.timeStack = self.crosswalkTime

    def Change_CarTime_Button_Event(self):
        print('Change To Car Time')
        return

    def Left_Camera_Crosswalk_Button_Event(self):
        self.stopCamera()
        self.stopTimer()
        setup = CameraSetup(self.config.getConfig()['LEFT_CAMERA_NUMBER'])
        result = setup.runSetup()
        self.config.setConfig('LEFT_CAMERA_CROSSWALK_POS', result)
        self.refreshCamera()
        self.startTimer()

    def Right_Camera_Crosswalk_Button_Event(self):
        self.stopCamera()
        self.stopTimer()
        setup = CameraSetup(self.config.getConfig()['RIGHT_CAMERA_NUMBER'])
        result = setup.runSetup()
        self.config.setConfig('RIGHT_CAMERA_CROSSWALK_POS', result)
        self.refreshCamera()
        self.startTimer()

    def Left_Camera_Carlane_Button_Event(self):
        self.stopCamera()
        self.stopTimer()
        setup = CameraSetup(self.config.getConfig()['LEFT_CAMERA_NUMBER'])
        result = setup.runSetup()
        self.config.setConfig('LEFT_CAMERA_CARLANE_POS', result)
        self.refreshCamera()
        self.startTimer()

    def Right_Camera_Carlane_Button_Event(self):
        self.stopCamera()
        self.stopTimer()
        setup = CameraSetup(self.config.getConfig()['RIGHT_CAMERA_NUMBER'])
        result = setup.runSetup()
        self.config.setConfig('RIGHT_CAMERA_CARLANE_POS', result)
        self.refreshCamera()
        self.startTimer()

    # ============================= TIMER ===============================

    def TimerMethod(self):
        while self.isTimerRun:
            # 초기화 부분
            if self.isCarlaneTime is False and self.isCrosswalkTime is False:
                self.timeStack = self.carlaneTime
                self.isCarlaneTime = True
                self.isCrosswalkTime = False

                self.carlane_TurnRed_Off()
                self.carlane_TurnGreen_On()

                self.crosswalk_TurnGreen_Off()
                self.crosswalk_TurnRed_On()

            # 타이머가 0초일 경우
            if self.timeStack == 0:
                self.carlane_TurnYellow_Off()
                # 차량신호 시간이 끝났을 경우
                if self.isCarlaneTime is True and self.isCrosswalkTime is False:

                    self.carlane_TurnRed_On()
                    self.carlane_TurnGreen_Off()

                    self.crosswalk_TurnGreen_On()
                    self.crosswalk_TurnRed_Off()

                    self.timeStack = self.crosswalkTime
                    self.isCarlaneTime = False
                    self.isCrosswalkTime = True

                # 횡단보도 시간이 끝났을 경우
                elif self.isCarlaneTime is False and self.isCrosswalkTime is True:

                    self.carlane_TurnRed_Off()
                    self.carlane_TurnGreen_On()

                    self.crosswalk_TurnGreen_Off()
                    self.crosswalk_TurnRed_On()

                    self.timeStack = self.carlaneTime
                    self.isCarlaneTime = True
                    self.isCrosswalkTime = False

            # changeTerm 내의 시간이라면 노란불 켜기
            if 0 < self.timeStack <= self.changeTerm and \
                    self.isCrosswalkTime is False and self.isCarlaneTime is True:
                self.carlane_TurnRed_Off()
                self.carlane_TurnYellow_On()
                self.carlane_TurnGreen_Off()

            # 타이머 감소 및 시간 표시 변경
            self.timeStack -= 1
            self.changeTimer(self.timeStack)
            time.sleep(1)

        # 타이머 종료 처리
        self.isCrosswalkTime = False
        self.isCarlaneTime = False

        self.carlane_TurnRed_Off()
        self.carlane_TurnYellow_Off()
        self.carlane_TurnGreen_Off()

        self.crosswalk_TurnRed_Off()
        self.crosswalk_TurnGreen_Off()

    def stopTimer(self):
        self.isTimerRun = False
        self.TimerLabel.setText('X')

    def startTimer(self):
        if self.timerThread.is_alive() is True:
            return
        self.timerThread = threading.Thread(target=self.TimerMethod)
        self.isTimerRun = True
        self.timerThread.start()

    def changeTimer(self, num):
        self.TimerLabel.setText(str(num + 1))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    app.exec_()
