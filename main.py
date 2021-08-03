import sys
import cv2
import FileManager
import DetectPerson
import numpy as np

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QSizePolicy, QPushButton
from PyQt5.QtCore import pyqtSignal, QThread, QEvent, QObject
from PyQt5 import QtGui

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
# AutoMatically Resize The Input Image Size To ( CAMERA_W * CAMERA_H )
def cvImgToQtImg(cvImage, W=150):
    cvImage = resizeCVIMG(cvImage, W)
    pixmap = cvImgToPixmap(cvImage)
    label = QLabel()
    label.setPixmap(pixmap)
    label.resize(pixmap.width(), pixmap.height())
    return label


def resizeCVIMG(cvImage, W=150):
    ratio = W / cvImage.shape[1]
    dim = (W, int(cvImage.shape[0] * ratio))

    # perform the actual resizing of the image
    cvImage = cv2.resize(cvImage, dim, interpolation=cv2.INTER_AREA)

    return cvImage


def cvImgToPixmap(cvImage):
    img = cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB)
    h, w, c = img.shape
    qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
    pixmap = QtGui.QPixmap.fromImage(qImg)
    return pixmap


def draw_area(cvImg, pos_list, dotColor=(255, 0, 0), lineColor=(0, 255, 0)):
    copyList = []
    for i in range(len(pos_list)):
        x = pos_list[i][0]
        y = pos_list[i][1]
        cv2.circle(cvImg, (x, y), 10, dotColor, -1)
        copyList.append([x, y])

    if len(pos_list) == 4:
        x_arg_sort = []
        for i in range(4):
            arg = np.argmax(copyList, axis=0)[0]
            x_arg_sort.append(arg)
            copyList[arg] = [-1, -1]
        x_arg_sort.reverse()

        if pos_list[x_arg_sort[0]][1] > pos_list[x_arg_sort[1]][1]:
            dump = x_arg_sort[0]
            x_arg_sort[0] = x_arg_sort[1]
            x_arg_sort[1] = dump

        if pos_list[x_arg_sort[2]][1] < pos_list[x_arg_sort[3]][1]:
            dump = x_arg_sort[2]
            x_arg_sort[2] = x_arg_sort[3]
            x_arg_sort[3] = dump

        # High-Low_Low_High
        for i in range(4):
            arg = x_arg_sort[i]
            start = pos_list[arg]
            end = pos_list[x_arg_sort[(i + 1) % 4]]
            cv2.line(cvImg, (start[0], start[1]), (end[0], end[1]), lineColor, 5)

    return cvImg


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray)

    def __init__(self, left_camera_num, right_camera_num):
        super().__init__()
        self._run_flag = True
        self.left_camera_num = left_camera_num
        self.right_camera_num = right_camera_num

    def run(self):
        # capture from web cam
        cam_left = cv2.VideoCapture(self.left_camera_num)
        cam_right = cv2.VideoCapture(self.right_camera_num)

        while self._run_flag:
            ret_left, cv_img_left = cam_left.read()
            ret_right, cv_img_right = cam_right.read()

            pos_left = []
            pos_right = []

            if ret_left is False:
                cv_img_left = []
            else:
                cv_img_left, pos_left = DetectPerson.DetectPerson(cv_img_left)

            if ret_right is False:
                cv_img_right = []
            else:
                cv_img_right, pos_right = DetectPerson.DetectPerson(cv_img_right)

            # Convert List => ND_ARRAY Form
            cv_img_left = np.array(cv_img_left)
            cv_img_right = np.array(cv_img_right)
            pos_left = np.array(pos_left)
            pos_right = np.array(pos_right)

            self.change_pixmap_signal.emit(cv_img_left, cv_img_right, pos_left, pos_right)

        # shut down capture system
        cam_left.release()
        cam_right.release()

    def stop(self):
        self._run_flag = False
        self.exit()


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.Option_TIME_CHANGE_TERM_Input = QLineEdit()
        self.Option_TIME_CARLANE_GREEN_Input = QLineEdit()
        self.Option_TIME_CROSSWALK_GREEN_Input = QLineEdit()
        self.Right_Camera_Button = QPushButton()
        self.Left_Camera_Button = QPushButton()
        self.CarLane_Yellow_Button = QPushButton()
        self.CarLane_Green_Button = QPushButton()
        self.CarLane_Red_Button = QPushButton()
        self.Crosswalk_Red_Button = QPushButton()
        self.Crosswalk_Green_Button = QPushButton()
        self.Option_INC_TIME_SPECIAL_Input = QLineEdit()
        self.ConfirmButton = QPushButton()
        self.Timer = QLabel()
        self.Option_INC_TIME_NORMAL_Input = QLineEdit()

        self.config = FileManager.configManager()

        self.setWindowTitle(":: The CROSS :: Smart Traffic Control System")

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

        self.Timer.setFont(QFont(TIMER_FONT, 60))
        self.Timer.setText("0")
        CrosswalkPanel.addStretch(1)
        CrosswalkPanel.addWidget(self.Timer)
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

        self.Crosswalk_Green_Button.setText("횡단보도 초록불로 변경")
        self.Crosswalk_Red_Button.setText("횡단보도 빨간불로 변경")

        self.Crosswalk_Green_Button.clicked.connect(self.Crosswalk_Green_Button_Event)
        self.Crosswalk_Red_Button.clicked.connect(self.Crosswalk_Red_Button_Event)

        self.CarLane_Green_Button.setText("신호등 초록불로 변경")
        self.CarLane_Yellow_Button.setText("신호등 노란불로 변경")
        self.CarLane_Red_Button.setText("신호등 빨간불로 변경")

        self.CarLane_Green_Button.clicked.connect(self.Carlane_Green_Button_Event)
        self.CarLane_Yellow_Button.clicked.connect(self.Carlane_Yellow_Button_Event)
        self.CarLane_Red_Button.clicked.connect(self.Carlane_Red_Button_Event)

        self.Left_Camera_Button.setText("좌측 카메라 횡단보도 영역설정")
        self.Right_Camera_Button.setText("우측 카메라 횡단보도 영역설정")

        self.Left_Camera_Button.clicked.connect(self.Left_Camera_Button_Event)
        self.Right_Camera_Button.clicked.connect(self.Right_Camera_Button_Event)

        Control_Crosswalk_Panel = QHBoxLayout()
        Control_Crosswalk_Panel.addWidget(self.Crosswalk_Red_Button)
        Control_Crosswalk_Panel.addWidget(self.Crosswalk_Green_Button)

        Control_Carlane_Panel = QHBoxLayout()
        Control_Carlane_Panel.addWidget(self.CarLane_Red_Button)
        Control_Carlane_Panel.addWidget(self.CarLane_Yellow_Button)
        Control_Carlane_Panel.addWidget(self.CarLane_Green_Button)

        Control_Camera_Panel = QHBoxLayout()
        Control_Camera_Panel.addWidget(self.Left_Camera_Button)
        Control_Camera_Panel.addWidget(self.Right_Camera_Button)

        ControlPanel.addLayout(Control_Crosswalk_Panel)
        ControlPanel.addLayout(Control_Carlane_Panel)
        ControlPanel.addLayout(Control_Camera_Panel)

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
        self.show()

    #   imgLeft & imgRight must be QtImage Instance
    def processing(self, imgLeft, imgRight, left_pos, right_pos):

        if len(imgLeft) == 0:
            imgLeft = self.CAMERA_NO_SIGNAL_IMG_L
        else:
            CrossArea = self.config.getConfig()['LEFT_CAMERA_CROSSWALK_POS']
            CarLaneArea = self.config.getConfig()['LEFT_CAMERA_CARLANE_POS']
            imgLeft = draw_area(imgLeft, CrossArea)
            imgLeft = draw_area(imgLeft, CarLaneArea, (255, 0, 0), (255, 0, 0))
            imgLeft = cvImgToQtImg(imgLeft, CAMERA_W)

        self.CameraLeft.setPixmap(imgLeft.pixmap())

        if len(imgRight) == 0:
            imgRight = self.CAMERA_NO_SIGNAL_IMG_R
        else:
            CrossArea = self.config.getConfig()['RIGHT_CAMERA_CROSSWALK_POS']
            CarLaneArea = self.config.getConfig()['RIGHT_CAMERA_CARLANE_POS']
            imgRight = draw_area(imgRight, CrossArea)
            imgRight = draw_area(imgRight, CarLaneArea, (255, 0, 0), (255, 0, 0))
            imgRight = cvImgToQtImg(imgRight, CAMERA_W)

        self.CameraRight.setPixmap(imgRight.pixmap())

        if len(left_pos) + len(right_pos) > 0:
            self.crosswalk_TurnGreen_On()
            self.crosswalk_TurnRed_Off()
        else:
            self.crosswalk_TurnRed_On()
            self.crosswalk_TurnGreen_Off()

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

    def carlane_TurnGreen_Off(self):
        self.CarLane_Yellow.setPixmap(self.YELLOW_OFF_IMG.pixmap())

    def stopCamera(self):
        if self.thread.isRunning() is True:
            self.thread.stop()

    def refreshCamera(self):
        self.stopCamera()
        self.thread = VideoThread(self.config.getConfig()['LEFT_CAMERA_NUMBER'],
                                  self.config.getConfig()['RIGHT_CAMERA_NUMBER'])
        self.thread.change_pixmap_signal.connect(self.processing)
        self.thread.start()

    # ================= CONTROL PANEL BUTTON EVENTS =====================

    def confirmButtonClicked(self):
        # TODO: TRY-EXCEPTION USING!!!
        # GET TEXTBOX VALUES
        INCREASE_TIME_NORMAL = int(self.Option_INC_TIME_NORMAL_Input.text())
        INCREASE_TIME_SPECIAL = int(self.Option_INC_TIME_SPECIAL_Input.text())

        # SAVE AT JSON
        self.config.setConfig('INCREASE_TIME_NORMAL', INCREASE_TIME_NORMAL)
        self.config.setConfig('INCREASE_TIME_SPECIAL', INCREASE_TIME_SPECIAL)

        # TODO: CHANGE OPTIONS TO PROGRAM

    def Crosswalk_Green_Button_Event(self):
        print('Crosswalk Green')
        return

    def Crosswalk_Red_Button_Event(self):
        print('Crosswalk Red')
        return

    def Carlane_Green_Button_Event(self):
        print('Carlane Green')
        return

    def Carlane_Yellow_Button_Event(self):
        print('Carlane Yellow')
        return

    def Carlane_Red_Button_Event(self):
        print('Carlane Red')
        return

    def Left_Camera_Button_Event(self):
        self.stopCamera()
        setup = CameraSetup(self.config.getConfig()['LEFT_CAMERA_NUMBER'])
        result = setup.runSetup()
        self.config.setConfig('LEFT_CAMERA_CROSSWALK_POS', result)
        print('left-camera-setting-done')
        self.refreshCamera()
        return

    def Right_Camera_Button_Event(self):
        self.stopCamera()
        setup = CameraSetup(self.config.getConfig()['RIGHT_CAMERA_NUMBER'])
        result = setup.runSetup()
        self.config.setConfig('RIGHT_CAMERA_CROSSWALK_POS', result)
        print('right-camera-setting-done')
        self.refreshCamera()
        return

    # ============================= TIMER ===============================

    def changeTimer(self, time):
        self.Timer.setText(time)


