import cnc

cnc.removePiece("p", "a2")
while True:
    move = input("what'n'where")#np. a1b2p
    cnc.movePiece(move)