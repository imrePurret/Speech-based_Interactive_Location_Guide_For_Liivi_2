
persons = []
f = open('PersonRoom.txt', 'r')
for line in f:
    persons.append(line.rstrip().split(" "))
lines = []
for i in persons:
     lines.append(i[0]+" "+i[1]+";[(WHERE)|(HOW)]?.*"+i[1][0].upper()+"[A-Z\.]* ?"+i[0].upper()+"+")


w = open('RegulaarAvaldised.txt', 'w')
for i in lines:
    w.write(i+"\n")
w.close()
