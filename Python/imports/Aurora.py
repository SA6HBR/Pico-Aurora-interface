# -----------------------------------------------------------
# Ericson C50 Aurora Communication
# (C) 2022 SA6HBR, Sweden
# Released under GNU Public License (GPL)
# email software@SA6HBR.se
# -----------------------------------------------------------
# status-adress
#
# getStatusBit(0x59) --> PTT
#
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
# -----------------------------------------------------------

import array
import ubinascii

debug       = True #False
startByte   = 0xff
controlByte = 0xe7
statusByte  = 0x00

displayByte = array.array('b',[0]*200)

firstByte   = False
lastByte    = False

rxArray     = array.array('b',[0]*64)
rxPrint     = -1
rxLength    = 0


# Intern functions
def getUnSignedByte(byte):
    if byte < 0:
        return 256+byte
    else:
        return byte
    
def get_bit(value, bit_index):
    return value & (1 << bit_index)

def setByte(byteArray,byteLength):
    startByte = getUnSignedByte(byteArray[1])
    countByte = getUnSignedByte(byteArray[2])
    global displayByte
    if startByte >= 0x00 and startByte <= getUnSignedByte(0xa7) and startByte + countByte <= 180 and countByte + 2 == byteLength:
        displayByte[startByte:startByte+countByte] = byteArray[3:3+countByte]
    else:
        if debug:
            print(ubinascii.hexlify(byteArray))
            print(str(countByte) + ' ' + str(byteLength))
        
def getBytesLength(byteArray,byteCount):

    length = 9
    if byteCount >= 2:
        if getUnSignedByte(byteArray[1]) == getUnSignedByte(controlByte):
            length = 2
        elif byteCount >= 60 or getUnSignedByte(byteArray[2]) >= 60:
            length = -1
        elif getUnSignedByte(byteArray[1]) >= getUnSignedByte(0x00) and getUnSignedByte(byteArray[1]) <= getUnSignedByte(0xa7):
            length = byteArray[2] + 2
        else:
            length = -1
            
    if debug and length == -1:
        print(ubinascii.hexlify(byteArray))
       
    return length

def readComport(rxBytes):
    rxBytesLength = len(rxBytes)
    global controlByte
    controlStatus = False
    global firstByte
    global startByte
    global lastByte
    global rxPrint
    global rxLength
    global rxArray
    global statusByte
    
    for y in range(0, rxBytesLength):
        if not firstByte and rxBytes[y] == startByte:
            firstByte = True
            rxPrint   = -1
            rxLength  = 9
            rxArray[0:64] = array.array('b',[0]*64)
    
        if firstByte:
            rxPrint          = rxPrint + 1
            rxArray[rxPrint] = rxBytes[y]
            rxLength = getBytesLength(rxArray,rxPrint)

        if firstByte and rxLength <= rxPrint:
            lastByte  = True

        if firstByte and lastByte:
            firstByte = False
            lastByte  = False

            if rxLength >= 0:
                if getUnSignedByte(rxArray[1]) == getUnSignedByte(controlByte):
                    controlStatus = True
                    statusByte    = rxArray[2]
                else:
                    setByte(rxArray,rxPrint)
    return controlStatus

def countNotNullInArray(checkArray):
    counts = 0
    for y in range(0, len(checkArray)):
        if checkArray[y] != 0x00:
            counts += 1
    return counts


# Extern functions
class communication:

    def getStatusBit(statusByte):
        global displayByte
        startByte = getUnSignedByte(statusByte)
        checkByte = displayByte[startByte]
        if get_bit(checkByte, bit_index=7) == 128:
            statusBool = True
        else:
            statusBool = False
        return statusBool

    def getButtonBytes(button):
        buttonName  = ["","0","1","2","3","4","5","6","7","8","9","A","B","C","D","M","S","#","*","ENTER","LS","ALARM","PTT","ON","UP","DOWN"]
        buttonByte  = array.array('b',[0x00,0x8c,0x87,0x86,0x85,0x8b,0x8a,0x89,0x8f,0x8e,0x8d,0x83,0x82,0x81,0x80,0x90,0x92,0x91,0x93,0x88,0x84,0x94,0x95,0x96,0x99,0x9A])
        buttonBytes = array.array('b',[0x21,0x02,0x00,0x00])
        try:
            a = buttonName.index(button)
        except ValueError:
            a = -1

        if a != -1:
            buttonBytes[3] = buttonByte[a]   

        return buttonBytes

    def getKeyBytes(key):
        keyName  = ["","SW1","SW2","SW3","POWER","EM","ServiceMode"]
        keyByte  = array.array('b',[0x00,0x01,0x02,0x04,0x08,0x10,0x18])
        keyBytes = array.array('b',[0x21,0x02,0x00,0xff])

        try:
            a = keyName.index(key)
        except ValueError:
            a = -1

        if a != -1:
            keyBytes[2] = keyByte[a]   

        return keyBytes

    def readComport(rxBytes):
        controlBool = False
        controlBool = readComport(rxBytes)

    def readComportWithControlStatus(rxBytes):
        controlBool = False
        controlBool = readComport(rxBytes)
        return controlBool

    def getKeepAliveBytes():
        global statusByte
        displayBytes = array.array('b',[ 0x21, 0x02, 0x83, 0x00])
        displayBytes[3] = statusByte   
        return displayBytes

    def getRefreshBytes():
        refreshBytes  = array.array('b',[0x00,0x21,0x02,0x85])
        return refreshBytes
    
    