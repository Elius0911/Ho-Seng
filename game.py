from machine import I2C,Pin
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
rgbR = Pin(2,Pin.OUT)
rgbG = Pin(3,Pin.OUT)
rgbB = Pin(4,Pin.OUT)
btnR = Pin(11,Pin.IN)
btnG = Pin(12,Pin.IN)
btnB = Pin(13,Pin.IN)

##全域變數----------------------------------------------------
timer = 0
currentStageIndex = 5
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
        ##stage1()
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
    lcd.putstr("Control The Fan")
    
##def stage1():
    


##Stage2 顏色: 按鈕控制RGB
def stage2LCD():
    global color
    
    colorList = ["Yellow", "Magenta", "Cyan", "White"]
    picker = urandom.randint(0, 3)
    color = colorList[picker]
    
    lcd.move_to(0,0)
    lcd.putstr("Change The Light")
    lcd.move_to(0,1)
    lcd.putstr("to " + color)
    
def stage2(): 
    global stage2SuccessIndex
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
                stage2SuccessIndex = 1
                delay(1000)
                clearLED()
                break
        if color == "Magenta":
            if rgbRIndex == 1 & rgbBIndex == 1:
                stage2SuccessIndex = 1
                delay(1000)
                clearLED()
                break
        if color == "Cyan":
            if rgbGIndex == 1 & rgbBIndex == 1:
                stage2SuccessIndex = 1
                delay(1000)
                clearLED()
                break
        if color == "White":
            if rgbRIndex == 1 & rgbGIndex == 1 & rgbBIndex == 1:
                stage2SuccessIndex = 1
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
    questionList = ["cc","cc2"] ##TODO: 放題目
    picker = urandom.randint(0, 1)
    question = questionList[picker]
    print(question)
    
    while True:
        cmd = str(ble.read(30), 'utf-8').strip('\0')
        if cmd == "SYSTEM-ECHO=CONNECTED OK\r\n": ##學習歷程有得寫囉 嘻嘻
            delay(2000)
            ble.write("HAHA")
        else:
            if cmd != "Command mode OK\r\n": ##學習歷程又有得寫囉 嘻嘻
                if cmd != "":
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
        delay(10)

##主程式------------------------------------------------------
startGame()
currentStage(5)
'''
if stage2SuccessFlag == 1:
    nextStage()
    currentStage(currentStageIndex)
'''
if stage5SuccessFlag == 1:
    print("YA")

        