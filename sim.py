from combat import *
from queue import Queue

class Tile:
    def __init__(self,terrain,x,y):

        self.x = x
        self.y = y

        self.terrain = terrain
        self.heroOn = None
        self.saviorHeroOn = None
        self.effects = None

        self.north = None
        self.east = None
        self.south = None
        self.west = None

    def getX(self): return self.x
    def getY(self): return self.y
    def getCoords(self): return self.x,self.y

    def setNorth(self,north):
        self.north = north

    def setEast(self,east):
        self.east = east

    def setSouth(self,south):
        self.south = south

    def setWest(self,west):
        self.west = west

    def getNorth(self):
        return self.north

    def getEast(self):
        return self.east

    def getSouth(self):
        return self.south

    def getWest(self):
        return self.west

    def setHero(self,hero):
        self.heroOn = hero

    def getHero(self):
        return self.heroOn

    def getTerrain(self):
        return self.terrain

    def printHero(self):
        if self.heroOn == None: print("None")
        else: print(self.heroOn.getName())

    def getTilesWithinNSpaces(self,n):
        fringe = Queue()
        tilesWithin = []
        fringe.put(self)
        tilesWithin.append(self)

        level = 0
        fringe.put(Tile(-1,-1,-1))
        while not fringe.empty() and level < n:
            cur = fringe.get()

            #print(cur.getX(),cur.getY())
            if cur.getNorth() != None and cur.getNorth() not in tilesWithin:
                fringe.put(cur.getNorth())
                tilesWithin.append(cur.getNorth())
            if cur.getEast() != None and cur.getEast() not in tilesWithin:
                fringe.put(cur.getEast())
                tilesWithin.append(cur.getEast())
            if cur.getSouth() != None and cur.getSouth() not in tilesWithin:
                fringe.put(cur.getSouth())
                tilesWithin.append(cur.getSouth())
            if cur.getWest() != None and cur.getWest() not in tilesWithin:
                fringe.put(cur.getWest())
                tilesWithin.append(cur.getWest())

            if cur.getX() == -1:
                level += 1
                fringe.put(Tile(-1,-1,-1))

        return tilesWithin

    def isWithinNTiles(self,other,n):
        tiles = self.getTilesWithinNSpaces(n)
        for tile in tiles:
            if tile.getHero() == other:
                return True
        return False


class StartingTile(Tile):
    def __init__(self,terrain,num,side,x,y):
        super().__init__(terrain,x,y)
        self.num = num
        self.side = side

class Map:
    def __init__(self,stp,ste):

        self.map=[]
        rows, cols = 8,6
        i = 0
        while i < rows:
            j = 0
            col = []
            while j < cols:
                col.append(Tile(0,j,i))
                j += 1
            self.map.append(col)
            i += 1

        self.startingTiles = [[], []]


        i = 0
        while i < len(stp):
            self.map[stp[i][0]][stp[i][1]] = StartingTile(self.map[stp[i][0]][stp[i][1]].getTerrain(),i,False,stp[i][1],stp[i][0])
            self.startingTiles[0].append(self.map[stp[i][0]][stp[i][1]])
            #self.currentTiles[0].append(self.map[stp[i][0]][stp[i][1]])
            i += 1

        i = 0
        while i < len(ste):
            self.map[ste[i][0]][ste[i][1]] = StartingTile(self.map[ste[i][0]][ste[i][1]].getTerrain(),i,True,ste[i][1],ste[i][0])
            self.startingTiles[1].append(self.map[ste[i][0]][ste[i][1]])
            #self.currentTiles[1].append(self.map[ste[i][0]][ste[i][1]])
            i += 1

        i = 0
        while i < len(self.map):
            j = 0
            while j < len(self.map[0]):
                if i != 0:
                    self.map[i][j].setNorth(self.map[i-1][j])
                if j != 0:
                    self.map[i][j].setWest(self.map[i][j-1])
                if i != len(self.map) - 1:
                    self.map[i][j].setSouth(self.map[i+1][j])
                if j != len(self.map[0]) - 1:
                    self.map[i][j].setEast(self.map[i][j+1])
                j += 1
            i += 1


    def placeUnits(self,playerUnits,enemyUnits):

        self.currentTiles = [{}, {}]
        self.playerUnits = playerUnits
        self.enemyUnits = enemyUnits

        i = 0
        while i < len(self.startingTiles[0]):
            self.startingTiles[0][i].setHero(playerUnits[i])
            self.currentTiles[0].update({playerUnits[i].getName(): self.startingTiles[0][i]})
            playerUnits[i].setTile(self.startingTiles[0][i])
            i += 1
        i = 0
        while i < len(self.startingTiles[1]):
            self.startingTiles[1][i].setHero(enemyUnits[i])
            self.currentTiles[1].update({enemyUnits[i].getName(): self.startingTiles[1][i]})
            enemyUnits[i].setTile(self.startingTiles[1][i])
            i += 1

        #print(self.currentTiles)

    def moveManual(self,unit,newSpace):
        return

    def getMap(self):
        return self.map

    def getCurrentTiles(self):
        return self.currentTiles


    def getNextUnits(self,boolean):
        if boolean: return self.enemyUnits
        else: return self.playerUnits


