import turtle

angle=10
smallestBranch=3

def tree(branchLen,t):
    if branchLen > smallestBranch:
        t.forward(branchLen)
        t.right(angle)
        tree(branchLen-15,t)
        t.left(angle*2)
        tree(branchLen-15,t)
        t.right(angle)
        t.backward(branchLen)

def main(branchLen=100):
    t = turtle.Turtle()
    t.speed(20)
    myWin = turtle.Screen()
    t.left(90)
    t.up()
    t.backward(100)
    t.down()
    t.color("green")
    tree(branchLen,t)
    #myWin.exitonclick()

main()
