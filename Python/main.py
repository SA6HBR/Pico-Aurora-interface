from machine import UART,Pin
import ubinascii,time
from imports.Aurora import communication as com

radioStatusLast = ""
controlStatus   = False
standAlone      = True
refreshBytes    = True
buttonPressed   = True
keyPressed      = True
debug           = True

button = Pin(14, Pin.IN, Pin.PULL_DOWN)
led    = Pin(15, Pin.OUT)
key    = Pin(16, Pin.IN, Pin.PULL_DOWN)

txPin  = 0
rxPin  = 1

uart0  = UART(0, baudrate=9600, bits=8, tx=Pin(txPin), rx=Pin(rxPin))

def powerOn(txPin,rxPin):
    tx = Pin(txPin,Pin.OUT)
    tx.value(0)
    time.sleep(1)
    uart0 = UART(0, baudrate=9600, bits=8, tx=Pin(txPin), rx=Pin(rxPin))

def powerOff():
    uart0.write(com.getKeyBytes("POWER"))
    time.sleep(2)
    uart0.write(com.getKeyBytes(""))


#START
if standAlone:
    #Check if it is running
    if uart0.any() > 0:
        dump = uart0.read()

    time.sleep(1)

    if uart0.any() == 0:
        powerOn(txPin,rxPin)
    
#LOOP
while 1>0:
    
    #get all status
    if refreshBytes and standAlone:
        refreshBytes = False
        uart0.write(com.getRefreshBytes())
    
    
    if uart0.any() > 0:
        if standAlone:
            # Radio without display
            controlStatus = com.readComportWithControlStatus(uart0.read())
        
            if controlStatus:
                uart0.write(com.getKeepAliveBytes())
                if debug:
                    print(ubinascii.hexlify(com.getKeepAliveBytes()))
        else:
            # Radio with display
            com.readComport(uart0.read())

    #### Button - START ###
    # "0","1","2","3","4","5","6","7","8","9","A","B","C","D","M","S","#","*","ENTER","LS","ALARM","PTT","ON","UP","DOWN"

    if button.value() and buttonPressed:
        uart0.write(com.getButtonBytes("PTT"))
        buttonPressed = False
    if button.value() == False and buttonPressed == False:
        uart0.write(com.getButtonBytes(""))
        buttonPressed = True

    #### Button - END ###


    #### Key - START ###
    # "SW1","SW2","SW3","POWER","EM","ServiceMode"

    if key.value() and keyPressed:
        uart0.write(com.getKeyBytes("POWER"))
        keyPressed = False

    if key.value() == False and keyPressed == False:
        uart0.write(com.getKeyBytes(""))
        keyPressed = True

    #### Key - END ###


    #### GET STATUS - START ###
    # 0x59 - Blixten - Transmission in progress - PTT
    # 0x5f - bollen - channel busy - Carrier-wave indicator
    # 0x63 - H - High transmit power
    # 0x65 - M - Medium transmit power
    # 0x67 - L - Low transmit power
    # 0x71 - SQ - Squelch
    # 0x77 - mail - VHS - Mottaget avrop
    # 0x81 - scan - Bärvågsscanning
    # 0x89 - Pause - Samtalsläge - uppkopplat
    # 0x8f - trekant Öppen trafik
    # 0x91 - > på hgt
    # 0x93 - hgt -  loudspeaker - Open monitoring - Öppen trafik
    # 0x95 - < på hgt
    # 0x99 - tuta - Yttre larm anslutet
    # 0x9b - tre strecken - External alarm
    # 0xa1 - P - Personsökarläge
    # 0xa7 - pil upp o ner - WHC call received

    if com.getStatusBit(0x59):
        radioStatus = "PTT-ON"
        led.value(1)
    else:
        radioStatus = "PTT-OFF"
        led.value(0)

    #### GET STATUS - END ###

    # print status when changes
    if radioStatus != radioStatusLast:
        print(radioStatus)
        radioStatusLast = radioStatus            

