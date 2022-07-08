from Module import adb
from Control import EvilHunter
from threading import Thread, Timer, Lock
import time
import cv2
import copy
from Data import ShareInfo as shareinfo

class GameManager():
    def __init__(self):
        self.GAMER_LIST = []
        self.ADB = adb.ADB()

    def __Get_Devices__(self):
        devices_list = self.ADB.adb_devices()
        for device_index in range(len(devices_list)):
            shareinfo.SCREENSHOT_MUTEX_LIST.append(Lock())
        return devices_list


class Gamer():
    def __init__(self, game_index):
        #print("in Gamer __init__ game_index:", game_index)
        self.GAME_INDEX = game_index
        self.thread_terminate = False;
        self.village_head_name = 'Inheritor'
        self.hitBOSS = False
        self.hitBOSSsuceess = False
        self.game_mode = 0

        self.ADB = adb.ADB()
        self.EvilHunter = EvilHunter.EvilHunter(self.GAME_INDEX)
        #self.EvilHunter = EvilHunter.EvilHunter(Device_Name="127.0.0.1:5555",Sample_Path="./Data/Sample_img")

    def __declare__(self, Device_Name):
        self.EvilHunter.__declare__(self.ADB, Device_Name, "./Data/Sample_img")

    def __hit_boss__(self):
        self.EvilHunter.match_BOSS()
        if self.EvilHunter.boss_count > 0:
            self.hitBOSSsuceess = True
            self.ADB.Touch(self.EvilHunter.GUI_Coordinate.BOSS_BTN[0],
                          self.EvilHunter.GUI_Coordinate.BOSS_BTN[1])  # press boss key

        if self.hitBOSSsuceess is True:
            self.__boss_timer_start__(1500)
            self.hitBOSSsuceess = False
        else:
            self.__boss_timer_start__(30)

    def __catch_treasure_chest__(self):
        self.EvilHunter.match_Treasure_Chest_Btn()
        if self.EvilHunter.Treasure_Chest_Btn_count > 0:
            self.ADB.Touch(self.EvilHunter.GUI_Coordinate.TREASURECHEST_BTN[0],
                           self.EvilHunter.GUI_Coordinate.TREASURECHEST_BTN[1])  # press treasure chest btn
            time.sleep(1)
            self.ADB.screen_capture(self.ADB.Device_Name, '_screenfortreasurechest.png')
            self.EvilHunter.match_Treasure_Chest()
            if self.EvilHunter.Treasure_Chest_count > 0:
                debug_match_Treasure_Chest_img = cv2.imread('debug_match_Treasure_Chest.png')
                cv2.circle(debug_match_Treasure_Chest_img,
                           (self.EvilHunter.Treasure_Chest_Center_Position[0],
                            self.EvilHunter.Treasure_Chest_Center_Position[1]), 5,
                           (0, 0, 255), -1)
                cv2.imwrite('debug_match_Treasure_Chest.png', debug_match_Treasure_Chest_img)
                self.ADB.Touch(self.EvilHunter.Treasure_Chest_Center_Position[0],
                              self.EvilHunter.Treasure_Chest_Center_Position[1])
                time.sleep(1)
                self.ADB.Touch(self.EvilHunter.GUI_Coordinate.PLAY_AD_BTN[0],
                               self.EvilHunter.GUI_Coordinate.PLAY_AD_BTN[1])  # press ad play
                time.sleep(30)
                self.EvilHunter.match_Close_AD()
                self.ADB.Touch(self.EvilHunter.Close_AD_Position[0],
                               self.EvilHunter.Close_AD_Position[1])
                debug_match_Close_AD_img = cv2.imread('debug_match_Close_AD.png')
                cv2.circle(debug_match_Close_AD_img,
                           (self.EvilHunter.Close_AD_Position[0],
                            self.EvilHunter.Close_AD_Position[1]), 5,
                           (0, 0, 255), -1)
                cv2.imwrite('debug_match_Close_AD.png', debug_match_Close_AD_img)
        self.__treasure_chest_timer_start__(30)

    def __boss_timer_start__(self, interval=1):
        self.boss_timer = Timer(interval, self.__hit_boss__)
        self.boss_timer.start()

    def __treasure_chest_timer_start__(self, interval=1):
        self.treasure_chest_timer = Timer(interval, self.__catch_treasure_chest__)
        self.treasure_chest_timer.start()

    def __start_normal__(self):
        th = Thread(target=self.__normal_run__)
        th.start()

    def __start_reroll__(self):
        th = Thread(target=self.__reroll_run__)
        th.start()

    def __normal_run__(self):
        self.__boss_timer_start__()
        time.sleep(3)
        self.__treasure_chest_timer_start__()

    def __reroll_run__(self):
        Retry_count = 1
        while (self.EvilHunter.L_level_count < self.EvilHunter.L_hunter_number_termination_condition or self.EvilHunter.L_level_berserker_count < self.EvilHunter.L_berserker_number_termination_condition) and self.thread_terminate == False :
            self.EvilHunter.__reset_hunter_info__()
            self.ADB.CloseGame()
            time.sleep(0.5)
            self.ADB.ClearGameData()
            time.sleep(0.5)
            self.ADB.StartGame()
            time.sleep(18)
            self.ADB.Touch(650, 40)  # 點擊"略過"
            time.sleep(6)
            self.ADB.Touch(333, 1090)  # 任意鍵開始遊戲
            time.sleep(3)
            self.ADB.Touch(350, 580)  # 點擊輸入攔
            time.sleep(1)
            self.ADB.Type(self.village_head_name)  # 輸入ID: Geralt z Rivii 'Gwimbred'
            time.sleep(1)
            self.ADB.Touch(350, 700)  # 任意鍵離開輸入攔
            time.sleep(1)
            self.ADB.Touch(350, 700)  # 點擊"開始遊戲"
            time.sleep(25)
            self.ADB.Touch(540, 90)  # 按郵件
            time.sleep(2)
            self.ADB.Touch(240, 1020)  # 按領取
            time.sleep(6)
            self.ADB.Touch(480, 1020)  # 關閉郵件
            time.sleep(1)
            self.ADB.Touch(500, 1220)  # 按倉庫
            time.sleep(1)
            self.ADB.Touch(500, 650)  # 選擇"特殊"
            time.sleep(1)
            self.ADB.Touch(80, 760)  # 選擇第一格物品
            time.sleep(1)
            self.ADB.Touch(200, 820)  # 使用全部
            time.sleep(2)
            self.ADB.Touch(320, 820)  # 關閉結果
            time.sleep(2)
            self.ADB.Touch(80, 760)  # 選擇第一格物品
            time.sleep(1)
            self.ADB.Touch(200, 820)  # 使用全部
            time.sleep(2)
            self.ADB.Touch(320, 820)  # 關閉結果
            time.sleep(2)
            #判斷待雞所獵人
            shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
            self.ADB.screen_capture(self.ADB.Device_Name, '_screen.png')
            time.sleep(1)
            self.EvilHunter.ScreenShot = cv2.imread(self.ADB.Device_Name.split(":")[1] + '_screen.png')
            shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()
            self.EvilHunter.match_standby_L_hunter()
            self.EvilHunter.match_standby_berserker()
            time.sleep(1)
            self.ADB.Touch(450, 1010)  # 關閉待機所
            time.sleep(1)
            self.ADB.Touch(360, 1222)  # 按獵人
            time.sleep(1)

            shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].acquire()
            self.ADB.screen_capture(self.ADB.Device_Name, '_screen.png')
            time.sleep(1)
            self.EvilHunter.ScreenShot = cv2.imread(self.ADB.Device_Name.split(":")[1]+'_screen.png')
            shareinfo.SCREENSHOT_MUTEX_LIST[self.GAME_INDEX].release()

            self.EvilHunter.match_L_level()
            self.EvilHunter.match_H_level()
            self.EvilHunter.match_S_level()
            self.EvilHunter.match_berserker()
            self.EvilHunter.match_L_level_berserker()
            self.EvilHunter.match_H_level_berserker()
            self.EvilHunter.match_S_level_berserker()

            print("模擬器:[",self.ADB.Device_Name,"]: ","第", Retry_count, "場")
            print(self.EvilHunter.L_level_count, " 隻 'L' 獵人", )
            #if obj.L_level_count is not 0:
            #    print("位置在: ", obj.L_level_list)
            print(self.EvilHunter.H_level_count, " 隻 'H' 獵人", )
            #if obj.H_level_count is not 0:
            #    print("位置在: ", obj.H_level_list)
            print(self.EvilHunter.S_level_count, " 隻 'S' 獵人", )
            #if obj.S_level_count is not 0:
            #    print("位置在: ", obj.S_level_list)
            print(self.EvilHunter.berserker_count, " 隻狂戰士 ")
            print("L - ", self.EvilHunter.L_level_berserker_count)
            print("H - ", self.EvilHunter.H_level_berserker_count)
            print("S - ", self.EvilHunter.S_level_berserker_count)
            # if obj.berserker_count is not 0:
            #    print("位置在: ", obj.berserker_list)
            Retry_count = Retry_count + 1
            time.sleep(2)
        print("達成終止條件: L 獵人: ", self.EvilHunter.L_level_count, "L 狂戰士: ", self.EvilHunter.L_level_berserker_count)


