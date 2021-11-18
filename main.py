import time
from machine import Pin, ADC, PWM
from range_finder import RangeFinder
from gpio_lcd import GpioLcd


class VisitorCounter():
    def __init__(self):  
           
        self.potValue = 0
        self.counter = 0
        self.first = 0
        self.second = 0
        self.prior = 0
        self.limit = 2
        
        self.time1 = 0
        self.distance1 = 0
        self.time2 = 0
        self.distance2 = 0

        self.limitRange = 0
        self.doorRange = 0

        self.pot = ADC(26)   # the middle pin on the Potentiometer

        self.lcd = GpioLcd(rs_pin=Pin(7),
                          enable_pin=Pin(9),
                          d4_pin=Pin(10),
                          d5_pin=Pin(11),
                          d6_pin=Pin(12),
                          d7_pin=Pin(13),
                          num_lines=2, num_columns=16)

        self.led = Pin(25, Pin.OUT)
        self.warningLed = Pin(0, Pin.OUT)
        
        
        self.rangeFinderObject = RangeFinder(echo_pin=15, trigger_pin=14)
        self.rangeFinderObject2 = RangeFinder(echo_pin=21, trigger_pin=20)
        
    def setup(self):
        
        self.lcd.clear()
        self.lcd.move_to(0,0)
        self.lcd.putstr("Limit : " + str(self.limit))
        time.sleep(2)
        
        self.lcd.clear()
        #time.sleep(0.01)
        self.lcd.move_to(0,0) # default cursor position is (0,0)
        self.lcd.putstr("existing: " + str(self.counter))
        
        self.setButton = Pin(16, Pin.IN, Pin.PULL_DOWN)
        self.decButton = Pin(17, Pin.IN, Pin.PULL_DOWN)
        self.incButton = Pin(18, Pin.IN, Pin.PULL_DOWN)


    """ Maps two ranges together """

    def range_mapper(self,x, in_min, in_max, out_min, out_max): 
        return int((x-in_min) * (out_max-out_min) / (in_max - in_min) + out_min) 
   
    def run(self):
        while True:
            print("tt")
            if self.limit - self.counter <= 2 and self.limit - self.counter >0 and self.limit - self.counter != 0:
                self.warningLed.on()
                time.sleep(0.1)
                self.warningLed.off()
                time.sleep(0.1)
                
            elif self.limit - self.counter <= 0:
                self.warningLed.on()
            else:
                self.warningLed.off()
                
            if self.setButton.value():
                time.sleep(0.2)
                print("111")
                self.lcd.clear()
                self.lcd.putstr("Current Limit : " + str(self.limit))
                
                while True:                       
                    if self.incButton.value():
                        time.sleep(0.2)
                        print("222")
                        self.limit += 1
                        self.lcd.clear()
                        self.lcd.putstr("Current Limit : " + str(self.limit))
                    elif self.decButton.value():
                        time.sleep(0.2)
                        print("333")
                        self.limit -= 1
                        self.lcd.clear()
                        self.lcd.putstr("Current Limit : " + str(self.limit))
                    elif self.setButton.value():
                        time.sleep(0.2)
                        self.lcd.clear()
                        self.lcd.putstr("Set direction mode. (Right/Left)")
                        while True:

                            if self.incButton.value():
                                time.sleep(0.2)
                                self.rangeFinderObject2 = RangeFinder(echo_pin=15, trigger_pin=14)
                                self.rangeFinderObject = RangeFinder(echo_pin=21, trigger_pin=20)
                                self.lcd.clear()
                                self.lcd.putstr("The entry direction is from right to left.")
                            elif self.decButton.value():
                                time.sleep(0.2)
                                self.rangeFinderObject = RangeFinder(echo_pin=15, trigger_pin=14)
                                self.rangeFinderObject2 = RangeFinder(echo_pin=21, trigger_pin=20)
                                
                                self.lcd.clear()
                                self.lcd.putstr("The entry direction is from left to right.")
                            if self.setButton.value():
                                time.sleep(0.2)
                                break
                                
                        #self.lcd.clear()
 
                        print("set")
                        break
          
            time.sleep(0.2)
            
            potValue = self.pot.read_u16()
            distanceLimit = self.range_mapper(potValue,600, 65535,0,330)
            self.doorRange = distanceLimit
            self.lcd.clear()
            self.lcd.move_to(0,0) # default cursor position is (0,0)
            self.lcd.putstr("Current existence: " + str(self.counter))
            self.lcd.move_to(0,1)
            self.lcd.putstr("Range: " + str(distanceLimit) + " cm")
            
            if(self.counter < 0):     #reset
                
                self.counter = 0
                self.first = 0
                self.second = 0
                self.prior = 0
                
                # next 3 lines are equal to setup() method
                self.lcd.clear()
                #time.sleep(0.01)
                self.lcd.move_to(0,0) 
                self.lcd.putstr("existing: " + str(self.counter))
            if(self.counter >= 3):
                self.led.on()
            else:
                self.led.off()
               
            print(self.counter)
            print(self.first," ",self.second," ",self.prior)
            
            self.distance1 = round(self.rangeFinderObject.find(),1) # distance calculated in cm
            print(self.distance1)
            
            
            if (self.distance1 < self.doorRange and self.distance1 != 0 and self.first == 0): # first sensor detected 
                self.first = 1
                if(self.prior == 0):
                    self.prior = 1
                    print("first active")
            elif (self.distance1 > self.doorRange):
                self.first = 0
            
            if(self.prior == 2 and self.first == 1 and self.second == 0):
                print("exit")
                self.counter -= 1
                self.prior = 0
                if self.counter < 0:
                    self.counter = 0
                # next 3 lines are equal to setup() method
                self.lcd.clear()
                #time.sleep(0.01)
                self.lcd.move_to(0,0) 
                self.lcd.putstr("existing: " + str(self.counter))
            time.sleep(0.1)
            self.distance2 = round(self.rangeFinderObject2.find(),1)
            print(self.distance2)
            
            if(self.distance2 < self.doorRange and self.distance2 != 0 and self.second == 0):
                self.second = 1
                print("second active")       
                if(self.prior == 0 and self.first == 0):
                    self.prior = 2
            elif (self.distance2 > self.doorRange):
                self.second = 0
            if(self.prior == 1 and self.first == 0 and self.second == 1):
                self.counter += 1 
                self.prior = 0
                # next 3 lines are equal to setup() method
                self.lcd.clear()
                #time.sleep(0.01)
                self.lcd.move_to(0,0) 
                self.lcd.putstr("existing: " + str(self.counter))
                print("entry")
            
        
        

        
        
visitorCounter = VisitorCounter()

visitorCounter.setup()
visitorCounter.run()












