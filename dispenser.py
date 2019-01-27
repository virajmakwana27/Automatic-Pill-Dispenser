import time
import smtplib
import datetime
import Adafruit_CharLCD as LCD
import RTC_DS1302
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# firebase import part
from firebase import firebase
firebase = firebase.FirebaseApplication('https://pill-dispenser-c307e.firebaseio.com/', None)
# end

# lcd pins
lcd_rs = 25 
lcd_en = 12
lcd_d4 = 5
lcd_d5 = 16
lcd_d6 = 20
lcd_d7 = 18
lcd_backlight = 4
# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)
# end

# for alarm

IR_count = 22
alarmPin=6
IR_box=21
GPIO.setup(alarmPin,GPIO.OUT)
GPIO.setup(IR_box,GPIO.IN)
GPIO.setwarnings(False)
ThisRTC = RTC_DS1302.RTC_DS1302()
DateTime = { "Year":0, "Month":0, "Day":0, "DayOfWeek":0, "Hour":0, "Minute":0, "Second":0 }
Data = ThisRTC.ReadDateTime(DateTime)
# end

# notification via mail
def email_notify(text):
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.login("bjvaghela459@gmail.com","#bj9791%")
    server.sendmail("bjvaghela459@gmail.com", "shreyshah97@gmail.com",text)
    server.close()
#end
    
#converts object to string(firebase)
def getTime(text):
    number,pType,pTime=text.split(",")
    number=number.split(":")[1].strip()
    pType=pType.split(":")[1].strip()
    pTime,hour,minute=pTime.split(":")
    hour=hour.strip()
    ho=""
    for i in range (len(hour)-2,len(hour)):
        if hour[i]!="'":
            ho=ho+hour[i]
    if len(ho)==1:
        ho="0"+ho
    if minute[1]=="'":
        minute="0"+minute[0]
    else:
        minute = minute[0]+minute[1]
    #print("time="+ho+":"+minute)
    ans=ho+":"+minute
    return ans
#end

# call this function for alarm
def ring_alarm(for_email):
    lcd.clear()
    #print "ringing alarm"
    DateTime = { "Year":0, "Month":0, "Day":0, "DayOfWeek":0, "Hour":0, "Minute":0, "Second":0 }
    box_taken=False
    GPIO.output(alarmPin,False)
    start_time = datetime.datetime.now()
    time_elapsed=0
    while box_taken==False and time_elapsed < 1:
        #print "inside while loop"
        Data = ThisRTC.ReadDateTime(DateTime)
        curr_time = format(DateTime["Hour"],"02d") +":"+ format(DateTime["Minute"],"02d")
        #lcd.clear()
        if len(for_email)>10:
            message = "  Collect pills\n"+for_email
        else:
            message = "  Collect pills\n   "+for_email+"\n"
        lcd.message(message)
        GPIO.output(alarmPin,True)
        if GPIO.input(IR_box)==False:
            box_taken=True
        curr_time =datetime.datetime.now()
        s = str(curr_time - start_time)
        hour,minute,seconds = s.split(":")
        time_elapsed = int(minute)
    GPIO.output(alarmPin,False)
    if box_taken==False:
        notify = "Seems like you forgot to take your medicine for the day.\n"+for_email
        email_notify(notify)
    lcd.clear()
    # Write code here for notification part that budhaao didnt pick pill
# end

# call this function to get amount
def getAmount(text):
    number,pType,pTime=text.split(",")
    return int(number.split(":")[1].strip())
# end

# function for add pill
def getnumber(text):
    t1,amount = text.split(',')
    a1,amount_int = amount.split(':')
    amount_int = amount_int[:-1]
    amount_int = amount_int[1:]
    return int(amount_int)
# end

