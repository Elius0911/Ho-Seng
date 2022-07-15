##插件與腳位定義----------------------------------------------
from machine import I2C,Pin,ADC,PWM
from gpb import delay
import urandom

from ble_uart import BleUart
from i2c_lcd import I2cLcd
from lcd_api import LcdApi

import math


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

<<<<<<< Updated upstream
=======
while True:
    cmd = str(ble.read(30), 'utf-8').strip('\0')
    print(cmd)
    delay(1000)
    if cmd == "SYSTEM-ECHO=CONNECTED OK\r\n":      ##學習歷程有得寫囉 嘻嘻
        ble.data_mode_entry()
        is_ble_connected = True
        break


##元件腳位----------------------------------------------------
vr = ADC(1)
fan = PWM(9, 200, 0)
>>>>>>> Stashed changes

rgbR = Pin(2,Pin.OUT)
rgbG = Pin(3,Pin.OUT)
rgbB = Pin(4,Pin.OUT)
btnR = Pin(11,Pin.IN)
btnG = Pin(12,Pin.IN)
btnB = Pin(13,Pin.IN)

<<<<<<< Updated upstream
vr = ADC(1)
fan = PWM(9, 200, 0)
stage1Target = 0  ## =0(讓風扇轉到最快) =1(讓風扇停)
stage1Success = 0
stage1Sense = 0  #偵測電阻值一次就好

##定義--------------------------------------------------------
currentStageIndex = 2
stage2Success = 0
timer = 0

rgbRIndex = 0
rgbGIndex = 0
rgbBIndex = 0
color = ""
=======

##全域變數----------------------------------------------------
timer = 0
currentStageIndex = 1
stageInstruction = ["", "c1", "c2", "c3", "c4", "c5"]  ##關卡說明

stage1SuccessFlag = 0
stage2SuccessFlag = 0
stage3SuccessFlag = 0
stage4SuccessFlag = 0
stage5SuccessFlag = 0


s1Target = 0
s2Color = ""
s2ColorList = ["Yellow", "Purple", "Cyan", "White"]
s5QuestionList = ["cc","cc2"]    
s5Question = ""

>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    lcd.putstr("Game start!!")
    clearLCD()
=======
    lcd.putstr("Game Start!!")
    lcd.move_to(0,1)
    lcd.putstr("Stage: " + str(currentStageIndex) + "/5")
    ble.write("-------------Stage " + str(currentStageIndex) +"-------------")
    clearLCD2()
>>>>>>> Stashed changes

def bleStageInstructionDisplay(index):
    global stageInstruction
    if is_ble_connected == True:
        delay(100)
        ble.write("Stage"+ str(index) + ": " + stageInstruction[index])

def currentStage(index):
    if index == 1:
        stage1Front()
        stage1Display()
        bleStageInstructionDisplay(currentStageIndex)
        stage1()
        ##stage1()
    elif index == 2:
        stage2Front()
        stage2Display()
        bleStageInstructionDisplay(currentStageIndex)
        stage2()
    ##elif index == 3:
        ##stage3Front()
        ##stage3Display()
        ##bleStageInstructionDisplay(currentStageIndex)
        ##stage3()
    ##elif index == 4:
        ##stage4Front()
        ##stage4Display()
        ##bleStageInstructionDisplay(currentStageIndex)
        ##stage4()
    elif index == 5:
        stage5Front()
        stage5Display()
        bleStageInstructionDisplay(currentStageIndex)
        stage5()

def nextStage():
    global currentStageIndex
    currentStageIndex += 1
<<<<<<< Updated upstream
    
    clearLCD()
    lcd.move_to(0,0)
    lcd.putstr("Stage Clear!!")
    clearLCD()
    lcd.putstr("Next Stage")
    lcd.move_to(0,1)
    lcd.putstr("Stage: " + str(currentStageIndex) + "/5")
    clearLCD()
=======

    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("Stage Clear!!")
    clearLCD2()

    lcd.putstr("Next Stage")
    lcd.move_to(0,1)
    lcd.putstr("Stage: " + str(currentStageIndex) + "/5")
    ble.write("-------------Stage " + str(currentStageIndex) +"-------------")
    clearLCD2()
>>>>>>> Stashed changes

