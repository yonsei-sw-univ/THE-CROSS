import numpy as np
import cv2
import Detector

from PyQt5.QtCore import QThread, pyqtSignal
from ImageUtils import draw_area

IMAGE_PATH = "Images\\"


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
                cv_img_left, pos_left = Detector.Detector(cv_img_left)

            if ret_right is False:
                cv_img_right = []
            else:
                cv_img_right, pos_right = Detector.Detector(cv_img_right)

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
