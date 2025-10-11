move = "a1h8"
first = move[0:2]
second = move[2:4]


letters = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
x = int(second[1])-1
y = letters[second[0]]

print(x,y)