def finish():
    clearLCD1()
    lcd.move_to(0,0)
    lcd.putstr("All Clear!")
    lcd.move_to(0,1)
    lcd.putstr("Congratulations!")
    ble.write("--------Congratulations!!--------")


##各關函式----------------------------------------------------
<<<<<<< Updated upstream
def stage1LCD():
=======

##--- Stage1: 電阻控制風扇 ---
def stage1Front():
    global stageInstruction
    global vr
    global s1Target
    
    fan.duty(int(vr.read()/4))
    if vr.read() > 2001:
        s1Target = 1  ##讓風扇轉快一點
    if vr.read() < 2000:
        s1Target = 0  ##讓風扇停

def stage1Display():
    global stageInstruction
    global s1Target

>>>>>>> Stashed changes
    lcd.move_to(0,0)
    lcd.putstr("Control the Fan")

    #bleDisplay
    if s1Target == 1:
        stageInstruction[1] = "控制風扇，讓它轉快一點"
    else:
        stageInstruction[1] = "控制風扇，讓它停下來"
    
def stage1():
    global vr
<<<<<<< Updated upstream
    global stage1Target
    global stage1Success
    global stage1Sense
    while True:
        print(vr.read())
        fan.duty(int(vr.read()/4))
        if stage1Sense == 0:
            if vr.read()<2000:
                stage1Target = 0  ##讓風扇轉到最快
                stage1Sense = 1
            if vr.read()>2001:
                stage1Target = 1  ##讓風扇停
                stage1Sense = 1
            
        if stage1Target == 1:
            if vr.read() < 70:
                stage1Success = 1
                fan.duty(0)
                break
        if stage1Target == 0:
            if vr.read() > 3600 :
                stage1Success = 1
=======
    global s1Target

    while True:
        print(vr.read())
        fan.duty(int(vr.read()/4))
        if s1Target == 0:
            if vr.read() > 3600:
                stage1SuccessFlag = 1
                fan.duty(0)
                break
        elif s1Target == 1:
            if vr.read() < 100 :
                stage1SuccessFlag = 1
>>>>>>> Stashed changes
                fan.duty(0)
                break
        
        delay(100)
<<<<<<< Updated upstream
            
    
##def stage1(): ##電阻控制風扇
    
    
def stage2LCD():
    global color
    
    colorList = ["Yellow", "Magenta", "Cyan", "White"]
    picker = urandom.randint(0, 3)
    color = colorList[picker]
=======


##---Stage2 RGB顏色: 按鈕控制RGB---
def stage2Front():
    global s2Color
    global s2ColorList

    colorPicker = urandom.randint(0, 3)
    s2Color = s2ColorList[colorPicker]
>>>>>>> Stashed changes
    
def stage2Display():
    global stageInstruction
    global s2Color
    global s2ColorList
    lcd.move_to(0,0)
    lcd.putstr("change the light")
    lcd.move_to(0,1)
    lcd.putstr("to " + s2Color)

    ##bleDisplay
    if s2Color == s2ColorList[0]:
        stageInstruction[2] = "按下按鈕，讓燈變成黃色"
    elif s2Color == s2ColorList[1]:
        stageInstruction[2] = "按下按鈕，讓燈變成紫色"
    elif s2Color == s2ColorList[2]:
        stageInstruction[2] = "按下按鈕，讓燈變成青色"
    elif s2Color == s2ColorList[3]:
        stageInstruction[2] = "按下按鈕，讓燈變成白色"
    
<<<<<<< Updated upstream
def stage2(): ##按鈕RGB
    global currentStageIndex
    global stage2Success
    global color
    global rgbRIndex
    global rgbGIndex
    global rgbBIndex
=======
def stage2(): 
    global stage2SuccessFlag
    global s2Color
    rgbRIndex = 0
    rgbGIndex = 0
    rgbBIndex = 0
>>>>>>> Stashed changes
    
    while True:
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
            
        if s2Color == s2ColorList[0]:
            if rgbRIndex == 1 & rgbGIndex == 1:
                stage2Success = 1
                break
<<<<<<< Updated upstream
        if color == "Magenta":
=======
        elif s2Color == s2ColorList[1]:
>>>>>>> Stashed changes
            if rgbRIndex == 1 & rgbBIndex == 1:
                stage2Success = 1
                break
<<<<<<< Updated upstream
        if color == "Cyan":