# call this function to dispense pill 1
def Pill1_dispense(amount):
    print " dispensing pill 1"
    count=0
    # be sure you are setting pins accordingly
    # GPIO10,GPIO9,GPIO11,GPI25
    StepPins = [4,17,23,24]
     
    # Set all pins as output
    for pin in StepPins:
        GPIO.setup(pin,GPIO.OUT)
      #GPIO.output(pin, False)

    GPIO.setup(IR_count,GPIO.IN)
    #wait some time to start
    time.sleep(2)
     
    # Define some settings
    StepCounter = 0
    WaitTime = 0.0010
    # Define simple sequence
    #StepCount1 = 4
    #Seq1 = []
    #Seq1 = range(0, StepCount1)
    #Seq1[0] = [1,0,0,0]
    #Seq1[1] = [0,1,0,0]
    #Seq1[2] = [0,0,1,0]
    #Seq1[3] = [0,0,0,1]
     
    # Define advanced sequence
    # as shown in manufacturers datasheet
    StepCount2 = 8
    Seq2 = []
    Seq2 = range(0, StepCount2)
    Seq2[0] = [0,1,0,0]
    Seq2[1] = [0,1,0,1]
    Seq2[2] = [0,0,0,1]
    Seq2[3] = [1,0,0,1]
    Seq2[4] = [1,0,0,0]
    Seq2[5] = [1,0,1,0]
    Seq2[6] = [0,0,1,0]

    Seq2[7] = [0,1,1,0]

    #Full torque
    StepCount3 = 4
    Seq3 = []
    Seq3= range(0, StepCount3)
    #Seq3 = [3,2,1,0]
    Seq3[0] = [0,0,1,1]
    Seq3[1] = [1,0,0,1]
    Seq3[2] = [1,1,0,0]
    Seq3[3] = [0,1,1,0]
     
    # set
    Seq = Seq2
    StepCount = StepCount2

    # Start main loop
    while True:
        if(GPIO.input(IR_count)==True):
            count=count+1
            print count
            time.sleep(1)
        if count>=amount:
            break
        for pin in range(0, 4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin]!=0:
                #print " Step %i Enable %i" %(StepCounter,xpin)
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
        StepCounter += 1
      # If we reach the end of the sequence
      # start again
        if StepCounter==StepCount:
            StepCounter = 0
        if StepCounter<0:
            StepCounter = StepCount
      # Wait before moving on
        time.sleep(WaitTime)
    # end
# call this function to dispense pill 2
def Pill2_dispense(amount):
    count=0
    print "dispensing pill 2"
    # be sure you are setting pins accordingly
    # GPIO10,GPIO9,GPIO11,GPI25
    StepPins = [27,10,9,11]
 
    # Set all pins as output
    for pin in StepPins:
        GPIO.setup(pin,GPIO.OUT)
      #GPIO.output(pin, False)

    GPIO.setup(IR_count,GPIO.IN)
    #wait some time to start
    time.sleep(2)
 
    # Define some settings
    StepCounter = 0
    WaitTime = 0.0010
    # Define simple sequence
    #StepCount1 = 4
    #Seq1 = []
    #Seq1 = range(0, StepCount1)
    #Seq1[0] = [1,0,0,0]
    #Seq1[1] = [0,1,0,0]
    #Seq1[2] = [0,0,1,0]
    #Seq1[3] = [0,0,0,1]
 
    # Define advanced sequence
    # as shown in manufacturers datasheet
    StepCount2 = 8
    Seq2 = []
    Seq2 = range(0, StepCount2)
    Seq2[0] = [0,1,0,0]
    Seq2[1] = [0,1,0,1]
    Seq2[2] = [0,0,0,1]
    Seq2[3] = [1,0,0,1]
    Seq2[4] = [1,0,0,0]
    Seq2[5] = [1,0,1,0]
    Seq2[6] = [0,0,1,0]
    Seq2[7] = [0,1,1,0]

    #Full torque
    StepCount3 = 4
    Seq3 = []
    Seq3= range(0, StepCount3)
    #Seq3 = [3,2,1,0]
    Seq3[0] = [0,0,1,1]
    Seq3[1] = [1,0,0,1]
    Seq3[2] = [1,1,0,0]
    Seq3[3] = [0,1,1,0]
 
    # set
    Seq = Seq2
    StepCount = StepCount2

    # Start main loop
    while True:
        if(GPIO.input(IR_count)==True):
            count=count+1
            print count
            time.sleep(1)
        if(count>=amount):
            break

        for pin in range(0, 4):
            xpin = StepPins[pin]
            if Seq[StepCounter][pin]!=0:
            #print " Step %i Enable %i" %(StepCounter,xpin)
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)
        StepCounter += 1
      # If we reach the end of the sequence
      # start again
        if StepCounter==StepCount:
            StepCounter = 0
        if StepCounter<0:
            StepCounter = StepCount
      # Wait before moving on
        time.sleep(WaitTime)
# end

