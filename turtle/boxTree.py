import turtle

angle=20
smallestBox=10



def drawBox(length,t):
  #t.setheading(angle)
  t.begin_fill()
  for i in range(4):
    t.forward(length)
    t.left(90)
  t.end_fill()



def tree(sideLen,t):
    if sideLen > smallestBox:
        #t.forward(branchLen)
        t.left(angle)
        drawBox(sideLen,t)

        if sideLen/1.5 > smallestBox:
          t.left(90)
          t.forward(sideLen)
          t.right(90)
        else:
          t.forward(sideLen*1.5)

        tree(sideLen/1.5,t)

        #t.right(90);t.forward(sideLen);
        #t.left(90-angle);t.forward(sideLen*1.5);
        tree(sideLen/1.5,t)
        
        #t.left(90)
        #t.forward(sideLen/1.5)
        #t.right(90)
        #t.left(angle)
        #t.left(90)
        #t.forward(sideLen/1.5)
        #t.right(90)
        #t.right(angle)
        #t.backward(sideLen/1.5)

def main(branchLen=75):
    t = turtle.Turtle()
    t.speed(5)
    myWin = turtle.Screen()
    #t.left(90)
    #t.up()
    #t.backward(100)
    #t.down()
    t.color("green")
    tree(branchLen,t)
    #myWin.exitonclick()

#main()
