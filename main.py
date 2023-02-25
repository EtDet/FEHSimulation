from future.moves.tkinter import *

class Tile:

    def __init__(self,terrain):
        self.terrain = terrain
        self.heroOn = None

    def setHero(self,hero):
        self.heroOn = hero


class Map:
    def __init__(self):
        self.map = []
        i = 0
        while i < 8:
            self.map.append([Tile(0),Tile(0),Tile(0),Tile(0),Tile(0),Tile(0)])
            i+=1

    def placeHero(self,hero,row,col):
        self.map[row][col].setHero(hero)

class Hero:
    def __init__(self,hp,at,sp,df,rs,weapon,movement):
        self.hp=hp
        self.at=at
        self.sp=sp
        self.df=df
        self.rs=rs
        self.wpnType = weapon
        self.move = movement  # 0 - inf, 1 - cav, 2 - fly, 3 - arm


marth = Hero(41,31,34,29,23,"Sword",0)
map = Map()
map.placeHero(marth,7,2)

root = Tk()
root.title('FEH Simulation Window')
root.iconbitmap('c:/Users/Ethan/PycharmProjects/FEHSimulation/Sprites/marth.png')
root.mainLoop()
#myCanvas = Canvas(root, width = 300, height = 400, bg = 'white')
