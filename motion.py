import math 

def distance(a,b): 
    dx = a.x - b.x
    dy = a.y - b.y

    return math.sqrt((dx * dx) + (dy *dy)) 

class interpreter: 
    