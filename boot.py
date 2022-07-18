##插件--------------------------------------------------------
from machine import I2C, Pin, ADC, PWM
from sensor import DHT11
import voice_recognition
from gpb import delay
import urandom
import audio_decode
from ble_uart import BleUart
from i2c_lcd import I2cLcd
from lcd_api import LcdApi

##揚聲器
audio_decode.init()

##語音辨識用
voice_recognition.load_database('cmd.bin')
delay(500)
voice_recognition.start(10)

##LCD用
I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(scl='C0', sda='C1', freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

##藍芽連接用
ble = BleUart(0, 115200)
delay(200)
ble.cmd_mode_entry()
ble.cmd_AT()
ble.set_device_name('Ho-Seng')


##元件腳位----------------------------------------------------
vr = ADC(1)
fan = PWM(5, 200, 0)

rgbR = Pin(2, Pin.OUT)
rgbG = Pin(3, Pin.OUT)
rgbB = Pin(4, Pin.OUT)
btnR = Pin(11, Pin.IN)
btnG = Pin(12, Pin.IN)
btnB = Pin(13, Pin.IN)

dht = DHT11(0)

lightSensor = ADC(0)


##全域變數----------------------------------------------------
inGame = 0 ##是否正在遊戲中
timeCounter = 0

currentStageIndex = 1
disconnectedFlag = 0
stageInstruction = ["", "Instuction1", "Instuction2", "Instuction3", "Instuction4", "Instuction5"]  ##關卡說明

stage1SuccessFlag = 0
stage2SuccessFlag = 0
stage3SuccessFlag = 0
stage4SuccessFlag = 0
stage5SuccessFlag = 0

s1TargetFlag = 0
s2ColorList = ["Yellow", "Purple", "Cyan", "White"]
s2Color = ""
s3Target = 0
s4Brightness = 0
s4TargetFlag = 0
s4Target = 0
s5QuestionList = ["cc","cc2"] ##TODO: stage5題目
s5Question = ""


##函式--------------------------------------------------------
def time_ct(t):
    global timeCounter
    timeCounter += 1

def clearLCD1():
    delay(1000)
    lcd.clear()
    delay(500)
def clearLCD2():
    delay(2000)
    lcd.clear()
    delay(500)

def clearLED():
    rgbR.value(0)
    rgbG.value(0)
    rgbB.value(0)  

def bleStageInstructionDisplay(index): ##藍芽: 手機上顯示題目
    global stageInstruction
    if is_ble_connected == True:
        delay(100)
        ble.write("Stage"+ str(index) + ": " + stageInstruction[index])


##起始字樣
def boot():
    lcd.move_to(0,0)
    lcd.putstr("Made by FongShan")
    lcd.move_to(0,1)
    lcd.putstr("New Age Men")
    clearLCD2()

    lcd.move_to(0,0)
    lcd.putstr("Welcome to")
    lcd.move_to(0,1)
    lcd.putstr("Ho-Seng")
    clearLCD2()

    lcd.move_to(0,0)
    lcd.putstr("Waiting For")
    lcd.move_to(0,1)
    lcd.putstr("BLE Connect")


def startGame():
    global inGame

    inGame = 1

    lcd.move_to(0,0)
    lcd.putstr("Game Start!!")
    lcd.move_to(0,1)
    lcd.putstr("Good Luck!")
    clearLCD2()

    lcd.putstr("Stage: 1/5")
    ble.write("-----------Stage 1-----------")
    clearLCD2()

    currentStage()

def currentStage():
    if currentStageIndex == 1:
        stage1Front()
        stage1Display()
        bleStageInstructionDisplay(1)
        stage1()
    elif currentStageIndex == 2:
        stage2Front()
        stage2Display()
        bleStageInstructionDisplay(2)
        stage2()
    elif currentStageIndex == 3:
        stage3Front()
        stage3Display()
        bleStageInstructionDisplay(3)
        stage3()
    elif currentStageIndex == 4:
        stage4Front()
        stage4Display()
        bleStageInstructionDisplay(4)
        stage4()
    elif currentStageIndex == 5:
        stage5Front()
        stage5Display()
        bleStageInstructionDisplay(5)
        stage5()

def nextStage():
    global currentStageIndex
    currentStageIndex += 1

    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("Stage Clear!!")
    clearLCD2()

    lcd.putstr("Next Stage")
    lcd.move_to(0,1)
    lcd.putstr("Stage: " + str(currentStageIndex) + "/5")
    ble.write("-----------Stage " + str(currentStageIndex) +"-----------")
    clearLCD2()
    
    currentStage()

def hint():
    global currentStageIndex
    global s4TargetFlag

    if currentStageIndex == 1:
        ble.write("轉動可變電阻看看?")
    elif currentStageIndex == 2:
        ble.write("按下不同的按鈕看看?")
    elif currentStageIndex == 3:
        ble.write("用手指壓著濕度感測器久一些看看?")
    elif currentStageIndex == 4:
        if s4TargetFlag == 1:
            ble.write("用某樣東西照著光敏電阻看看?")
        else:
            ble.write("用某樣東西蓋著光敏電阻看看?")
    ##else: ##TODO: 看題目是什麼, 給不同提示

def allClear(): ##關卡全破
    global inGame

    inGame = 0

    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("Congratulations!")
    ble.write("------Congratulations!!------")
    lcd.move_to(0,1)

def finishGame(): ##強制結束遊戲
    global inGame

    inGame = 0

    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("Game Over")
    ble.write("----------Game Over----------")
    lcd.move_to(0,1)

def connected():
    global disconnectedFlag

    disconnectedFlag = 0
    
    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("Connected")
    clearLCD2()

    lcd.move_to(0,0)
    lcd.putstr("Wait For Voice")
    lcd.move_to(0,1)
    lcd.putstr("CMD to Start")

def disconnected():
    global disconnectedFlag

    disconnectedFlag = 1
    clearLCD2()
    lcd.move_to(0,0)
    lcd.putstr("Disconnected")


##主要--------------------------------------------------------
def main(): ##遊戲開始與推進用
    global currentStageIndex
    global stage1SuccessFlag
    global stage2SuccessFlag
    global stage3SuccessFlag
    global stage4SuccessFlag
    global stage5SuccessFlag

    if is_ble_connected == True:
        currentStageIndex = 1               ##TODO:Debug時指定起始關卡用
        startGame()
        if stage1SuccessFlag == 1:
            audio_decode.start('correct.mp3')
            nextStage()
        if stage2SuccessFlag == 1:
            audio_decode.start('correct.mp3')
            nextStage()
        if stage3SuccessFlag == 1:
            audio_decode.start('correct.mp3')
            nextStage()
        if stage4SuccessFlag == 1:
            audio_decode.start('correct.mp3')
            nextStage()
        if stage5SuccessFlag == 1:
            audio_decode.start('allClear.mp3')
            allClear()

def init(): ##初始化/重置
    global inGame
    global disconnectedFlag
    global currentStageIndex
    global stageInstruction

    global stage1SuccessFlag
    global stage2SuccessFlag
    global stage3SuccessFlag
    global stage4SuccessFlag
    global stage5SuccessFlag

    global s1TargetFlag
    global s2Color
    global s3Target
    global s4Brightness
    global s4TargetFlag
    global s4Target
    global s5Question

    inGame = 0
    disconnectedFlag = 0
    currentStageIndex = 1
    stageInstruction = ["", "Instuction1", "Instuction2", "Instuction3", "Instuction4", "Instuction5"]  ##關卡說明

    stage1SuccessFlag = 0
    stage2SuccessFlag = 0
    stage3SuccessFlag = 0
    stage4SuccessFlag = 0
    stage5SuccessFlag = 0

    s1TargetFlag = 0
    s2Color = ""
    s3Target = 0
    s4Brightness = 0
    s4TargetFlag = 0
    s4Target = 0
    s5Question = ""

    clearLCD2()


##各關函式----------------------------------------------------

##--- Stage1: 可變電阻控制風扇 ---
def stage1Front():
    global stageInstruction
    global vr
    global s1TargetFlag
    
    fan.duty(int(vr.read()/4))
    if vr.read() > 2001:
        s1TargetFlag = 1  ##讓風扇轉快一點
    if vr.read() < 2000:
        s1TargetFlag = 0  ##讓風扇停

def stage1Display():
    global stageInstruction
    global s1TargetFlag

    lcd.move_to(0,0)
    lcd.putstr("Control the Fan")

    #bleDisplay
    if s1TargetFlag == 1:
        stageInstruction[1] = "讓風扇轉快一點"
    else:
        stageInstruction[1] = "讓風扇停下來"
    
def stage1():
    global stage1SuccessFlag
    global vr
    global s1TargetFlag
    global is_ble_connected

    while True:
        cmd_id = voice_recognition.get_id()
        if inGame == 1:
            if cmd_id == 2: ##結束遊戲
                finishGame()
                break
            if cmd_id == 3: ##請求支援(提示)
                hint()
            if cmd_id == 7: ##重新遊戲
                init()
                main()
                break
        
        cmd = str(ble.read(30), 'utf-8').strip('\0')
        delay(500)
        if cmd == "SYSTEM-ECHO=DISCONNECTED OK\r\n":
            is_ble_connected = False
            disconnected()
            break

        fan.duty(int(vr.read()/4))
        if s1TargetFlag == 1:
            if vr.read() < 100 :
                stage1SuccessFlag = 1
                fan.duty(0)
                break
        else:
            if vr.read() > 3600:
                stage1SuccessFlag = 1
                fan.duty(0)
                break
        delay(200)


##---Stage2: 按鈕控制RGB顏色---
def stage2Front():
    global s2Color
    global s2ColorList
    
    colorPicker = urandom.randint(0, 3)
    s2Color = s2ColorList[colorPicker]
    
def stage2Display():
    global stageInstruction
    global s2Color
    global s2ColorList
    lcd.move_to(0,0)
    lcd.putstr("Change The Light")
    lcd.move_to(0,1)
    lcd.putstr("to " + s2Color)

    ##bleDisplay
    if s2Color == s2ColorList[0]:
        stageInstruction[2] = "讓燈變成黃色"
    elif s2Color == s2ColorList[1]:
        stageInstruction[2] = "讓燈變成紫色"
    elif s2Color == s2ColorList[2]:
        stageInstruction[2] = "讓燈變成青色"
    elif s2Color == s2ColorList[3]:
        stageInstruction[2] = "讓燈變成白色"
    
def stage2(): 
    global stage2SuccessFlag
    global s2Color
    global is_ble_connected

    rgbRIndex = 0
    rgbGIndex = 0
    rgbBIndex = 0

    while True:
        cmd_id = voice_recognition.get_id()
        if inGame == 1:
            if cmd_id == 2: ##結束遊戲
                finishGame()
                break
            if cmd_id == 3: ##請求支援(提示)
                hint()
            if cmd_id == 7: ##重新遊戲
                init()
                main()
                break
        
        cmd = str(ble.read(30), 'utf-8').strip('\0')
        delay(200)
        if cmd == "SYSTEM-ECHO=DISCONNECTED OK\r\n":
            is_ble_connected = False
            disconnected()
            break

        ##按鈕偵測
        if btnR.value() == 1:
            if rgbRIndex == 0:
                rgbRIndex = 1
                delay(200)
            else:
                rgbRIndex = 0
                delay(200)
            rgbR.value(rgbRIndex)
        if btnG.value() == 1:
            if rgbGIndex == 0:
                rgbGIndex = 1
                delay(200)
            else:
                rgbGIndex = 0
                delay(200)
            rgbG.value(rgbGIndex)
        if btnB.value() == 1:
            if rgbBIndex == 0:
                rgbBIndex = 1
                delay(200)
            else:
                rgbBIndex = 0
                delay(200)
            rgbB.value(rgbBIndex)
            
        ##結果判定
        if s2Color == s2ColorList[0]:
            if rgbRIndex == 1 & rgbGIndex == 1:
                stage2SuccessFlag = 1
                delay(1000)
                clearLED()
                break
        elif s2Color == s2ColorList[1]:
            if rgbRIndex == 1 & rgbBIndex == 1:
                stage2SuccessFlag = 1
                delay(1000)
                clearLED()
                break
        elif s2Color == s2ColorList[2]:
            if rgbGIndex == 1 & rgbBIndex == 1:
                stage2SuccessFlag = 1
                delay(1000)
                clearLED()
                break
        elif s2Color == s2ColorList[3]:
            if rgbRIndex == 1 & rgbGIndex == 1 & rgbBIndex == 1:
                stage2SuccessFlag = 1
                delay(1000)
                clearLED()
                break
    

##--- Stage3: 增加濕度 ---
def stage3Front():
    global dht
    global s3Target

    while True:
        humidity = dht.humidity()
        delay(200)
        if humidity >= 5:
            if humidity <= 65:
                break
            else:
                humidity = 60
                break
        else:
            humidity = 60
            break
        
    s3Target = humidity + 5

def stage3Display():
    lcd.move_to(0,0)
    lcd.putstr("Increase the")
    lcd.move_to(0,1)
    lcd.putstr("Humidity")
    stageInstruction[3] = "增加濕度到 " + str(s3Target) + " %"
    
def stage3():
    global dht
    global stage3SuccessFlag
    global is_ble_connected

    while True:
        cmd_id = voice_recognition.get_id()
        if inGame == 1:
            if cmd_id == 2: ##結束遊戲
                finishGame()
                break
            if cmd_id == 3: ##請求支援(提示)
                hint()
            if cmd_id == 7: ##重新遊戲
                init()
                main()
                break

        cmd = str(ble.read(30), 'utf-8').strip('\0')
        delay(500)
        if cmd == "SYSTEM-ECHO=DISCONNECTED OK\r\n":
            is_ble_connected = False
            disconnected()
            break

        humidity = dht.humidity()
        lcd.move_to(11,1)               ##TODO: test, 濕度即時更新
        lcd.putstr(str(humidity) + "%")

        if humidity >= s3Target:
            stage3SuccessFlag = 1
            break
    

##--- Stage4: 光敏電阻 ---
def stage4Front():
    global s4Brightness
    global s4TargetFlag
    global s4Target
    
    while True:
        s4Brightness = lightSensor.read()
        delay(200)
        if s4Brightness > 100:
            break
    s4TargetFlag = urandom.randint(0,1)

    if s4TargetFlag == 1:
        s4Target = s4Brightness - 200 ##越亮, 值越低
    else:
        s4Target = s4Brightness + 300

def stage4Display():
    global s4TargetFlag
    global s4Target

    lcd.move_to(0,0)
    if s4TargetFlag == 1:
        lcd.putstr("Let it Brighter")
        stageInstruction[4] = "讓光敏電阻變得更亮"
    else:
        lcd.putstr("Let it Darker")
        stageInstruction[4] = "讓光敏電阻變得更暗"
    
def stage4():
    global s4Brightness
    global s4TargetFlag
    global s4Target
    global stage4SuccessFlag
    global is_ble_connected

    while True:
        cmd_id = voice_recognition.get_id()
        if inGame == 1:
            if cmd_id == 2: ##結束遊戲
                finishGame()
                break
            if cmd_id == 3: ##請求支援(提示)
                hint()
            if cmd_id == 7: ##重新遊戲
                init()
                main()
                break
        
        cmd = str(ble.read(30), 'utf-8').strip('\0')
        delay(500)
        if cmd == "SYSTEM-ECHO=DISCONNECTED OK\r\n":
            is_ble_connected = False
            disconnected()
            break
        
        brightnessRead = lightSensor.read()
        if brightnessRead != 0:
            s4Brightness = brightnessRead
        if s4TargetFlag == 1:
            if s4Brightness < s4Target: ##越亮, 值越低
                stage4SuccessFlag = 1
                break
        else:
            if s4Brightness > s4Target:
                stage4SuccessFlag = 1
                break


##--- Stage5: 手機解謎(藍芽) ---
def stage5Front():
    global s5QuestionList
    global s5Question

    qPicker = urandom.randint(0, 1)
    s5Question = s5QuestionList[qPicker]

def stage5Display():
    global stageInstruction
    global s5Question
    
    lcd.move_to(0,0)
    lcd.putstr("Answer on Phone")

    ##bleDisplay
    stageInstruction[5] = "請回答下列問題\r\n" + s5Question
    
def stage5():
    global s5Question
    global stage5SuccessFlag
    global is_ble_connected

    while True:
        cmd_id = voice_recognition.get_id()
        if inGame == 1:
            if cmd_id == 2: ##結束遊戲
                finishGame()
                break
            if cmd_id == 3: ##請求支援(提示)
                hint()
            if cmd_id == 7: ##重新遊戲
                init()
                main()
                break

        cmd = str(ble.read(30), 'utf-8').strip('\0')
        delay(500)
        if cmd == "SYSTEM-ECHO=DISCONNECTED OK\r\n":
            is_ble_connected = False
            disconnected()
            break
        elif cmd != "":
            if cmd == s5Question:
                clearLCD1()
                lcd.move_to(0,0)
                lcd.putstr("Correct")
                audio_decode.start('correct.mp3')
                clearLCD1()
                stage5SuccessFlag = 1
                break
            else:
                clearLCD1()
                lcd.move_to(0,0)
                audio_decode.start('wrong.mp3')
                lcd.putstr("Incorrect")
                clearLCD1()
                stage5Display()


##主程式------------------------------------------------------
boot()

while True:
    cmd = str(ble.read(30), 'utf-8').strip('\0')
    delay(500)
    if cmd == "SYSTEM-ECHO=CONNECTED OK\r\n":
        ble.data_mode_entry()
        is_ble_connected = True
        connected()
        break

while True:
    cmd_id = voice_recognition.get_id()
    cmd = str(ble.read(30), 'utf-8').strip('\0')
    if inGame == 0: ##未進遊戲
        if cmd_id == 1: ##開始遊戲
            init()
            main()
        if cmd_id == 7: ##重新開始
            init()
            main()
    delay(500)
    if cmd == "SYSTEM-ECHO=DISCONNECTED OK\r\n":
        is_ble_connected = False
        disconnected()
    if disconnectedFlag == 1:
        if cmd == "SYSTEM-ECHO=CONNECTED OK\r\n":
            ble.data_mode_entry()
            is_ble_connected = True
            connected()