=======
        elif s2Color == s2ColorList[2]:
>>>>>>> Stashed changes
            if rgbGIndex == 1 & rgbBIndex == 1:
                stage2Success = 1
                break
<<<<<<< Updated upstream
        if color == "White":
=======
        elif s2Color == s2ColorList[3]:
>>>>>>> Stashed changes
            if rgbRIndex == 1 & rgbGIndex == 1 & rgbBIndex == 1:
                stage2Success = 1
                break
    
<<<<<<< Updated upstream
    
def stage3LCD():
=======

##--- Stage3: 手指增加濕度 ---(標準為當下濕度，通關為當下+5或3)
##def stage3Front():

def stage3Display():
>>>>>>> Stashed changes
    lcd.move_to(0,0)
    lcd.putstr("3")
    
##def stage3(): ##手指增加濕度(標準為當下濕度，通關為當下+5或3)
    
    
<<<<<<< Updated upstream
def stage4LCD():
=======
##--- Stage4: 光敏電阻 ---
def stage4Front():
>>>>>>> Stashed changes
    lcd.move_to(0,0)
    lcd.putstr("4")
    
##def stage4(): ##光敏


<<<<<<< Updated upstream
def stage5LCD():
    lcd.move_to(0,0)
    lcd.putstr("5")
=======

##--- Stage5 藍芽模組解謎: 手機答題 ---
def stage5Front():
    global stageInstruction
    global s5QuestionList
    global s5Question
    qPicker = urandom.randint(0, 1)
    s5Question = s5QuestionList[qPicker]

def stage5Display():
    global stageInstruction
    global s5QuestionList
    global s5Question
    
    lcd.move_to(0,0)
    lcd.putstr("Answer on Phone")

    ##bleDisplay
    if s5Question == s5QuestionList[0]:
        stageInstruction[5] = "1st"
    elif s5Question == s5QuestionList[1]:
        stageInstruction[5] = "2nd"
    ##elif s5Question == s5QuestionList[2]:
    ##    stageInstruction[5] = ""
    ##elif s5Question == s5QuestionList[3]:
    ##   stageInstruction[5] = ""
    
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
    stage5Display()
    
def stage5():
    global s5Question
    global s5QuestionList
>>>>>>> Stashed changes
    
def stage5(): ##藍芽模組解謎
    while True:
        cmd = str(ble.read(30), 'utf-8').strip('\0')
<<<<<<< Updated upstream
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

=======
        if is_ble_connected == True:
            if cmd != "":
                print(cmd)
                if s5Question == s5QuestionList[0]:
                    if cmd == s5Question:
                        correct()
                        break
                    else:
                        incorrect()
                elif s5Question == s5QuestionList[1]:
                    if cmd == s5Question:
                        correct()
                        break
                    else:
                        incorrect()
                ##TODO: 有加題目就繼續放

        delay(1000)
>>>>>>> Stashed changes


##主要--------------------------------------------------------
def main():
    global currentStageIndex
    global stage1SuccessFlag
    global stage2SuccessFlag
    global stage3SuccessFlag
    global stage4SuccessFlag
    global stage5SuccessFlag

    if is_ble_connected == True:
        startGame()
        ##currentStageIndex = 2 ##TODO:之後刪
        currentStage(currentStageIndex) 
        if stage1SuccessFlag == 1:
            nextStage()
            currentStage(currentStageIndex)
        if stage2SuccessFlag == 1:
            nextStage()
            currentStageIndex = 5 ##TODO:之後刪
            currentStage(currentStageIndex)
            ##nextStage()
            ##currentStage(currentStageIndex)
        '''
        if stage3uccessFlag == 1:
            nextStage()
            currentStage(currentStageIndex)
        if stage4SuccessFlag == 1:
            nextStage()
            currentStage(currentStageIndex)
        '''
        if stage5SuccessFlag == 1:
            finish()


##主程式------------------------------------------------------
<<<<<<< Updated upstream
startGame()
'''
currentStage(2)
if stage2Success == 1:
    nextStage()
    clearLED()
    currentStage(currentStageIndex)
print(currentStageIndex)
'''
currentStage(1)
if stage1Success == 1:
    nextStage()
    clearLED()
    currentStage(currentStageIndex)
print(currentStageIndex)
        
=======
main()
##restart()
>>>>>>> Stashed changes
