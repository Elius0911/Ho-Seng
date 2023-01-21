##插件與腳位定義----------------------------------------------
from machine import I2C, Pin, ADC, PWM
from gpb import delay
import urandom

from ble_uart import BleUart
from i2c_lcd import I2cLcd
from lcd_api import LcdApi

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(scl='C0', sda='C1', freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

ble = BleUart( 0 , 115200 )
delay(200)
ble.cmd_mode_entry()
ble.cmd_AT()
ble.set_device_name('New Age Men')

##元件腳位----------------------------------------------------
vr = ADC(1)
##fan = PWM(9, 200, 0)

rgbR = Pin(2,Pin.OUT)
rgbG = Pin(3,Pin.OUT)
rgbB = Pin(4,Pin.OUT)
btnR = Pin(11,Pin.IN)
btnG = Pin(12,Pin.IN)
btnB = Pin(13,Pin.IN)

##全域變數----------------------------------------------------
timer = 0
currentStageIndex = 1

stage1SuccessFlag = 0
stage2SuccessFlag = 0
stage5SuccessFlag = 0

color = ""

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
    
def startGame():
    lcd.move_to(0,0)
    lcd.putstr("Game Start!!")
    clearLCD2()

def currentStage(index):
    if index == 1:
        stage1LCD()
        stage1()
    elif index == 2:
        stage2LCD()
        stage2()
    elif index == 3:
        stage3LCD()
        ##stage3()
    elif index == 4:
        stage4LCD()
        ##stage4()
    elif index == 5:
        stage5LCD()
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
    clearLCD2()

##各關函式----------------------------------------------------
##Stage1 : 電阻控制風扇
def stage1LCD():
    lcd.move_to(0,0)
    lcd.putstr("control the Fan")
    
def stage1():
    global stage1SuccessFlag
    global vr
    target = 0 ## 0:讓風扇轉到最快, 1:讓風扇停
    sense = 0 ##只偵測電阻值一次
    
    while True:
        print(vr.read())
        fan.duty(int(vr.read()/4))
        
        if sense == 0:
            if vr.read() < 2000:
                target = 0  ##讓風扇轉到最快
                sense = 1
            if vr.read()>2001:
                target = 1  ##讓風扇停
                sense = 1
            
        if target == 1:
            if vr.read() < 70:
                stage1SuccessFlag = 1
                fan.duty(0)
                break
        else:
            if vr.read() > 3600 :
                stage1SuccessFlag = 1
                fan.duty(0)
                break
        delay(100)

##Stage2 顏色: 按鈕控制RGB
def stage2LCD():
    global color
    
    colorList = ["Yellow", "Magenta", "Cyan", "White"]
    colorPicker = urandom.randint(0, 3)
    color = colorList[colorPicker]
    print(color)
    print(colorPicker)
    
    lcd.move_to(0,0)
    lcd.putstr("Change The Light")
    lcd.move_to(0,1)
    lcd.putstr("to " + color)
    
def stage2(): 
    global stage2SuccessFlag
    global color
    rgbRIndex = 0
    rgbGIndex = 0
    rgbBIndex = 0
    
    while True:
        if btnR.value() == 1:
            if rgbRIndex == 0:
                rgbRIndex = 1
                delay(200)
            elif rgbRIndex == 1:
                rgbRIndex = 0
                delay(200)
            rgbR.value(rgbRIndex)
        if btnG.value() == 1:
            if rgbGIndex == 0:
                rgbGIndex = 1
                delay(200)
            elif rgbGIndex == 1:
                rgbGIndex = 0
                delay(200)
            rgbG.value(rgbGIndex)
        if btnB.value() == 1:
            if rgbBIndex == 0:
                rgbBIndex = 1
                delay(200)
            elif rgbBIndex == 1:
                rgbBIndex = 0
                delay(200)
            rgbB.value(rgbBIndex)
            
        if color == "Yellow":
            if rgbRIndex == 1 & rgbGIndex == 1:
                stage2SuccessFlag = 1
                delay(1000)
                clearLED()
                break
        elif color == "Magenta":
            if rgbRIndex == 1 & rgbBIndex == 1:
                stage2SuccessFlag = 1
                delay(1000)
                clearLED()
                break
        elif color == "Cyan":
            if rgbGIndex == 1 & rgbBIndex == 1:
                stage2SuccessFlag = 1
                delay(1000)
                clearLED()
                break
        elif color == "White":
            if rgbRIndex == 1 & rgbGIndex == 1 & rgbBIndex == 1:
                stage2SuccessFlag = 1
                delay(1000)
                clearLED()
                break
    

##Stage3 : 手指增加濕度(標準為當下濕度，通關為當下+5或3)
def stage3LCD():
    lcd.move_to(0,0)
    lcd.putstr("3")
    
##def stage3():
    
    
##Stage4 : 光敏電阻
def stage4LCD():
    lcd.move_to(0,0)
    lcd.putstr("4")
    
##def stage4(): 


##Stage5 藍芽模組解謎: 手機答題
def stage5LCD():
    lcd.move_to(0,0)
    lcd.putstr("Answer on Phone")
    
def correct():
    global stage5SuccessFlag

    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("Correct")
    clearLCD1()
    stage5SuccessFlag = 1

def incorrect():
    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("Incorrect")
    clearLCD1()
    stage5LCD()
    
def stage5():
    questionList = ["cc","cc2"]
    qPicker = urandom.randint(0, 1)
    question = questionList[qPicker]
    print(question)
    
    while True:
        cmd = str(ble.read(30), 'utf-8').strip('\0')
        if cmd == 'SYSTEM-ECHO=CONNECTED OK\r\n':      ##學習歷程有得寫囉 嘻嘻
            ble.data_mode_entry()
            is_ble_connected = True
        elif cmd == 'SYSTEM-ECHO=DISCONNECTED OK\r\n':
            ble.cmd_mode_entry()
            is_ble_connected = False
        if is_ble_connected == True:
            delay(100)
            ble.write("Question")
            if question == questionList[0]:
                if cmd == question:
                    correct()
                    break
                else:
                    incorrect()
            if question == questionList[1]:
                if cmd == question:
                    correct()
                    break
                else:
                    incorrect()
        delay(1000)

##主程式------------------------------------------------------
startGame()
currentStage(2)

if stage1SuccessFlag == 1:
    nextStage()
    currentStage(currentStageIndex)
if stage2SuccessFlag == 1:
    nextStage()
    currentStage(currentStageIndex)

if stage5SuccessFlag == 1:
    print("YA")       