##插件--------------------------------------------------------
from machine import I2C, Pin, ADC, PWM
from sensor import DHT11
import voice_recognition
from gpb import delay, timer
import urandom
from ble_uart import BleUart
from i2c_lcd import I2cLcd
from lcd_api import LcdApi

##gameTime = timer(1) ##TODO: Timer不知道怎麼取得時間值QQ

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

while True:
    cmd = str(ble.read(30), 'utf-8').strip('\0')
    print(cmd)
    delay(1000)
    if cmd == "SYSTEM-ECHO=CONNECTED OK\r\n":
        ble.data_mode_entry()
        is_ble_connected = True
        break

if cmd == "SYSTEM-ECHO=DISCONNECTED OK\r\n":
    if is_ble_connected == True:
        is_ble_connected = False
        disconnectedFlag = 1


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
disconnectedFlag = 0
currentStageIndex = 1
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


def startGame():
    ##global gameTime 
    global inGame

    ##gameTime.init(freq=1000) ##TODO: Timer不知道怎麼取得時間值QQ
    inGame = 1

    lcd.move_to(0,0)
    lcd.putstr("Game Start!!")
    lcd.move_to(0,1)
    lcd.putstr("Good Luck!")
    clearLCD2()
    
    lcd.move_to(0,0)
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

def finish(): ##關卡全破
    ##global gameTime

    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("Congratulations!")
    ble.write("------Congratulations!!------")
    ##lcd.move_to(0,1)
    ##lcd.putstr("time: " + str(gameTime)) ##TODO: Timer不知道怎麼取得時間值QQ

def gameover(): ##強制結束遊戲
    ##global gameTime
    global inGame
    
    inGame = 0
    
    lcd.move_to(0,0)
    lcd.putstr("Game Over")
    ble.write("----------Game Over----------")
    ##lcd.move_to(0,1)
    ##lcd.putstr("time: " + str(gameTime)) ##TODO: Timer不知道怎麼取得時間值QQ


def disconnected():
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
        ##currentStageIndex = 5 ##TODO:Debug時指定起始關卡用
        startGame()
        if stage1SuccessFlag == 1:
            nextStage()
        if stage2SuccessFlag == 1:
            nextStage()
        if stage3SuccessFlag == 1:
            nextStage()
        if stage4SuccessFlag == 1:
            nextStage()
        if stage5SuccessFlag == 1:
            finish()

def init(): ##初始化/重置
    ##global gameTime
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

    ##gameTime.deinit() ##TODO: Timer不知道怎麼取得時間值QQ
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

    while True:
        delay(1000)
        print(vr.read())
        fan.duty(int(vr.read()/4))
        if s1TargetFlag == 1:
            if vr.read() < 300 :
                stage1SuccessFlag = 1
                fan.duty(0)
                break
        else:
            if vr.read() > 3500:
                stage1SuccessFlag = 1
                fan.duty(0)
                break


##---Stage2: 按鈕控制RGB顏色---
def stage2Front():
    global s2Color
    global s2ColorList
    
    colorPicker = urandom.randint(0, 3)
    print(colorPicker)
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
    rgbRIndex = 0
    rgbGIndex = 0
    rgbBIndex = 0
    
    while True:
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
        delay(300)
        print(humidity)
        if humidity >= 5:
            if humidity <= humidity <= 63:
                break
    s3Target = humidity + 5
    print(s3Target)
    print("-----")

def stage3Display():
    lcd.move_to(0,0)
    lcd.putstr("Increase the")
    lcd.move_to(0,1)
    lcd.putstr("Humidity")
    stageInstruction[3] = "增加濕度到 " + str(s3Target) + " %"
    
def stage3():
    global dht
    global stage3SuccessFlag

    while True:
        delay(1000)
        humidity = dht.humidity()
        print(humidity)
        if dht.humidity() >= s3Target:
            stage3SuccessFlag = 1
            break
    

##--- Stage4: 光敏電阻 ---
def stage4Front():
    global s4Brightness
    global s4TargetFlag
    global s4Target
    
    while True:
        s4Brightness = lightSensor.read()
        delay(300)
        print(s4Brightness)
        if s4Brightness > 100:
            break
    s4TargetFlag = urandom.randint(0,1)
    print(s4TargetFlag)
    print("-----")

    if s4TargetFlag == 1:
        s4Target = s4Brightness - 300 ##越亮, 值越低
    else:
        s4Target = s4Brightness + 300
    print(s4Target)

def stage4Display():
    global s4TargetFlag
    global s4Target

    lcd.move_to(0,0)
    if s4TargetFlag == 1:
        lcd.putstr("Let it Brighter")
        stageInstruction[4] = "讓光感電阻變得更亮"
    else:
        lcd.putstr("Let it Darker")
        stageInstruction[4] = "讓光感電阻變得更暗"
    
def stage4():
    global s4Brightness
    global s4TargetFlag
    global s4Target
    global stage4SuccessFlag

    while True:
        delay(1000)
        brightnessRead = lightSensor.read()
        if brightnessRead != 0:
            s4Brightness = brightnessRead
        print(s4Brightness)
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
    stageInstruction[5] = "請回答下列問題:\r\n" + s5Question
    
def stage5():
    global s5Question
    global stage5SuccessFlag
    
    while True:
        cmd = str(ble.read(30), 'utf-8').strip('\0')
        if cmd != "":
            print(cmd)
            if cmd == s5Question:
                clearLCD1()
                lcd.move_to(0,0)
                lcd.putstr("Correct")
                clearLCD1()
                stage5SuccessFlag = 1
                break
            else:
                clearLCD1()
                lcd.move_to(0,0)
                lcd.putstr("Incorrect")
                clearLCD1()
                stage5Display()
        delay(500)


##主程式------------------------------------------------------

##迴圈不會執行的樣子
while True:
    cmd_id = voice_recognition.get_id() ##TODO: 語音包
    if inGame == 0: ##未進遊戲
        if cmd_id == 1: ##開始遊戲
            init()
            main()
    else: ##正在遊戲中
        if cmd_id == 2: ##結束遊戲
            gameover()
        if cmd_id == 3: ##請求支援(提示)
            hint()
        if cmd_id == 7: ##重新開始
            init()
            main()
        if disconnectedFlag == 1:
            disconnected()


'''
##閹割版
while True:
    cmd_id = voice_recognition.get_id() ##TODO: 語音包
    if cmd_id == 1: ##開始遊戲
        init()
        main()
        print(cmd_id)
    if cmd_id == 7: ##重新開始
        init()
        main()
        print(cmd_id)
    if disconnectedFlag == 1:
            disconnected()
'''