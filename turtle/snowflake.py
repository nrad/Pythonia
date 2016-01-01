import turtle

angle=60
totLen=200
level=2
smallestLine=1.*totLen/(3**level)
stepLen=totLen/level

def koch(t,order,length):
  if order == 0:
    t.forward(length)
  if order >= 0 :
    koch(t,order-1,length/3.)
    t.left(angle)
    koch(t,order-1,length/3.)      
    t.right(180-angle)
    koch(t,order-1,length/3.)
    t.left(60)
    koch(t,order-1,length/3.)

  
      
  # 
  #      t.forward(branchLen)
  #      t.right(angle)
  #      tree(branchLen-15,t)
  #      t.left(angle*2)
  #      tree(branchLen-15,t)
  #      t.right(angle)
  #      t.backward(branchLen)

def main(length=totLen):
    t = turtle.Turtle()
    t.speed(20)
    myWin = turtle.Screen()
    t.up()
    t.backward(totLen/2.)
    t.down()
    t.color("green")
    #for initAng in [0,300,300,300,300,300]:
    #  t.left(initAng)
    for initAng in [0,120,120]:
      t.right(initAng)
      koch(t,level,totLen)
    #myWin.exitonclick()

main()
