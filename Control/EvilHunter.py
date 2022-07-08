import os
import numpy as np
import cv2
import copy
from threading import Thread
import time
from Data import ShareInfo as shareinfo


class EvilHunter:
    def __init__(self,  game_index, Device_Name="", Sample_Path=""):
        #print("in EvilHunter __init__ game_index:", game_index)
        self.GAME_INDEX = game_index
        self.ScreenShot = None

        self.game_screenshot_thread_terminate = False
        self.AD_Btn_count = 0
        self.Sample_Image = dict()
        self.Close_AD_Position = [0, 0]
        self.Fire_center_position = [0, 0]
        self.AD_monster_center_position = [0, 0]
        self.Treasure_Chest_Center_Position = [0, 0]
        self.L_hunter_number_termination_condition = 0
        self.L_berserker_number_termination_condition = 0
        self.berserker_list = []
        self.L_level_list = []
        self.H_level_list = []
        self.S_level_list = []
        self.berserker_count = 0
        self.L_level_count = 0
        self.H_level_count = 0
        self.S_level_count = 0
        self.L_level_berserker_count = 0
        self.H_level_berserker_count = 0
        self.S_level_berserker_count = 0


    class GUI_Coordinate:
        AD_BTN = [620, 1000]
        BOSS_BTN = [640, 200]
        TREASURECHEST_BTN = [565, 1030]
        PLAY_AD_BTN = [250, 770]

    def Keep_Game_ScreenShot(self,file_name):
        th = Thread(target=self.Keep_Game_ScreenShot_fn,args=[file_name])
        th.start()

    def Keep_Game_ScreenShot_fn(self, file_name):
        while self.game_screenshot_thread_terminate == False:
            shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
            self.ADB.screen_capture(device_name=self.ADB.Device_Name, file_name=file_name)
            self.ScreenShot = cv2.imread(self.ADB.Device_Name.split(":")[1] + file_name)
            shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
            time.sleep(10)

    def __reset_hunter_info__(self):
        self.berserker_list = []
        self.L_level_list = []
        self.H_level_list = []
        self.S_level_list = []
        self.berserker_count = 0
        self.L_level_count = 0
        self.H_level_count = 0
        self.S_level_count = 0
        self.L_level_berserker_count = 0
        self.H_level_berserker_count = 0
        self.S_level_berserker_count = 0

    def __declare__(self, adb, Device_Name, Sample_Path):
        #print("in EvilHunter __declare__")
        #self.ADB = adb.ADB(Device_Name=Device_Name,Screen_Size=[900,1600])
        self.ADB = adb;
        self.ADB.Set_ADB_Info(Device_Name=Device_Name,Screen_Size=[900,1600])
        self.Sample_Image = dict()
        #導入範例檔案
        self.Import_Sample_Image(Sample_Path)
        # 啟動截圖線程
        #self.Keep_Game_ScreenShot(file_name='_screen.png')

    def Import_Sample_Image(self,Path):
        if os.path.isdir(Path) == False:
            print("範例圖片資料夾不存在")
            return 0
        File_List = os.listdir(Path)
        imageCount = 0;
        for File_Name in File_List:
            File_Index = File_Name.replace(".png","")
            self.Sample_Image[File_Index] = cv2.imread(Path+"/"+ File_Name)
            imageCount+=1;
        print("範例圖片導入成功, 共", imageCount, "張")

    def match_BOSS(self):
        c, w, h = self.Sample_Image['BOSS'].shape[::-1]
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        Boss_Btn_res = cv2.matchTemplate(self.ScreenShot, self.Sample_Image['BOSS'], cv2.TM_CCOEFF_NORMED)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        threshold = 0.9
        boss_res_loc = np.where(Boss_Btn_res >= threshold)
        self.boss_count = len(boss_res_loc[0])
        #for pt in zip(*boss_res_loc[::-1]):
        #    cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
        #cv2.imwrite('debug_match_BOSS.png', self.ScreenShot)

    def match_Treasure_Chest_Btn(self):
        c, w, h = self.Sample_Image['TreasureChestBtn'].shape[::-1]
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        Treasure_Chest_Btn_res = cv2.matchTemplate(self.ScreenShot, self.Sample_Image['TreasureChestBtn'], cv2.TM_CCOEFF_NORMED)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        threshold = 0.9
        Treasure_Chest_Btn_res_loc = np.where(Treasure_Chest_Btn_res >= threshold)
        self.Treasure_Chest_Btn_count = len(Treasure_Chest_Btn_res_loc[0])
        #for pt in zip(*Treasure_Chest_Btn_res_loc[::-1]):
        #    cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
        #cv2.imwrite('debug_match_Treasure_Chest_Btn.png', self.ScreenShot)

    def match_Treasure_Chest(self):
        source_img = cv2.imread(self.ADB.Device_Name.split(":")[1] + '_screenfortreasurechest.png')
        c, w, h = self.Sample_Image['TreasureChest'].shape[::-1]
        Treasure_Chest_res = cv2.matchTemplate(source_img, self.Sample_Image['TreasureChest'], cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        Treasure_Chest_res_loc = np.where(Treasure_Chest_res >= threshold)
        self.Treasure_Chest_count = len(Treasure_Chest_res_loc[0])

        for pt in zip(*Treasure_Chest_res_loc[::-1]):
            cv2.rectangle(source_img, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
            self.Treasure_Chest_Center_Position[0] = int(pt[0] + w / 2)
            self.Treasure_Chest_Center_Position[1] = int(pt[1] + h / 2)
        cv2.imwrite('debug_match_Treasure_Chest.png', source_img)

    def match_Close_AD(self):
        c, w, h = self.Sample_Image['CloseAD-1'].shape[::-1]
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        gray_screenshot_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2GRAY)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        gray_close_img = cv2.cvtColor(self.Sample_Image['CloseAD-1'], cv2.COLOR_BGR2GRAY)

        Close_AD_res = cv2.matchTemplate(gray_screenshot_img, gray_close_img, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        Close_AD_res_loc = np.where(Close_AD_res >= threshold)
        self.Close_AD_count = len(Close_AD_res_loc[0])

        if self.Close_AD_count is 0:
            gray_close_img = cv2.cvtColor(self.Sample_Image['CloseAD-2'], cv2.COLOR_BGR2GRAY)
            Close_AD_res = cv2.matchTemplate(gray_screenshot_img, gray_close_img, cv2.TM_CCOEFF_NORMED)
            Close_AD_res_loc = np.where(Close_AD_res >= threshold)
            self.Close_AD_count = len(Close_AD_res_loc[0])

        for pt in zip(*Close_AD_res_loc[::-1]):
            #cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
            self.Close_AD_Position[0] = int(pt[0] + w / 2)
            self.Close_AD_Position[1] = int(pt[1] + h / 2)
        #cv2.imwrite('debug_match_Close_AD.png', self.ScreenShot)

    def match_Fire(self):
        source_image = self.ADB.screen_capture_to_stream(device_name=self.ADB.Device_Name)

        cv2.imshow('source_image', source_image)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        #source_img = cv2.imread('screen1.png')
        # AD_Monster_img = cv2.imread('./Data/Sample_img/ADMonster.png')
        c, w, h = self.Sample_Image['Fire'].shape[::-1]
        '''
        # Background porcess
        hsv_source_img = cv2.cvtColor(self.source_img, cv2.COLOR_BGR2HSV)
        gray_res_source_img = cv2.cvtColor(self.source_img, cv2.COLOR_BGR2GRAY)
        lower_red = np.array([58, 43, 46])
        upper_red = np.array([99, 255, 255])
        source_mask = cv2.inRange(hsv_source_img, lower_red, upper_red)
        mask_source_img = cv2.bitwise_and(gray_res_source_img, gray_res_source_img, mask=source_mask)
        # cv2.namedWindow("hsv_source_img", cv2.WINDOW_NORMAL)
        # cv2.imshow('gray_res_source_img', gray_res_source_img)
        # cv2.imshow('mask', source_mask)
        # cv2.namedWindow("mask_source_img", cv2.WINDOW_NORMAL)
        # cv2.imshow('mask_source_img', mask_source_img)

        # opening_source_img = cv2.morphologyEx(mask_source_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        # opening_source_img = cv2.morphologyEx(opening_source_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        # blur_source_img = cv2.blur(mask_source_img, (3, 5))
        ret, binary_source_image = cv2.threshold(mask_source_img, 70, 255, cv2.THRESH_TOZERO)
        # cv2.imshow('binary_source_image', binary_source_image)
        contours, hierarchy = cv2.findContours(binary_source_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(binary_source_image, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
        # AD_contours = []
        for contour_index in range(len(contours)):
            contour = contours[contour_index]
            contour_area = cv2.contourArea(contour)
            # 处理掉小的轮廓区域，这个区域的大小自己定义。
            if (contour_area < (h / 4 * w / 4) or contour_area > (h * w)):
                contour_filter = []
                contour_filter.append(contour)
                # thickness不为-1时，表示画轮廓线，thickness的值表示线的宽度。
                cv2.drawContours(binary_source_image, contour_filter, -1, (0, 0, 0), thickness=-1)
                # continue
            # AD_contours.append(contour)
        # cv2.drawContours(binary_source_image, AD_contours, -1, (255, 255, 255), thickness=-1)
        # cv2.namedWindow("binary_source_image", cv2.WINDOW_NORMAL)
        # cv2.imshow('binary_source_image', binary_source_image)
        
        # Template porcess
        # blur_berserker_img = cv2.blur(berserker_img, (3, 5))
        # opening_berserker_img = cv2.morphologyEx(berserker_img, cv2.MORPH_OPEN, np.ones((1,1),np.uint8) )
        # opening_berserker_img = cv2.morphologyEx(opening_berserker_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        hsv_Fire_img = cv2.cvtColor(self.Sample_Image['Fire'], cv2.COLOR_BGR2HSV)
        gray_res_Fire_img = cv2.cvtColor(self.Sample_Image['Fire'], cv2.COLOR_BGR2GRAY)
        AD_Fire_mask = cv2.inRange(hsv_Fire_img, lower_red, upper_red)
        mask_Fire_img = cv2.bitwise_and(gray_res_Fire_img, gray_res_Fire_img, mask=AD_Fire_mask)
        binary_Fire_ret, binary_Fire_image = cv2.threshold(mask_Fire_img, 70, 255, cv2.THRESH_TOZERO)
        Fire_contours, Fire_hierarchy = cv2.findContours(binary_Fire_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for Fire_contour_index in range(len(Fire_contours)):
            Fire_contour = Fire_contours[Fire_contour_index]
            Fire_contour_area = cv2.contourArea(Fire_contour)
            # 处理掉小的轮廓区域，这个区域的大小自己定义。
            if (Fire_contour_area < (h / 4 * w / 4) or Fire_contour_area > (h * w)):
                Fire_contour_filter = []
                Fire_contour_filter.append(Fire_contour)
                # thickness不为-1时，表示画轮廓线，thickness的值表示线的宽度。
                cv2.drawContours(binary_Fire_image, Fire_contour_filter, -1, (0, 0, 0), thickness=-1)
                # continue
        # cv2.imshow('mask_Fire_img', mask_Fire_img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        '''
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        Fire_match_res = cv2.matchTemplate(self.ScreenShot, self.Sample_Image['Fire'], cv2.TM_CCOEFF_NORMED)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        threshold = 0.7
        Fire_match_res_loc = np.where(Fire_match_res >= threshold)
        self.Fire_count = len(Fire_match_res_loc[0])

        for pt in zip(*Fire_match_res_loc[::-1]):
            #cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
            self.Fire_center_position[0] = int(pt[0] + w / 2)
            self.Fire_center_position[1] = int(pt[1] + h / 2)
        #print(self.AD_monster_position)
        #cv2.imwrite('debug_match_Fire.png', self.ScreenShot)

    def match_AD_Btn(self):
        #source_img = cv2.imread('screen1.png')
        #hsv_source_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2HSV)
        #gray_res_source_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2GRAY)
        #lower_red = np.array([156, 43, 46])
        #upper_red = np.array([180, 255, 255])
        #mask = cv2.inRange(hsv_source_img, lower_red, upper_red)
        #mask_source_img = cv2.bitwise_and(gray_res_source_img, gray_res_source_img, mask=mask)
        #cv2.namedWindow("hsv_source_img", cv2.WINDOW_NORMAL)
        #cv2.imshow('hsv_source_img', hsv_source_img)
        #cv2.imshow('mask', mask)
        #cv2.namedWindow("mask_source_img", cv2.WINDOW_NORMAL)
        #cv2.imshow('mask_source_img', mask_source_img)

        #AD_Btn_img = cv2.imread('./Data/Sample_img/ADBtn.png', 0)
        # blur_berserker_img = cv2.blur(berserker_img, (3, 5))
        # opening_berserker_img = cv2.morphologyEx(berserker_img, cv2.MORPH_OPEN, np.ones((1,1),np.uint8) )
        # opening_berserker_img = cv2.morphologyEx(opening_berserker_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        #binary_AD_ret, binary_AD_image = cv2.threshold(cv2.cvtColor(self.Sample_Image['ADBtn'], cv2.COLOR_BGR2GRAY), 240, 255, cv2.THRESH_TOZERO_INV)
        #c, w, h = self.Sample_Image['ADBtn'].shape[::-1]
        #cv2.imshow('binary_AD_image', binary_AD_image)

        # opening_source_img = cv2.morphologyEx(mask_source_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        # opening_source_img = cv2.morphologyEx(opening_source_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        # blur_source_img = cv2.blur(mask_source_img, (3, 5))
        #ret, binary_source_image = cv2.threshold(mask_source_img, 100, 255, cv2.THRESH_BINARY)
        #cv2.imshow('binary_source_image', binary_source_image)
        #contours, hierarchy = cv2.findContours(binary_source_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(res_source_img, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
        '''AD_contours = []
        for contour_index in range(len(contours)):
            contour = contours[contour_index]
            contour_area = cv2.contourArea(contour)
            # 处理掉小的轮廓区域，这个区域的大小自己定义。
            if (contour_area < (h / 10 * w / 10) or contour_area > (h * w)):
                contour_filter = []
                contour_filter.append(contour)
                # thickness不为-1时，表示画轮廓线，thickness的值表示线的宽度。
                cv2.drawContours(binary_source_image, contour_filter, -1, (0, 0, 0), thickness=-1)
                continue
            #
            AD_contours.append(contour)
        cv2.drawContours(binary_source_image, AD_contours, -1, (255, 255, 255), thickness=-1)'''

        '''for contour in contours:
            print(cv2.contourArea(contour))
            # if cv2.contourArea(contour) > 300.0 or cv2.contourArea(contour) < 50.0:
            cv2.drawContours(res_source_img, contour, -1, (255, 255, 255), cv2.FILLED)'''
        #cv2.namedWindow("binary_source_image", cv2.WINDOW_NORMAL)
        #cv2.imshow('binary_source_image', binary_source_image)

        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        AD_Btn_res = cv2.matchTemplate(self.ScreenShot, self.Sample_Image['ADBtn'], cv2.TM_CCOEFF_NORMED)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        threshold = 0.9
        AD_Btn_res_loc = np.where(AD_Btn_res >= threshold)

        #for pt in zip(*AD_Btn_res_loc[::-1]):
        #    cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
        #cv2.imwrite('debug_match_AD_Btn.png', self.ScreenShot)
        self.AD_Btn_count = len(AD_Btn_res_loc[0])

    def match_AD_monster(self):
        #source_img = cv2.imread('screen1.png')
        # AD_Monster_img = cv2.imread('./Data/Sample_img/ADMonster.png')
        c, w, h = self.Sample_Image['ADMonster'].shape[::-1]

        # Background porcess
        hsv_source_img = cv2.cvtColor(self.source_img, cv2.COLOR_BGR2HSV)
        gray_res_source_img = cv2.cvtColor(self.source_img, cv2.COLOR_BGR2GRAY)
        lower_red = np.array([28, 43, 46])
        upper_red = np.array([99, 255, 255])
        source_mask = cv2.inRange(hsv_source_img, lower_red, upper_red)
        mask_source_img = cv2.bitwise_and(gray_res_source_img, gray_res_source_img, mask=source_mask)
        #cv2.namedWindow("hsv_source_img", cv2.WINDOW_NORMAL)
        #cv2.imshow('gray_res_source_img', gray_res_source_img)
        #cv2.imshow('mask', source_mask)
        #cv2.namedWindow("mask_source_img", cv2.WINDOW_NORMAL)
        #cv2.imshow('mask_source_img', mask_source_img)

        # opening_source_img = cv2.morphologyEx(mask_source_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        # opening_source_img = cv2.morphologyEx(opening_source_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        # blur_source_img = cv2.blur(mask_source_img, (3, 5))
        ret, binary_source_image = cv2.threshold(mask_source_img, 70, 255, cv2.THRESH_TOZERO)
        # cv2.imshow('binary_source_image', binary_source_image)
        contours, hierarchy = cv2.findContours(binary_source_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(binary_source_image, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
        # AD_contours = []
        for contour_index in range(len(contours)):
            contour = contours[contour_index]
            contour_area = cv2.contourArea(contour)
            # 处理掉小的轮廓区域，这个区域的大小自己定义。
            if (contour_area < (h / 4 * w / 4) or contour_area > (h * w)):
                contour_filter = []
                contour_filter.append(contour)
                # thickness不为-1时，表示画轮廓线，thickness的值表示线的宽度。
                cv2.drawContours(binary_source_image, contour_filter, -1, (0, 0, 0), thickness=-1)
                # continue
            # AD_contours.append(contour)
        # cv2.drawContours(binary_source_image, AD_contours, -1, (255, 255, 255), thickness=-1)

        '''for contour in contours:
            print(cv2.contourArea(contour))
            # if cv2.contourArea(contour) > 300.0 or cv2.contourArea(contour) < 50.0:
            cv2.drawContours(res_source_img, contour, -1, (255, 255, 255), cv2.FILLED)'''
        # cv2.namedWindow("binary_source_image", cv2.WINDOW_NORMAL)
        # cv2.imshow('binary_source_image', binary_source_image)

        # Template porcess
        # blur_berserker_img = cv2.blur(berserker_img, (3, 5))
        # opening_berserker_img = cv2.morphologyEx(berserker_img, cv2.MORPH_OPEN, np.ones((1,1),np.uint8) )
        # opening_berserker_img = cv2.morphologyEx(opening_berserker_img, cv2.MORPH_OPEN, np.ones((1, 1), np.uint8))
        hsv_AD_Monster_img = cv2.cvtColor(self.Sample_Image['ADMonster'], cv2.COLOR_BGR2HSV)
        gray_res_AD_Monster_img = cv2.cvtColor(self.Sample_Image['ADMonster'], cv2.COLOR_BGR2GRAY)
        AD_Monster_mask = cv2.inRange(hsv_AD_Monster_img, lower_red, upper_red)
        mask_AD_Monster_img = cv2.bitwise_and(gray_res_AD_Monster_img, gray_res_AD_Monster_img, mask=AD_Monster_mask)
        binary_Monster_ret, binary_Monster_image = cv2.threshold(mask_AD_Monster_img, 70, 255, cv2.THRESH_TOZERO)
        Monster_contours, Monster_hierarchy = cv2.findContours(binary_Monster_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for Monster_contour_index in range(len(Monster_contours)):
            Monster_contour = Monster_contours[Monster_contour_index]
            Monster_contour_area = cv2.contourArea(Monster_contour)
            # 处理掉小的轮廓区域，这个区域的大小自己定义。
            if (Monster_contour_area < (h / 4 * w / 4) or Monster_contour_area > (h * w)):
                Monster_contour_filter = []
                Monster_contour_filter.append(Monster_contour)
                # thickness不为-1时，表示画轮廓线，thickness的值表示线的宽度。
                cv2.drawContours(binary_Monster_image, Monster_contour_filter, -1, (0, 0, 0), thickness=-1)
                #continue
        #cv2.imshow('binary_Monster_image', binary_Monster_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        AD_Monster_res = cv2.matchTemplate(binary_source_image, binary_Monster_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.6
        AD_Monster_res_loc = np.where(AD_Monster_res >= threshold)
        AD_Monster_count = len(AD_Monster_res_loc[0])

        if AD_Monster_count is 0:
            _Monster_Copy_image = copy.deepcopy(binary_Monster_image)
            for i in range(h):
                for j in range(w):
                    _Monster_Copy_image[i, w - 1 - j] = binary_Monster_image[i, j]  # 水平镜像
            # cv2.imshow('_Monster_Copy_image', _Monster_Copy_image)
            AD_Monster_res = cv2.matchTemplate(binary_source_image, _Monster_Copy_image, cv2.TM_CCOEFF_NORMED)
            threshold = 0.6
            AD_Monster_res_loc = np.where(AD_Monster_res >= threshold)

        for pt in zip(*AD_Monster_res_loc[::-1]):
            #cv2.rectangle(self.source_img, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
            self.AD_monster_center_position[0] = int(pt[0] + w / 2)
            self.AD_monster_center_position[1] = int(pt[1] + h - 10)
        #print(self.AD_monster_position)
        #cv2.imwrite('debug_match_AD_monster.png', self.source_img)

    def match_standby_L_hunter(self):
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        hsv_source_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2HSV)
        gray_res_source_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2GRAY)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        lower_red = np.array([0, 43, 46])
        upper_red = np.array([20, 255, 255])
        mask = cv2.inRange(hsv_source_img, lower_red, upper_red)
        mask_source_img = cv2.bitwise_and(gray_res_source_img, gray_res_source_img, mask=mask)
        ret, binary_source_image = cv2.threshold(mask_source_img, 70, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(binary_source_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        standby_hunter_contours = []
        for contour_index in range(len(contours)):
            contour = contours[contour_index]
            contour_area = cv2.contourArea(contour)
            # 处理掉小的轮廓区域，这个区域的大小自己定义。
            if (contour_area < 10000 ):
                contour_filter = []
                contour_filter.append(contour)
                # thickness不为-1时，表示画轮廓线，thickness的值表示线的宽度。
                cv2.drawContours(binary_source_image, contour_filter, -1, (0, 0, 0), thickness=-1)
                continue
            #
            standby_hunter_contours.append(contour)
        cv2.drawContours(binary_source_image, standby_hunter_contours, -1, (255, 255, 255), thickness=-1)

        final_contours, final_hierarchy = cv2.findContours(binary_source_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        self.L_level_count += len(final_contours)
        for i in range(0, len(final_contours)):
            x, y, w, h = cv2.boundingRect(final_contours[i])
            self.L_level_list.append([x+w/2,y])

    def match_standby_berserker(self):
        c, w, h = self.Sample_Image['StandbyBerserker'].shape[::-1]
        gray_berserker_img = cv2.cvtColor(self.Sample_Image['StandbyBerserker'], cv2.COLOR_BGR2GRAY)
        binary_berserker_ret, binary_berserker_image = cv2.threshold(gray_berserker_img, 70, 255,
                                                                     cv2.THRESH_BINARY)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        hsv_source_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2HSV)
        gray_res_source_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2GRAY)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        lower_red = np.array([170, 63, 66])
        upper_red = np.array([180, 255, 255])
        mask = cv2.inRange(hsv_source_img, lower_red, upper_red)
        mask_source_img = cv2.bitwise_and(gray_res_source_img, gray_res_source_img, mask=mask)
        ret, binary_source_image = cv2.threshold(mask_source_img, 70, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(binary_source_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(res_source_img, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
        berserker_contours = []
        for contour_index in range(len(contours)):
            contour = contours[contour_index]
            contour_area = cv2.contourArea(contour)
            # 处理掉小的轮廓区域，这个区域的大小自己定义。
            if (contour_area < (h / 10 * w / 10) or contour_area > (h * w)):
                contour_filter = []
                contour_filter.append(contour)
                # thickness不为-1时，表示画轮廓线，thickness的值表示线的宽度。
                cv2.drawContours(binary_source_image, contour_filter, -1, (0, 0, 0), thickness=-1)
                continue
            #
            berserker_contours.append(contour)
        cv2.drawContours(binary_source_image, berserker_contours, -1, (255, 255, 255), thickness=-1)

        berserker_res = cv2.matchTemplate(binary_source_image, binary_berserker_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.80
        berserker_res_loc = np.where(berserker_res >= threshold)
        pre_pt = []
        repeat_match = 0
        for pt in zip(*berserker_res_loc[::-1]):
            #cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
            if not pre_pt:
                pre_pt.append(pt)
                self.berserker_list.append(pt)
            else:
                no_repeat = True
                for berserker_pt_index in range(len(pre_pt)):
                    x = pre_pt[berserker_pt_index][0] - pt[0]
                    y = pre_pt[berserker_pt_index][1] - pt[1]
                    if np.sqrt(np.sum(np.square(x) + np.square(y))) < 100:
                        no_repeat = False
                        repeat_match += 1
                        break
                if no_repeat == True:
                    pre_pt.append(pt)
                    self.berserker_list.append(pt)
        #cv2.imwrite('debug_match_berserker.png', self.ScreenShot)
        self.berserker_count += len(berserker_res_loc[0]) - repeat_match

    def match_berserker(self):
        c, w, h = self.Sample_Image['Berserker'].shape[::-1]
        gray_berserker_img = cv2.cvtColor(self.Sample_Image['Berserker'], cv2.COLOR_BGR2GRAY)
        binary_berserker_ret, binary_berserker_image = cv2.threshold(gray_berserker_img, 70, 255,
                                                                     cv2.THRESH_BINARY)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        hsv_source_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2HSV)
        gray_res_source_img = cv2.cvtColor(self.ScreenShot, cv2.COLOR_BGR2GRAY)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        lower_red = np.array([170, 63, 66])
        upper_red = np.array([180, 255, 255])
        mask = cv2.inRange(hsv_source_img, lower_red, upper_red)
        mask_source_img = cv2.bitwise_and(gray_res_source_img, gray_res_source_img, mask=mask)
        ret, binary_source_image = cv2.threshold(mask_source_img, 70, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(binary_source_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.drawContours(res_source_img, contours, -1, (255, 255, 255), thickness=cv2.FILLED)
        berserker_contours = []
        for contour_index in range(len(contours)):
            contour = contours[contour_index]
            contour_area = cv2.contourArea(contour)
            # 处理掉小的轮廓区域，这个区域的大小自己定义。
            if (contour_area < (h / 10 * w / 10) or contour_area > (h * w)):
                contour_filter = []
                contour_filter.append(contour)
                # thickness不为-1时，表示画轮廓线，thickness的值表示线的宽度。
                cv2.drawContours(binary_source_image, contour_filter, -1, (0, 0, 0), thickness=-1)
                continue
            #
            berserker_contours.append(contour)
        cv2.drawContours(binary_source_image, berserker_contours, -1, (255, 255, 255), thickness=-1)
        #cv2.imshow('binary_source_image', binary_source_image)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        berserker_res = cv2.matchTemplate(binary_source_image, binary_berserker_image, cv2.TM_CCOEFF_NORMED)
        threshold = 0.80
        berserker_res_loc = np.where(berserker_res >= threshold)
        pre_pt = []
        repeat_match = 0
        for pt in zip(*berserker_res_loc[::-1]):
            #cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
            if not pre_pt:
                pre_pt.append(pt)
                self.berserker_list.append(pt)
            else:
                no_repeat = True
                for berserker_pt_index in range(len(pre_pt)):
                    x = pre_pt[berserker_pt_index][0] - pt[0]
                    y = pre_pt[berserker_pt_index][1] - pt[1]
                    if np.sqrt(np.sum(np.square(x) + np.square(y))) < 100:
                        no_repeat = False
                        repeat_match += 1
                        break
                if no_repeat == True:
                    pre_pt.append(pt)
                    self.berserker_list.append(pt)
        #cv2.imwrite('debug_match_berserker.png', self.ScreenShot)
        self.berserker_count += len(berserker_res_loc[0]) - repeat_match

    def match_L_level(self):
        #c, w, h = self.Sample_Image['L'].shape[::-1]
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        L_level_res = cv2.matchTemplate(self.ScreenShot, self.Sample_Image['L'], cv2.TM_CCOEFF_NORMED)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        threshold = 0.94
        L_level_res_loc = np.where(L_level_res >= threshold)
        pre_pt = []
        repeat_match = 0
        for pt in zip(*L_level_res_loc[::-1]):
            #cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
            if not pre_pt:
                pre_pt.append(pt)
                self.L_level_list.append(pt)
            else:
                no_repeat = True
                for L_pt_index in range(len(pre_pt)):
                    x = pre_pt[L_pt_index][0] - pt[0]
                    y = pre_pt[L_pt_index][1] - pt[1]
                    if np.sqrt(np.sum(np.square(x) + np.square(y))) < 100:
                        no_repeat = False
                        repeat_match += 1
                        break
                if no_repeat == True:
                    pre_pt.append(pt)
                    self.L_level_list.append(pt)
        self.L_level_count += len(L_level_res_loc[0]) - repeat_match

    def match_H_level(self):
        #c, w, h = self.Sample_Image['H'].shape[::-1]
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        H_level_res = cv2.matchTemplate(self.ScreenShot, self.Sample_Image['H'], cv2.TM_CCOEFF_NORMED)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        threshold = 0.94
        H_level_res_loc = np.where(H_level_res >= threshold)
        pre_pt = []
        repeat_match = 0
        for pt in zip(*H_level_res_loc[::-1]):
            #cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), ( 255, 125, 0), 1)
            if not pre_pt:
                pre_pt.append(pt)
                self.H_level_list.append(pt)
            else:
                no_repeat = True
                for H_pt_index in range(len(pre_pt)):
                    x = pre_pt[H_pt_index][0] - pt[0]
                    y = pre_pt[H_pt_index][1] - pt[1]
                    if np.sqrt(np.sum(np.square(x) + np.square(y))) < 100:
                        no_repeat = False
                        repeat_match += 1
                        break
                if no_repeat == True:
                    pre_pt.append(pt)
                    self.H_level_list.append(pt)
        self.H_level_count = len(H_level_res_loc[0]) - repeat_match

    def match_S_level(self):
        #c, w, h = self.Sample_Image['S'].shape[::-1]
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
        S_level_res = cv2.matchTemplate(self.ScreenShot, self.Sample_Image['S'], cv2.TM_CCOEFF_NORMED)
        shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
        threshold = 0.94
        S_level_res_loc = np.where(S_level_res >= threshold)
        pre_pt = []
        repeat_match = 0
        for pt in zip(*S_level_res_loc[::-1]):
            #cv2.rectangle(self.ScreenShot, pt, (pt[0] + w, pt[1] + h), (255, 125, 0), 1)
            if not pre_pt:
                pre_pt.append(pt)
                self.S_level_list.append(pt)
            else:
                no_repeat = True
                for S_pt_index in range(len(pre_pt)):
                    x = pre_pt[S_pt_index][0] - pt[0]
                    y = pre_pt[S_pt_index][1] - pt[1]
                    if np.sqrt(np.sum(np.square(x) + np.square(y))) < 100:
                        no_repeat = False
                        repeat_match += 1
                        break
                if no_repeat == True:
                    pre_pt.append(pt)
                    self.S_level_list.append(pt)
        self.S_level_count = len(S_level_res_loc[0]) - repeat_match

    def match_L_level_berserker(self):
        #位置比對
        for L_level_index in range(self.L_level_count):
            for berserker_index in range(self.berserker_count):
                x = self.L_level_list[L_level_index][0] - self.berserker_list[berserker_index][0]
                y = self.L_level_list[L_level_index][1] - self.berserker_list[berserker_index][1]
                if np.sqrt(np.sum(np.square(x)+np.square(y))) < 100:
                    self.L_level_berserker_count += 1
                    break

    def match_H_level_berserker(self):
        #位置比對
        for H_level_index in range(self.H_level_count):
            for berserker_index in range(self.berserker_count):
                x = self.H_level_list[H_level_index][0] - self.berserker_list[berserker_index][0]
                y = self.H_level_list[H_level_index][1] - self.berserker_list[berserker_index][1]
                if np.sqrt(np.sum(np.square(x) + np.square(y))) < 100:
                    self.H_level_berserker_count += 1
                    break

    def match_S_level_berserker(self):
        #位置比對
        for S_level_index in range(self.S_level_count):
            for berserker_index in range(self.berserker_count):
                x = self.S_level_list[S_level_index][0] - self.berserker_list[berserker_index][0]
                y = self.S_level_list[S_level_index][1] - self.berserker_list[berserker_index][1]
                #print("S 狂 距離: ", np.sqrt(np.sum(np.square(x)+np.square(y))))
                if np.sqrt(np.sum(np.square(x)+np.square(y))) < 100:
                    self.S_level_berserker_count += 1
                    break

if __name__ == '__main__':
    print("in EvilHunter main")
    #obj = EvilHunter(Device_Name="127.0.0.1:5555",Sample_Path="../Data/Sample_img")

    # while 1:
    #     Has_stat =   obj.Check_Red_Water_Exist()
    #     if Has_stat == 1:
    #         print("有藥水")
    #     else:
    #         print("沒藥水")
    #         obj.Click_System_Btn("F8")
    #     time.sleep(1)

    # obj.Click_System_Btn("Menu_Sign_in")
    # rs = obj.Check_And_Take_Sign_MailBox()

    # if rs == 1:
    #     print("有新訊息哦")
    # else:
    #     print("沒有新訊息哦")

    # obj.Click_System_Btn('Menu')
    # time.sleep(0.2)

    # obj.Import_Sample_Image("../Data/Sample_img")

    # obj.Image_Hash(obj.ADB.ScreenShot)

    # obj.Get_Red_Water_Img()
    #
    # obj.Click_System_Btn('Item_Box')
    # time.sleep(0.2)
    # obj.Click_System_Btn('Pick_up')
    # time.sleep(0.2)
    # obj.Click_System_Btn('Attack')

