##插件與腳位定義----------------------------------------------
from machine import I2C
from gpb import delay
from i2c_lcd import I2cLcd
from lcd_api import LcdApi

I2C_ADDR = 0x27
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16
i2c = I2C(scl='C0', sda='C1', freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

##函式--------------------------------------------------------
def clearLCD2():
    delay(2000)
    lcd.clear()
    delay(500)


##起始字樣----------------------------------------------------
lcd.move_to(0,0)
lcd.putstr("Welcome to")
lcd.move_to(0,1)
lcd.putstr("He-Sheng")

clearLCD2()

lcd.move_to(0,0)
lcd.putstr("Made by FongShan")
lcd.move_to(0,1)
lcd.putstr("New Age Men")