import subprocess
import time
import numpy as np
import cv2

class ADB:
    def __init__(self, Device_Name="", Screen_Size=""):
        #print("in adb __init__")
        self.ADB_Path = '.\Tool\\adb.exe'
        self.ffmpeg_Path = '.\Tool\\ffmpeg\\ffmpeg'
        self.Screen_Size = Screen_Size
        self.Device_Name = Device_Name

    def Set_ADB_Info(self, Device_Name, Screen_Size):
        self.Screen_Size = Screen_Size
        self.Device_Name = Device_Name

    def screen_capture(self, device_name=None, file_name='_screen.png'):
        if device_name == None:
            device_name = self.Device_Name
        self.adb_call_wait(device_name, ['shell', 'screencap', '-p', '/sdcard/'+device_name.split(":")[1]+file_name])
        #time.sleep(1)
        self.adb_call_wait(device_name, ['pull', '/sdcard/'+device_name.split(":")[1]+file_name])
        #time.sleep(0.5)
        #self.adb_call_wait(device_name, ['shell', 'rm', '-f','/sdcard/'+device_name.split(":")[1]+file_name])

    def screen_capture_to_stream(self, device_name=None):
        if device_name == None:
            device_name = self.Device_Name
        stream = self.adb_call_wait_and_out(device_name, ['shell', 'screenrecord', '--verbose', '/sdcard/demo/test.mp4'])
        return stream

    def Type(self, data, device_name=None):
        if device_name == None:
            device_name = self.Device_Name
        self.adb_call_wait(device_name, ['shell', 'input', 'text', '\"'+str(data)+'\"'])

    def Touch(self,x,y,device_name=None):
        if device_name == None:
            device_name = self.Device_Name
        x = str(x)
        y = str(y)
        self.adb_call_wait(device_name,['shell','input','tap',x,y])

    def Touch_not_wait(self,x,y,device_name=None):
        if device_name == None:
            device_name = self.Device_Name
        x = str(x)
        y = str(y)
        self.adb_call(device_name,['shell','input','tap',x,y])

    def StartGame(self, device_name=None):
        if device_name == None:
            device_name = self.Device_Name
        self.adb_call(device_name, ['shell', 'am', 'start', '-n', 'com.superplanet.evilhunter/com.google.firebase.MessagingUnityPlayerActivity'])

    def CloseGame(self, device_name=None):
        if device_name == None:
            device_name = self.Device_Name
        self.adb_call(device_name, ['shell', 'am', 'force-stop', 'com.superplanet.evilhunter'])

    def ClearGameData(self, device_name=None):
        if device_name == None:
            device_name = self.Device_Name
        self.adb_call(device_name, ['shell', 'pm', 'clear', 'com.superplanet.evilhunter'])

    def adb_call(self,device_name,detail_list):
        command = [self.ADB_Path,'-s',device_name]
        for order in detail_list:
            command.append(order)
        #print(command)
        subprocess.Popen(command)

    def adb_call_wait(self,device_name,detail_list):
        command = [self.ADB_Path,'-s',device_name]
        for order in detail_list:
            command.append(order)
        #print(command)
        subprocess.call(command)

    def adb_call_wait_and_out(self,device_name,detail_list):
        command = [self.ADB_Path,'-s',device_name]
        for order in detail_list:
            command.append(order)
        print(command)
        stream = subprocess.Popen(command, shell=True)

        ffmpegCmd = [self.ffmpeg_Path, '-ss', '1', '-i', '-', '-qscale:v', '4', '-frames:v', '1', 'output.png']
        print(ffmpegCmd)
        ffmpeg = subprocess.call(ffmpegCmd, stdin=stream.stdout, shell=True)
        print(ffmpeg)

        source_image = cv2.imread('output.png')
        cv2.imshow('output.png', source_image)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return




        ffmpegCmd = [self.ffmpeg_Path, '-i', '-', '-f', 'rawvideo', '-vcodec', 'bmp', '-vf', 'fps=5', '-']
        print(ffmpegCmd)
        ffmpeg= subprocess.Popen(ffmpegCmd, stdin=stream.stdout, stdout=subprocess.PIPE)
        print(ffmpeg.stdout)
        fileSizeBytes = ffmpeg.stdout.read(6)

        print(fileSizeBytes)
        fileSize = 0
        for i in range(4):
            fileSize += fileSizeBytes[i + 2] * 256 ** i
        bmpData = fileSizeBytes + ffmpeg.stdout.read(fileSize - 6)
        source_image = cv2.imdecode(np.fromstring(bmpData, dtype=np.uint8), 1)
        cv2.imshow('source_image', source_image)

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    def adb_devices(self):
        command = [self.ADB_Path, 'devices']
        #print(command)
        adbcallback=subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        adbcallbackString = str(adbcallback, encoding='utf-8')
        #print(String)
        #print(String.count('device\r\n'))
        if adbcallbackString.find("List of devices attached") < 0:  # adb is not working
            return None
        device_count=adbcallbackString.count('device\r\n')
        device_list = []
        for i in range(device_count):
            device_list.append(adbcallbackString.split("\t")[i].split("\r\n")[-1])
        return device_list


if __name__ == '__main__':
    print("in adb main")
    #obj = ADB(Device_Name="127.0.0.1:5555",Screen_Size=[1280,720])
    # obj.Touch(573,460)
    #hawd = obj.Get_Self_Hawd(0)

    # obj.window_capture(hawd,'test.png')
    #obj.Drag(1164,467,1164,400,1164,370)
    # obj.LD_Call()