# TODO: MAKE THIS CLASS TO >>> THREAD
class CameraSetup:

    def __init__(self, camera_num):
        super().__init__()
        self.touch_list = []
        self.windowName = 'Camera Setup :: Save & Exit Button is KEY Q'
        self.isRun = True
        self.Camera_Number = camera_num
        self.CAMERA_NO_SIGNAL_IMG = cv2.imread(IMAGE_PATH + "camera_no_signal.png")

    def addXY_inList(self, x, y):
        if len(self.touch_list) >= 4:
            self.touch_list = []
        self.touch_list.append([x, y])

    def clear_List(self):
        self.touch_list = []

    def click_event(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print('x : ', x, ' y : ', y)
            self.addXY_inList(x, y)

    def runSetup(self):

        cv2.namedWindow(self.windowName)
        cv2.setMouseCallback(self.windowName, self.click_event)

        cap = cv2.VideoCapture(self.Camera_Number)

        while self.isRun:
            ret, frame = cap.read()
            if ret is False:
                frame = self.CAMERA_NO_SIGNAL_IMG
            else:
                frame = draw_area(frame, self.touch_list)

            cv2.imshow(self.windowName, frame)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key & 0xFF == ord('Q'):
                self.isRun = False
                cv2.destroyWindow(self.windowName)
                cap.release()
                cv2.waitKey(10)
                return self.touch_list


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    app.exec_()
