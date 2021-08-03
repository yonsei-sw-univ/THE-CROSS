import json
import os

PATH = "config.json"

# ===== SETTING INITIAL CONFIG VALUES =====#

INCREASE_TIME_DEFAULT = 5
INCREASE_TIME_SPECIAL = 8

LEFT_CAMERA_NUMBER = 0
RIGHT_CAMERA_NUMBER = -1

CROSSWALK_TIME = 10
CARLANE_TIME = 100
CHANGE_TERM = 5

LEFT_CAMERA_CROSSWALK_POS = [[0, 0], [0, 0], [0, 0], [0, 0]]
RIGHT_CAMERA_CROSSWALK_POS = [[0, 0], [0, 0], [0, 0], [0, 0]]
LEFT_CAMERA_CARLANE_POS = [[0, 0], [0, 0], [0, 0], [0, 0]]
RIGHT_CAMERA_CARLANE_POS = [[0, 0], [0, 0], [0, 0], [0, 0]]

optionList = ['INCREASE_TIME_NORMAL', 'INCREASE_TIME_SPECIAL',
              'CROSSWALK_TIME', 'CARLANE_TIME', 'CHANGE_TERM',
              'LEFT_CAMERA_NUMBER', 'RIGHT_CAMERA_NUMBER', 'LEFT_CAMERA_CROSSWALK_POS',
              'RIGHT_CAMERA_CROSSWALK_POS', 'LEFT_CAMERA_CARLANE_POS', 'RIGHT_CAMERA_CARLANE_POS']
optionValues = [INCREASE_TIME_DEFAULT, INCREASE_TIME_SPECIAL,
                CROSSWALK_TIME, CARLANE_TIME, CHANGE_TERM,
                LEFT_CAMERA_NUMBER, RIGHT_CAMERA_NUMBER, LEFT_CAMERA_CROSSWALK_POS,
                RIGHT_CAMERA_CROSSWALK_POS, LEFT_CAMERA_CARLANE_POS, RIGHT_CAMERA_CARLANE_POS]


# =========================================#


class configManager:
    config = dict()

    def __init__(self):
        if os.path.isfile(PATH) is not True:
            fd = open(PATH, 'w', encoding='UTF-8')
            fd.write("{}")
            fd.close()
            self.recoveryOptions()

        with open(PATH, 'r', encoding="UTF-8") as pf:
            self.config = json.load(pf)
            pf.close()

        return

    def setConfig(self, option, value):
        self.config[option] = value
        self.saveJSON()
        return

    def recoveryOptions(self):
        for i in range(len(optionList)):
            self.config[optionList[i]] = optionValues[i]
        self.saveJSON()
        return

    def getConfig(self):
        return self.config

    def saveJSON(self):
        with open(PATH, 'w', encoding='UTF-8') as pf:
            json.dump(self.config, pf, indent='\t', ensure_ascii=False)
        pf.close()
