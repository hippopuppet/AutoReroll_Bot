import os, platform, time
# import win32gui, win32ui, win32con, win32api
# import imagehash
import cv2
import numpy as np
import subprocess
from threading import Thread


ADB_Path = "../tools/adb.exe"

def Touch(x,y):
    command = ('../tools/adb.exe -s 127.0.0.1:62026 shell input tap '+ str(x) + ' ' + str(y))
    subprocess.Popen(command)

def Type(data):
    subprocess.Popen('../tools/adb.exe -s 127.0.0.1:62026 shell input text '+ str(data))

# def adb_call():
#     subprocess.Popen()

def StartGame():
    subprocess.Popen('../tools/adb.exe -s 127.0.0.1:62026 shell am start -n com.superplanet.evilhunter/com.google.firebase.MessagingUnityPlayerActivity')

def CloseGame():
    subprocess.Popen('../tools/adb.exe -s 127.0.0.1:62026 shell am force-stop com.superplanet.evilhunter')

def ClearData():
    subprocess.Popen('../tools/adb.exe -s 127.0.0.1:62026 shell pm clear com.superplanet.evilhunter')

def Capture(filename):
    subprocess.Popen('../tools/adb.exe -s 127.0.0.1:62026 shell screencap -p /sdcard/'+str(filename))
    time.sleep(0.5)
    subprocess.Popen('../tools/adb.exe -s 127.0.0.1:62026 pull /sdcard/'+str(filename))

def monitor_screen():
    th = Thread(target=monitor_screen_fn)
    th.start()

def monitor_screen_fn():
    while 1:
        Capture('screen.png')
        time.sleep(0.2)

# monitor_screen()
L_count = 0
Retry_count = 1
while L_count <= 1:
    CloseGame()
    time.sleep(0.5)
    ClearData()
    time.sleep(0.5)
    StartGame()
    time.sleep(18)
    Touch(650,40)             # 點擊"略過"
    time.sleep(6)
    Touch(333,1090)           # 任意鍵開始遊戲
    time.sleep(1)
    Touch(350,580)            # 點擊輸入攔
    time.sleep(1)
    Type('QQ')                # 輸入ID: QQ
    time.sleep(1)
    Touch(350,700)            # 任意鍵離開輸入攔
    time.sleep(1)
    Touch(350,700)            # 點擊"開始遊戲"
    time.sleep(16)
    Touch(540,90)             # 按郵件
    time.sleep(2)
    Touch(240,1020)           # 按領取
    time.sleep(3)
    Touch(480,1020)           # 關閉郵件
    time.sleep(1)
    Touch(500,1220)           # 按倉庫
    time.sleep(1)
    Touch(500,650)            # 選擇"特殊"
    time.sleep(1)
    Touch(80,760)             # 選擇第一格物品
    time.sleep(1)
    Touch(200,820)            # 使用全部
    time.sleep(2)
    Touch(320,820)            # 關閉結果
    time.sleep(1)
    Touch(360,1222)           # 按獵人
    time.sleep(1)
    Capture('screen1.png')
    time.sleep(1)
    source_img = cv2.imread('screen1.png')

    L_img = cv2.imread('L.png')
    H_img = cv2.imread('H.png')
    S_img = cv2.imread('S.png')
    R_img = cv2.imread('R.png')
    N_img = cv2.imread('N.png')
    L_res = cv2.matchTemplate(source_img, L_img, cv2.TM_CCOEFF_NORMED)
    threshold = 0.94
    L_loc = np.where( L_res >= threshold)
    L_count = len(L_loc[0])
    print("第", Retry_count,"場")
    print("L腳色數量 : ", L_count)
    Retry_count= Retry_count + 1
    time.sleep(2)



# idx = 0
# while idx < len(L_loc):
#     print(L_loc[idx])
#     idx += 1
#
# print(idx)


# H_res = cv2.matchTemplate(source_img, H_img, cv2.TM_CCOEFF_NORMED)
# threshold = 0.92
# H_loc = np.where( H_res >= threshold)
# print(H_loc)
#
# S_res = cv2.matchTemplate(source_img, S_img, cv2.TM_CCOEFF_NORMED)
# threshold = 0.92
# S_loc = np.where( S_res >= threshold)
# print(S_loc)
#
# R_res = cv2.matchTemplate(source_img, R_img, cv2.TM_CCOEFF_NORMED)
# threshold = 0.92
# R_loc = np.where( R_res >= threshold)
# print(R_loc)
#
# N_res = cv2.matchTemplate(source_img, N_img, cv2.TM_CCOEFF_NORMED)
# threshold = 0.93
# N_loc = np.where( N_res >= threshold)
# print(N_loc)
