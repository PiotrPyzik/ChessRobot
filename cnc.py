
from time import sleep
setXStep = "$100 = 100"
setYStep = "$101 = 50"
setZStep = "$102 = 480"
z_distacne = 10
board_size = 24#cm
field_size = board_size/8

def sendGcode(cmd):
    ser.write((cmd + "\n").encode("utf-8"))
    while True:
        response = ser.readline().decode("utf-8").strip()
        if response == "ok":
            print("ok")
            return(True)
        elif response.startswith("error"):
            print(f"❌ {cmd} -> {response}")
            break
        else:
            if len(response)>1:
                print(f"↪ {response}")
                break

def chessNotationToMatrix(field):
    letters = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
    y = int(field[1])-1#cyfra z np. a1
    x = int(letters[field[0]])#litera z a1
    return([x,y])


def moveToField(field):
    field = chessNotationToMatrix(field)
    center_offset = field_size/2
    command = f"G1 X{field[0]*field_size} Y{field[1]*field_size}\n"
    sendGcode(command)
    
    
    return command
def connectToArduino():
    import serial
    while True:
        for i in range(8):
            print(f"trying port COM{i}")
            try: 
                ser = serial.Serial(port=f'COM{i}', baudrate=115200, timeout=.1) 
                print("p1 done")
                return(ser)
            except: 
                pass
        sleep(1)

def goHome():
    sendGcode("G1 X0 Y0 Z0")

def goToCamera():
    sendGcode("G1 Y-9 Z0")

def GRBLSetup():
    sendGcode(f"G90")
    sendGcode(f"$100=105")#x
    sendGcode(f"$101=50")#y
    sendGcode(f"$102=480")#z
    sendGcode(f"$112=100")#limit z feedrate
    sendGcode(f"$120=100")
    sendGcode(f"$121=100")
    sendGcode(f"$122=100")
    sendGcode(f'G10 P0 L20 X0')
    sendGcode(f'G10 P0 L20 Y0')
    sendGcode(f'G10 P0 L20 Z0')
    sendGcode(f"g1 f200")#set feedrate
    print("udało się?")


def catchPiece(z):
    sendGcode(f"M4")
    sendGcode(f"G1 Z{z}")
    sleep(2)
    sendGcode(f"G1 Z0")

def releasePiece(z):
    sendGcode(f"G1 Z{z}")
    sendGcode(f"M3")
    sendGcode(f"G1 Z0")
    
distance_from_board = 12.5
piece_height= {'p':3.5, 'b':4.6, 'r':4.5, 'k':5.5, 'n':4.5, 'q':4.9}

def movePiece(move):
    first = move[0:2]
    second = move[2:4]
    height = distance_from_board-piece_height[move[4:5]]
    moveToField(first)
    catchPiece(height)
    moveToField(second)
    releasePiece(height)
    
def removePiece(piece, field):
    height = distance_from_board-piece_height[piece]
    moveToField(field)
    catchPiece(height)
    sendGcode(f"G1 X{-field_size}")
    releasePiece(0)
    
ser = connectToArduino()
GRBLSetup()