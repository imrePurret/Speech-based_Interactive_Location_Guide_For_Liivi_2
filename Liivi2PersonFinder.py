# -*- coding: utf-8 -*-
# It is program for voice introductions moving in Liivi 2 Tartu.
try:
    import pyttsx
    speak = True
except ImportError:
    speak = False
import re
import os
import sys
from Tkinter import *

global state
global name
state = 0
name = ""



isMac = False
if sys.platform == "darwin":
    isMac = True

#Calculating Levenshtein distance to get closest names.
def ld(s1,s2):
    if len(s1) > len(s2):
        s1,s2 = s2,s1
    distances = range(len(s1) + 1)
    for index2,char2 in enumerate(s2):
        newDistances = [index2+1]
        for index1,char1 in enumerate(s1):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1], distances[index1+1], newDistances[-1])))
        distances = newDistances
    return distances[-1]

if not os.path.isfile('RegulaarAvaldised.txt'):
    os.system("RegularExpressionGenerator.py")

if os.path.isfile('RegulaarAvaldised.txt'):
    countReg = 0
    countInf = 0
    with open('RegulaarAvaldised.txt') as infp:
        for line in infp:
          countReg += 1
    with open('PersonRoom.txt') as infp:
        for line in infp:
          countInf += 1
    if countReg != countInf:
        os.system("RegularExpressionGenerator.py")
    
persons = []
f = open('PersonRoom.txt', 'r')
for line in f:
    persons.append(line.rstrip().split(" "))

regulars = []
f = open('RegulaarAvaldised.txt', 'r')
for line in f:
    regulars.append(line.rstrip().split(";"))

locations = []
f = open('RoomLocation.txt', 'r')
for line in f:
    locations.append(line.rstrip().split(" "))

engine = pyttsx.init() #Generating speech engine.
rate = engine.getProperty('rate') # Setting voice speed.
engine.setProperty('rate', rate-75)
volume = engine.getProperty('volume')
engine.setProperty('volume', volume+1.5)
voices = engine.getProperty('voices')
engine.setProperty('voice', 0)
string = " "

def findClosestPerson(string):
    string = string.upper()
    arr = string.split(" ")
    if len(arr)>1:
        closest = ld((arr[0]+" "+arr[1]), (persons[0][0]+" "+persons[0][1]))
    else:
        closest = ld(arr[0], (persons[0][0]+" "+persons[0][1]))
    res = persons[0]
    for i in range(len(arr)-1):
        for j in persons:
            j[1] = j[1].upper()
            dist1 = ld((arr[i]+" "+arr[i+1]), (j[0]+" "+j[1]))
            dist2 = ld((arr[i]+" "+arr[i+1]), (j[1]+" "+j[0]))
            if dist1 < closest or dist2 < closest:
                closest = min(dist1,dist2)
                res=j
    if len(arr)==1:
        for j in persons:
            j[1] = j[1].upper()
            dist1 = ld(arr[0], (j[0]+" "+j[1]))
            dist2 = ld(arr[0], (j[1]+" "+j[0]))
            if dist1 < closest or dist2 < closest:
                closest = min(dist1,dist2)
                res=j
    return res

def findPerson(string, mast):
    global label
    global state
    global name
    if state==1:
        if (re.compile('(.*YES.*|.*EXACTLY.*)')).match(string.upper()):
            print "Nüüd tuleks nimi anda!"
            print name
    ct = 0
    name=None
    room=None
    location=None
    answer = ""
    string = string.upper()
    string = string.replace(u"Ä","A",10) #Changes Ä to A for regex
    string = string.replace(u'Ü',"Y",10) #Changes Ü to Y for regex
    string = string.replace(u"Š","S",10) #Changes Š to S for regex
    string = string.replace(u"Ž","Z",10) #Changes Š to S for regex

    for i in regulars:
        if (re.compile(i[1])).match(string):
            name = i[0].split(" ")
    if name==None:
        res = findClosestPerson(string)
        name = res
        answer += "Could not find person with this name. But maybe you are looking for " + res[1].title() + " " + res[0].title()+"."
        engine.runAndWait()
        try:
            label.pack_forget()
        except NameError:
            labelExists=True
        except AttributeError:
            labelExists=True
        label = Label(master, text="Could not find person with this name. But maybe you are looking for " + res[1].title() + " " + res[0].title()+".")
        label.pack()
        state = 1
        return answer
    for i in persons:
        if i[1].upper()==name[1].upper() and i[0].upper()==name[0].upper():
            room = i[2]
    if room==None:
        answer +="Could not find person with this name."
        engine.runAndWait()
        Label(master, text="No persons found!").pack()
        return answer
    for i in locations:
        if i[0]==room:
            location = i
    if location==None:
        answer +="Could not find person with this name."
        engine.runAndWait()
        Label(master, text="No persons found!").pack()
        return answer
    first = name[1].title() + " " + name[0].title()+' is on the '+location[1]+' floor room '+room+"."
    answer +=name[1].title() + " " + name[0].title()+' is on the '+location[1]+' floor room '+room+"."
    stair = ""
    if len(location)==7: #Instroctions logic
        if location[3]=="1":
            stair += "Go up the stairs to "+location[1]+" floor,"
        if location[3]=="-1":
            stair += "Go down the stairs to basement,"
        stair += " turn "+location[4]+", and the room "+room
        if location[5]=="end":
            stair += " is at the end of the corridor."
        else:
            stair += " is the "+location[5]+" door on your "+location[6]+"."
        answer +=stair
    if len(location)==8:
        if location[3]=="1":
            stair += "Go up the stairs to "+location[1]+" floor,"
        if location[3]=="-1":
            stair += "Go down the stairs to basement,"
        stair += " turn "+location[4]+", to corridor and turn "+location[5]+" to corridor and the room "+room
        stair += " is the "+location[6]+" door on your "+location[7]+"."
        answer +=stair
    if len(location)==9:
        if location[3]=="-1":
            stair += "Go down the stairs to basement,"
        if location[3]=="1":
            stair += "Go up the stairs to "+location[1]+" floor,"
        stair += " turn to "+location[4]+", corridor and turn"+location[5]+" to next corridor and"
        if location[6]=="end":
            stair += " at the end of the corridor is the room " +room+"."
        else:
            stair += " turn "+location[6]+", to corridor and the room "+room
            stair += " is the "+location[7]+" door on your "+location[8]+"."
        answer +=stair
    first = first.replace(u'Y',u"Ü",10)
    try:
        label.pack_forget()
    except NameError:
        labelExists=True
    label = Label(master, text=first+"\n"+stair)
    label.pack()
    state = 0
    return answer

def key(event):
    if '\r' == event.char:
        callback()

master = Tk() #Creates Tkinter window

master.tk.call('encoding', 'system', 'utf-8')
master.title("Person Finder in Liivi 2")
master.bind("<Key>", key)

Label(master, text=u'Who are you looking for? ').pack()

e = Entry(master, width=45, textvariable=u"Person name - at least first initial and family name!")
e.pack()

e.focus_set()
global label


def callback():
    message = findPerson(e.get(), master)
    if speak and not isMac:
        engine.say(message)
        engine.runAndWait()
    if speak and isMac:
        os.system("say '"+message+"'") 

b = Button(master, text="Find", width=15, command=callback)
b.pack()

mainloop()
