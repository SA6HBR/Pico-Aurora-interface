# Pico-Aurora-Interface
Connect a raspberry pi pico to Ericsson C50 Aurora / Niros TRX3001

![alt text](https://github.com/SA6HBR/Pico-Aurora-interface/blob/main/image/circuit.png "Interface")  
You connect the interface in JS1. Same port normaly display is using.  
  
### Example: Code for get status of PTT  

    if com.getStatusBit(0x59):  
        radioStatus = "PTT-ON"  
        led.value(1)  
    else:  
        radioStatus = "PTT-OFF"  
        led.value(0)  
        
Status you can choose from:
![alt text](https://github.com/SA6HBR/Pico-Aurora-interface/blob/main/image/c52_display.png "Status")     
  
### Example: Code for press PTT  

    if button.value() and buttonPressed:  
        uart0.write(com.getButtonBytes("PTT"))  
        buttonPressed = False
        
    if button.value() == False and buttonPressed == False:  
        uart0.write(com.getButtonBytes(""))  
        buttonPressed = True  
  
Button you can choose from:  
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, M, S, #, *, ENTER, LS, ALARM, PTT, ON, UP, DOWN  

### Example: Code for press POWER

    if key.value() and keyPressed:  
      uart0.write(com.getKeyBytes("POWER"))  
      keyPressed = False  
  
    if key.value() == False and keyPressed == False:  
        uart0.write(com.getKeyBytes(""))  
        keyPressed = True  
  
Key/Function you can choose from:  
SW1, SW2, SW3, POWER, EM, ServiceMode  
  
## Useful Links

* [Circuit](https://github.com/SA6HBR/Pico-Aurora-interface/blob/main/CircuitDiagram/Pico_Aurora_interface.pdf)
* [MiKTeX](https://miktex.org/)
* [KiCad](https://www.kicad.org/)

## License

GNU General Public License v3.0, see [LICENSE](https://github.com/SA6HBR/SerialProxy/blob/main/LICENSE) for details.
