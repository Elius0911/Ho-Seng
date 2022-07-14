##插件與腳位定義----------------------------------------------
from machine import I2C,Pin#
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


rgbR = Pin(2,Pin.OUT)
rgbG = Pin(3,Pin.OUT)
rgbB = Pin(4,Pin.OUT)
btnR = Pin(11,Pin.IN)
btnG = Pin(12,Pin.IN)
btnB = Pin(13,Pin.IN)



##定義--------------------------------------------------------
currentStageIndex = 2
stage2Success = 0
timer = 0

rgbRIndex = 0
rgbGIndex = 0
rgbBIndex = 0
color = ""

def clearLCD():
    delay(2000)
    lcd.clear()
    delay(500)
    
def clearLED():
    rgbR.value(0)
    rgbG.value(0)
    rgbB.value(0)
    
def startGame():
    lcd.move_to(0,0)
    lcd.putstr("Game start!!")
    clearLCD()

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
    
    clearLCD()
    lcd.move_to(0,0)
    lcd.putstr("Stage Clear!!")
    clearLCD()
    lcd.putstr("Next Stage")
    lcd.move_to(0,1)
    lcd.putstr("Stage: " + str(currentStageIndex) + "/5")
    clearLCD()

##各關函式----------------------------------------------------
def stage1LCD():
    lcd.move_to(0,0)
    lcd.putstr("control the Fan")
    
##def stage1(): ##電阻控制風扇
    
    
def stage2LCD():
    global color
    
    colorList = ["Yellow", "Magenta", "Cyan", "White"]
    picker = urandom.randint(0, 3)
    color = colorList[picker]
    
    lcd.move_to(0,0)
    lcd.putstr("change the light")
    lcd.move_to(0,1)
    lcd.putstr("to " + color)
    
def stage2(): ##按鈕RGB
    global currentStageIndex
    global stage2Success
    global color
    global rgbRIndex
    global rgbGIndex
    global rgbBIndex
    
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
                stage2Success = 1
                break
        if color == "Magenta":
            if rgbRIndex == 1 & rgbBIndex == 1:
                stage2Success = 1
                break
        if color == "Cyan":
            if rgbGIndex == 1 & rgbBIndex == 1:
                stage2Success = 1
                break
        if color == "White":
            if rgbRIndex == 1 & rgbGIndex == 1 & rgbBIndex == 1:
                stage2Success = 1
                break
    
    
def stage3LCD():
    lcd.move_to(0,0)
    lcd.putstr("3")
    
##def stage3(): ##手指增加濕度(標準為當下濕度，通關為當下+5或3)
    
    
def stage4LCD():
    lcd.move_to(0,0)
    lcd.putstr("4")
    
##def stage4(): ##光敏


def stage5LCD():
    lcd.move_to(0,0)
    lcd.putstr("5")
    
def stage5(): ##藍芽模組解謎
    while True:
        cmd = str(ble.read(30), 'utf-8').strip('\0')
        if cmd != '':
            if cmd == 'cc':
                print('cc2')
            elif cmd == 'lol':
                print('lol2')
        delay(10)

##------------------------------------------------------------
##def checkStage():
##    lcd.clear()
##    delay(500)
##    lcd.move_to(0,0)
##    lcd.putstr("Stage: " + str(currentStageIndex) + "/5")
##    delay(500)
##    currentStage(currentStageIndex)


##主程式------------------------------------------------------
startGame()
'''
currentStage(2)
if stage2Success == 1:
    nextStage()
    clearLED()
    currentStage(currentStageIndex)
print(currentStageIndex)
'''
currentStage(5)
        