if __name__ == "__main__":
    '''
    manager = GameManager()
    device_list = manager.__Get_Devices__()
    print('請輸入以下要控制的模擬器號碼或是 0 離開程式')
    for index in range(len(device_list)):
        print(index + 1, " ", device_list[index])

    device_index = int(input()) - 1
    while device_index is not -1:
        gamer = Gamer(len(manager.GAMER_LIST))
        print('請選擇')
        print('1. 刷首抽 [警告: 此選項將刪除現有遊戲資料，請謹慎選擇]')
        print('2. 自動打王及開寶箱')
        game_mode = int(input())
        while game_mode is 1:
            print('選擇 --> 1. 刷首抽 [警告: 此選項將刪除現有遊戲資料，請謹慎選擇]')
            print('將清除遊戲資料，確定嗎 Y/N')
            double_check = input()
            if double_check == 'Y' or double_check == 'y':
                break
            print('請選擇')
            print('1. 刷首抽 [警告: 此選項將刪除現有遊戲資料，請謹慎選擇]')
            print('2. 自動打王及開寶箱')
            game_mode = int(input())
        gamer.game_mode = game_mode

        if gamer.game_mode is 1:
            print('終止條件: L 獵人數量: 0 - 6')
            L_hunter_number = int(input())
            while L_hunter_number > 6 or L_hunter_number < 0:
                print('終止條件: L 獵人數量: 0 - 6')
                L_hunter_number = int(input())
            gamer.EvilHunter.L_hunter_number_termination_condition = L_hunter_number
            print('終止條件: L 獵人中需要 狂戰士 數量: 0 - ',L_hunter_number )
            L_berserker_number = int(input())
            while L_berserker_number > L_hunter_number or L_berserker_number < 0:
                print('終止條件: L 獵人數量: 0 - ', L_hunter_number)
                L_berserker_number = int(input())
            gamer.EvilHunter.L_berserker_number_termination_condition = L_berserker_number
            print('是否指定ID Y/N')
            self_naming = input()
            if self_naming == 'Y' or self_naming == 'y':
                print('請輸入 ID (限10個英文字母)')
                name = input()
                gamer.village_head_name = name

            print(device_list[device_index], ' 刷首抽模式啟動...')
            gamer.__declare__(device_list[device_index])
            gamer_record = copy.deepcopy(gamer)
            manager.GAMER_LIST.append(gamer_record)

            manager.GAMER_LIST[len(manager.GAMER_LIST)-1].EvilHunter.Keep_Game_ScreenShot(file_name='_screen.png')
            while manager.GAMER_LIST[len(manager.GAMER_LIST)-1].EvilHunter.ScreenShot is None:
                print("等待…")
                time.sleep(1)
            manager.GAMER_LIST[len(manager.GAMER_LIST)-1].__start_reroll__()

        elif gamer.game_mode is 2:
            print(device_list[device_index], ' 打王模式啟動...')
            gamer.__declare__(device_list[device_index])
            while gamer.EvilHunter.ScreenShot is None:
                print("等待…")
                time.sleep(1)
            gamer_record = copy.deepcopy(gamer)
            manager.GAMER_LIST.append(gamer_record)
            gamer.__start_normal__()

        device_list.remove(device_list[device_index])
        device_conut = len(device_list)
        if device_conut is 0:
            print('已無可選擇的模擬器，可輸入 0 離開程式')
        else:
            print('請繼續輸入要控制的模擬器號碼或是 0 離開程式')
        for index in range(len(device_list)):
            print(index + 1, " ", device_list[index])
        device_index = int(input()) - 1
        '''



    # test code
    manager = GameManager()
    device_list = manager.__Get_Devices__()
    for index in range(len(device_list)):
        print(index + 1, " ", device_list[index])
    obj = Gamer(0)
    obj.__declare__(device_list[0])
    #obj.EvilHunter.Keep_Game_ScreenShot(file_name='_screen.png')
    #while obj.EvilHunter.ScreenShot is None:
    #    print("等待…")
    #    time.sleep(1)
    #obj.ADB.screen_capture(obj.ADB.Device_Name, 'screen1.png')
    #time.sleep(0.5)
    #obj.EvilHunter.ScreenShot = cv2.imread(obj.ADB.Device_Name.split(":")[1] + '_screen.png')
    ##obj.EvilHunter.ScreenShot = cv2.imread('62026_screen.png')

    #obj.__start_normal__()
    obj.EvilHunter.match_Fire()
    ##obj.EvilHunter.match_standby_L_hunter()
    ##print(obj.EvilHunter.L_level_count)
    ##obj.EvilHunter.match_standby_berserker()
    ##print(obj.EvilHunter.berserker_count)

    '''obj.EvilHunter.match_Fire()
    if obj.EvilHunter.Fire_count > 0:
        print('touch key')
        interval = 0
        obj.ADB.Touch(obj.EvilHunter.Fire_center_position[0],
                               obj.EvilHunter.Fire_center_position[1])
        cv2.circle(obj.EvilHunter.source_img,
                   (obj.EvilHunter.Fire_center_position[0], obj.EvilHunter.Fire_center_position[1]), 5,
                   (0, 0, 255), -1)
        cv2.imwrite('FireRes.png', obj.EvilHunter.source_img)'''

    '''
    # TEST press AD : pending
    obj.EvilHunter.match_AD_Btn()
    if obj.EvilHunter.AD_Btn_count > 0:
        obj.ADB.Touch(620, 1000)   # press AD key
        #time.sleep(0.1)
        obj.ADB.screen_capture(obj.ADB.Device_Name, 'screen1.png')
        #time.sleep(0.1)
        obj.EvilHunter.source_img = cv2.imread(obj.ADB.Device_Name.split(":")[1] + 'screen1.png')
        obj.EvilHunter.match_AD_monster()
        if obj.EvilHunter.AD_monster_center_position is not None:
            print('touch key')
            interval = 0
            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0], obj.EvilHunter.AD_monster_center_position[1])

            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0] + interval,
                          obj.EvilHunter.AD_monster_center_position[1])

            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0] + interval,
                          obj.EvilHunter.AD_monster_center_position[1] + interval)

            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0] ,
                          obj.EvilHunter.AD_monster_center_position[1] + interval)

            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0] - interval,
                          obj.EvilHunter.AD_monster_center_position[1] )

            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0] - interval,
                          obj.EvilHunter.AD_monster_center_position[1] - interval)

            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0],
                          obj.EvilHunter.AD_monster_center_position[1] - interval)

            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0] + interval,
                          obj.EvilHunter.AD_monster_center_position[1] - interval)

            obj.ADB.Touch_not_wait(obj.EvilHunter.AD_monster_center_position[0] - interval,
                          obj.EvilHunter.AD_monster_center_position[1] + interval)
            print('touch key end')
            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0], obj.EvilHunter.AD_monster_center_position[1]), 5, (0, 0, 255), -1)

            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0] + interval,
                          obj.EvilHunter.AD_monster_center_position[1]), 5, (0, 0, 255), -1)

            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0] + interval,
                          obj.EvilHunter.AD_monster_center_position[1] + interval), 5, (0, 0, 255), -1)

            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0],
                          obj.EvilHunter.AD_monster_center_position[1] + interval), 5, (0, 0, 255), -1)

            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0] - interval,
                          obj.EvilHunter.AD_monster_center_position[1]), 5, (0, 0, 255), -1)

            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0] - interval,
                          obj.EvilHunter.AD_monster_center_position[1] - interval), 5, (0, 0, 255), -1)

            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0],
                          obj.EvilHunter.AD_monster_center_position[1] - interval), 5, (0, 0, 255), -1)

            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0] + interval,
                          obj.EvilHunter.AD_monster_center_position[1] - interval), 5, (0, 0, 255), -1)

            cv2.circle(obj.EvilHunter.source_img, (obj.EvilHunter.AD_monster_center_position[0] - interval,
                          obj.EvilHunter.AD_monster_center_position[1] + interval), 5, (0, 0, 255), -1)
            cv2.imwrite('AD_Monster_res.png', obj.EvilHunter.source_img)
            obj.ADB.Touch(260, 860)  # press start AD
    '''
            #print("Touch AD: ",obj.EvilHunter.AD_monster_center_position)
