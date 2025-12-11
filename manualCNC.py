import cnc
cnc.goHome()
while True:
    move = input("what'n'where")#np. a1b2p
    cnc.moveToField(move)