class State:
    def __init__(self,prev,map,phase,leftToAct):
        self.prev = prev
        self.map = map
        self.phase = phase # false - player, true - enemy
        self.leftToAct = leftToAct[:]

    def doMove(self,unit,newTile):
        oldTile = unit.getTile()
        oldTile.setHero(None)
        unit.setTile(newTile)
        newTile.setHero(unit)

        i = 0

        while i < len(self.leftToAct):
            if self.leftToAct[i] == unit:
                self.leftToAct.pop(i)
            i += 1
        if len(self.leftToAct) == 0:
            next = State(self,self.map,not self.phase,self.map.getNextUnits(not self.phase))
        else :
            next = State(self,self.map,self.phase,self.leftToAct)



    def getPossibleMoves(self,unit):
        move = unit.getMovement()
        tiles = []
        if move == 0 or move == 2:
            tiles = unit.getTile().getTilesWithinNSpaces(2)
        if move == 1:
            tiles = unit.getTile().getTilesWithinNSpaces(3)
        if move == 3:
            tiles = unit.getTile().getTilesWithinNSpaces(1)

        i = 0
        while i < len(tiles):
            if tiles[i].getHero() != None:
                tiles.pop(i)
                if i != 0: i -= 1
            i += 1
        tiles.append(unit.getTile())

        # 3 possible moves for each unit at a given state
        # do nothing
        # attack
        # support

        # we'll account for duo skills/pair up/canto later
        return tiles

    def nextStates(self, unit):
        return None

units = HeroDirectory().getHeroes()
playerUnits = [marth,nino,takumi,ephraim]
enemyUnits = [alm,nowi,hector,bartre]
startingTilesPlayer = [(7,1),(7,2),(7,3),(7,4)]
startingTilesEnemy = [(0,1),(0,2),(0,3),(0,4)]
map = Map(startingTilesPlayer,startingTilesEnemy)
map.placeUnits(playerUnits,enemyUnits)

startState = State(-1,map,False,playerUnits)
moves = startState.getPossibleMoves(ephraim)
startState.doMove(ephraim,moves[0])

daMap = map.getMap()

for x in daMap:
    for y in x:
        if y.getHero() != None: print(y.getHero().getName(),end='')
        else: print(None,end='')
        #print(y.getCoords()," ",end='')
    print()



print()
#for x in daMap:
#    for y in x:
#
#        if y.getEast() != None: print(y.getEast().getCoords()," ",end='')
#    print()

print(daMap[0][2].getTilesWithinNSpaces(2))
print(daMap[0][2].isWithinNTiles(nowi,2))
# current issue - control which move is next
