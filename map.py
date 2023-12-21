from queue import Queue


class Tile:
    def __init__(self, tile_num, terrain, is_def_terrain, texture):
        self.tileNum = tile_num  # number between 0-47, increases by 1 going right, 6 by going up
        self.x_coord = tile_num % 6
        self.y_coord = tile_num // 6

        # terrain key
        # 0 - default
        # 1 - forest
        # 2 - flier only (mountain, water, etc.)
        # 3 - trench
        # 4 - impassible

        self.terrain = terrain
        self.is_def_terrain = is_def_terrain

        self.hero_on = None
        self.savior_hero_on = None

        self.structure_on = None

        self.north = None
        self.east = None
        self.south = None
        self.west = None

        # divine vein key
        # 0 - none
        # 1 - flame
        # 2 - stone

        self.divine_vein = 0
        self.divine_vein_owner = 0

        # texture key
        # 0 - green grass / bush / water / trench / pillar
        # 1 - cobble path / tree / mountain / trench / house
        # 2 - sand / palm tree / spike pit / trench / wall
        # 3 - dark grass / flowers / x / x / castle
        # 4 - purple grass
        # 5 - wood
        self.terrain_texture = texture

    def tilesWithinNSpaces(self, n):
        fringe = Queue()  # tiles to visit
        tilesWithin = []  # tiles visited
        fringe.put(self)  # put this node in fringe
        tilesWithin.append(self)

        # Breadth First Search of local tiles within n spaces

        level = 0
        fringe.put(Tile(-1, -1, -1, -1))

        while not fringe.empty() and level < n:

            cur = fringe.get()

            if cur.north is not None and cur.north not in tilesWithin:
                fringe.put(cur.north)
                tilesWithin.append(cur.north)
            if cur.east is not None and cur.east not in tilesWithin:
                fringe.put(cur.east)
                tilesWithin.append(cur.east)
            if cur.south is not None and cur.south not in tilesWithin:
                fringe.put(cur.south)
                tilesWithin.append(cur.south)
            if cur.west is not None and cur.west not in tilesWithin:
                fringe.put(cur.west)
                tilesWithin.append(cur.west)

            if cur.tileNum == -1:
                level += 1
                fringe.put(Tile(-1, -1, -1, -1))

        return tilesWithin

    def unitsWithinNSpaces(self, n, lookForSameSide):
        if self.hero_on is None: return -1
        side = self.hero_on.side
        within_n_tiles = self.tilesWithinNSpaces(n)
        counter = 0
        for x in within_n_tiles:
            if x.hero_on.side == side and lookForSameSide or x.hero_on.side != side and not lookForSameSide: counter += 1
        return counter


class Structure:
    def __init__(self, struct_type, health, bct, rct, bcb, rcb):

        # structure key

        self.struct_type = struct_type
        self.health = health

        self.blueCanTraverse = bct
        self.redCanTraverse = rct

        self.blueCanBreak = bcb
        self.redCanBreak = rcb

# class AR_Structure: SUBCLASS
# level
# struct owner

# class MW_Structure: SUBCLASS
# level
# triggered


class Map:
    def __init__(self):
        self.tiles = [0] * 48
        for i in range(0, 48):
            self.tiles[i] = Tile(i, 0, 0, 0)
        for i in range(0, 48):
            if i // 6 != 0: self.tiles[i].south = self.tiles[i - 6]
            if i // 6 != 7: self.tiles[i].north = self.tiles[i + 6]
            if i % 6 != 0: self.tiles[i].west = self.tiles[i-1]
            if i % 6 != 5: self.tiles[i].east = self.tiles[i+1]

    '''def __init__(self, terrain_map, def_tile_map, texture_map):
        self.tiles = [48]
        for i in range(0, 48):
            self.tiles[i] = Tile(i, terrain_map[i], def_tile_map[i], texture_map[i])
        for i in range(0, 48):
            if i // 6 != 0: self.tiles[i].south = self.tiles[i - 6]
            if i // 6 != 7: self.tiles[i].north = self.tiles[i + 6]
            if i % 6 != 0: self.tiles[i].west = self.tiles[i - 1]
            if i % 6 != 5: self.tiles[i].east = self.tiles[i + 1]'''
