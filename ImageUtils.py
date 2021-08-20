import numpy as np
import cv2

from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui


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
        cv2.circle(cvImg, (x, y), 5, dotColor, -1)
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
            cv2.line(cvImg, (start[0], start[1]), (end[0], end[1]), lineColor, 2)

    return cvImg


# spots is Array
# TODO: RESULT IS BOOLEAN ( TOTALLY IS IN AREA )
def isSpotInRect(rectPos, spot):
    if len(spot) == 0:
        return False

    copyList = list(rectPos)
    x_arg_sort = []
    for i in range(4):
        arg = np.argmax(copyList, axis=0)[0]
        x_arg_sort.append(arg)
        copyList[arg] = [-1, -1]
    x_arg_sort.reverse()

    if rectPos[x_arg_sort[0]][1] > rectPos[x_arg_sort[1]][1]:
        dump = x_arg_sort[0]
        x_arg_sort[0] = x_arg_sort[1]
        x_arg_sort[1] = dump

    if rectPos[x_arg_sort[2]][1] < rectPos[x_arg_sort[3]][1]:
        dump = x_arg_sort[2]
        x_arg_sort[2] = x_arg_sort[3]
        x_arg_sort[3] = dump

    p1 = rectPos[x_arg_sort[0]]
    p2 = rectPos[x_arg_sort[1]]
    p3 = rectPos[x_arg_sort[2]]
    p4 = rectPos[x_arg_sort[3]]

    # High Low Low High
    # y = (Ay-By)/(Ax-Bx)*( x - Ax ) + Ay
    for i in range(0, len(spot)):

        try:
            # [xmin, ymax, xmax, ymin]
            target = [(spot[i][0] + spot[i][2]) / 2, (spot[i][1] + spot[i][3]) / 2]

            if p1[0] == p2[0]:
                if not p1[0] < target[0]:
                    continue
            else:
                # linear a > 0
                if (p1[1] - p2[1]) / (p1[0] - p2[0]) > 0:
                    if not ((p1[1] - p2[1]) / (p1[0] - p2[0]) * (target[0] - p1[0]) + p1[1]) < target[1]:
                        continue
                # linear a < 0
                else:
                    if not ((p1[1] - p2[1]) / (p1[0] - p2[0]) * (target[0] - p1[0]) + p1[1]) > target[1]:
                        continue

            if not ((p2[1] - p3[1]) / (p2[0] - p3[0]) * (target[0] - p2[0]) + p2[1]) > target[1]:
                continue

            if p3[0] == p4[0]:
                if not p3[0] > target[0]:
                    continue
            else:
                # linear a > 0
                if (p3[1] - p4[1]) / (p3[0] - p4[0]) > 0:
                    if not ((p3[1] - p4[1]) / (p3[0] - p4[0]) * (target[0] - p3[0]) + p3[1]) > target[1]:
                        continue
                # linear a < 0
                else:
                    if not ((p3[1] - p4[1]) / (p3[0] - p4[0]) * (target[0] - p3[0]) + p3[1]) < target[1]:
                        continue

            if not ((p4[1] - p1[1]) / (p4[0] - p1[0]) * (target[0] - p4[0]) + p4[1]) < target[1]:
                continue

        except Exception as e:
            return False

        return True

    return False