def main():
  Total_Pill1 = 0
  Total_Pill2 = 0
  initial_pill1 = 0
  initial_pill2 = 0
  while True:
    text = str(firebase.get('/AddPill/Pill1',None))
    Pill1_amount_added = getnumber(text)
    text = str(firebase.get('/AddPill/Pill2',None))
    Pill2_amount_added = getnumber(text)
    if Pill1_amount_added != initial_pill1:
        Total_Pill1 = Total_Pill1 + Pill1_amount_added
        initial_pill1 = Pill1_amount_added
    if Pill2_amount_added != initial_pill2:
        Total_Pill2 = Total_Pill2 + Pill2_amount_added
        initial_pill2 = Pill2_amount_added
    time1 = []
    Pill1t1_data = str(firebase.get('/PillData/p1t1',None))
    time1.insert(0,getTime(Pill1t1_data))
    Pill1t2_data = str(firebase.get('/PillData/p1t2',None))
    time1.insert(1,getTime(Pill1t2_data))
    Pill1t3_data = str(firebase.get('/PillData/p1t3',None))
    time1.insert(2,getTime(Pill1t3_data))
    Pill2t1_data = str(firebase.get('/PillData/p2t1',None))
    time1.insert(3,getTime(Pill2t1_data))
    Pill2t2_data = str(firebase.get('/PillData/p2t2',None))
    time1.insert(4,getTime(Pill2t2_data))
    Pill2t3_data = str(firebase.get('/PillData/p2t3',None))
    time1.insert(5,getTime(Pill2t3_data))
    flag=0
    Data = ThisRTC.ReadDateTime(DateTime)
    curr_time = format(DateTime["Hour"],"02d") +":"+ format(DateTime["Minute"],"02d")
    if curr_time == "00:00":
        continue
    lcd.clear()
    lcd.message("    "+curr_time)  # lcd displaying
    index1=-1
    index2=-1
    for i in range(0,6):
        print "Firebase time is" +time1[i]
        print "current time is" + curr_time
        if time1[i]==curr_time:
            flag = flag+1
            if flag==1:
                index1=i
            if flag==2:
                index2=i
    if flag!=0:
        #print "time to dispense"
        if flag==1:
            if index1<3:
                if index1==0:
                    amount = getAmount(Pill1t1_data)
                if index1==1:
                    amount = getAmount(Pill1t2_data)
                if index1==2:
                    amount = getAmount(Pill1t3_data)
                if Total_Pill1<amount:
                    message = "Could not dispense pill1 as the amount is low"
                    email_notify(message)
                #print "amount = "+str(amount)
                else:    
                    Total_Pill1-=amount
                    Pill1_dispense(amount)
                    for_email = "type1 : "+str(amount)
                    ring_alarm(for_email)
                    if Total_Pill1<3:
                        print "pill 1 low"
                        notify = "Pill 1 low\nTotal pill 1 left are :"+str(Total_Pill1)
                        email_notify(notify)
                    print "remaining amount is"+str(Total_Pill1)
                    Data = ThisRTC.ReadDateTime(DateTime)
                    curr_time_2 = format(DateTime["Hour"],"02d") +":"+ format(DateTime["Minute"],"02d")
                    #lcd.clear()
                    lcd.message("   "+curr_time)  # lcd displaying
                    time.sleep(60)   
                
            else:
                if index1==3:
                    amount = getAmount(Pill2t1_data)
                if index1==4:
                    amount = getAmount(Pill2t2_data)
                if index1==5:
                    amount = getAmount(Pill2t3_data)
                if Total_Pill2<amount:
                    message = "Could not dispense pill2 as the amount is low"
                    email_notify(message)
                else:    
                    Total_Pill2-=amount
                    Pill2_dispense(amount)
                    for_email = "type2 : "+str(amount)
                    ring_alarm(for_email)
                    if Total_Pill2<3:
                        print "pill 2 low"
                        notify = "Pill 2 low\nTotal pill 2 left are :"+str(Total_Pill2)
                        email_notify(notify)
                    print "remaining amount is"+str(Total_Pill2)
                    Data = ThisRTC.ReadDateTime(DateTime)
                    curr_time_ = format(DateTime["Hour"],"02d") +":"+ format(DateTime["Minute"],"02d")
                    #lcd.clear()
                    lcd.message("   "+curr_time)  # lcd displaying
                    time.sleep(60)
                
        else:
             if index1==0:
                    amount1 = getAmount(Pill1t1_data)
             if index1==1:
                    amount1 = getAmount(Pill1t2_data)
             if index1==2:
                    amount1 = getAmount(Pill1t3_data)
             if index2==3:
                    amount2 = getAmount(Pill2t1_data)
             if index2==4:
                    amount2 = getAmount(Pill2t2_data)
             if index2==5:
                    amount2 = getAmount(Pill2t3_data)
             if Total_Pill1<amount1 or Total_Pill2<amount2:
                    message = "Could not dispense pills as the amount of pill1 or pill2 is low"
                    email_notify(message)
             else: 
				 Total_Pill1-=amount1
                 Total_Pill2-=amount2    
                 Pill1_dispense(amount1)
                 Pill2_dispense(amount2)
                 for_email = "type1:"+str(amount1)+" "+"type2:"+str(amount2)
                 ring_alarm(for_email)
                 curr_time_2 = format(DateTime["Hour"],"02d") +":"+ format(DateTime["Minute"],"02d")
                 #lcd.clear()
                 lcd.message("   "+curr_time)  # lcd displaying
                 time.sleep(60)
main()