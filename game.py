from combat import *
from map import Map

class Move():
    def __init__(self, dest, action, target, num_moved, is_warp):
        self.destination = dest     # tile ID
        self.action = action        # 0 - move, 1 - assist, 2 - attack, -1 - end turn (screw you B!Corrin)
        self.target = target        # Hero/Structure targeted by assist/attack
        self.num_moved = num_moved  # num tiles between start and this tile
        self.is_warp = is_warp      # does this move use a warp space?

test = Map()

sylgr = Weapon("Sylgr", "idk", 14, 2, {"spdBoost": 3, "sylgrBase": 0, "dagger": 7})
reposition = Skill("Reposition", "idk", {"repo": 0})
chillSpd3 = Skill("Chill Spd 3", "idk", {"chillSpd": 7})
spdTactic3 = Skill("Spd Tactic 3", "idk", {"spdTactic": 3})

ylgr = Hero("Ylgr", "Ylgr", 0, 0, 38, 33, 38, 22, 20, "BDagger", 0, sylgr, reposition, luna, sorceryBlade3, chillSpd3, spdTactic3, None, None)
enemy = Hero("Swordguy", "Swordguy", 1, 0, 50, 35, 25, 36, 22, "Sword", 0, stalwartSword, None, None, None, None, None, None, None)

#test.tiles[4].terrain = 1
# PLACE UNITS ONTO MAP
ylgr.tile = test.tiles[3]
enemy.tile = test.tiles[45]

# METHODS
def get_possible_move_tiles(hero):
    curTile = hero.tile
    move_type = hero.move

    # base movement
    spaces_allowed = 3 - abs(move_type) - 1

    # status effects
    spaces_allowed += 1 * (Status.MobilityUp in hero.statusPos)
    if Status.Gravity in hero.statusNeg or Status.MobilityUp in hero.statusPos and Status.Stall in hero.statusNeg:
        spaces_allowed = 1

    visited = set()
    queue = [(curTile, 0)]  # curTile.tilesWithinNSpaces(spaces_allowed)
    possible_tiles = []

    while queue:
        current_tile, cost = queue.pop(0)

        if cost > spaces_allowed: break

        possible_tiles.append(current_tile)
        visited.add(current_tile)

        current_neighbors = []
        for x in (current_tile.north, current_tile.east, current_tile.south, current_tile.west):
            if x is not None:
                current_neighbors.append(x)

        for x in current_neighbors:
            if x not in visited:
                neighbor_cost = get_tile_cost(x, hero)
                if cost + neighbor_cost <= spaces_allowed and neighbor_cost >= 0 and x.hero_on is None:
                    queue.append((x, cost + neighbor_cost))
                    visited.add(x)

    return possible_tiles


def get_tile_cost(tile, hero):
    cost = 1
    move_type = hero.move

    # cases in which units cannot go to tile
    if tile.terrain == 1 and move_type == 1: return -1 # cavalry & forests
    if tile.terrain == 2 and move_type != 2: return -1 # nonfliers & water/mountains
    if tile.terrain == 4: return -1                    # impassible terrain for anyone
    if tile.structure_on is not None: return -1        # structure currently on

    if tile.terrain == 1 and move_type == 0: cost = 2
    if tile.terrain == 3 and move_type == 1: cost = 2
    if tile.divine_vein == 1 and tile.divine_vein_owner != hero.side and hero.getRange() == 2: cost = 2

    if Status.TraverseTerrain in hero.statusPos: cost = 1

    if tile.hero_on is not None:
        if "pathfinder" in tile.hero_on.getSkills(): cost = 0

    return cost


player_units_all = [ylgr]
enemy_units_all = [enemy]

player_units = [ylgr]
enemy_units = [enemy]

turn_count = 0


while len(player_units) != 0 and len(enemy_units) != 0:
    turn_count += 1
    moves_obj_array = []
    a = ylgr.tile.tileNum

    moves = get_possible_move_tiles(ylgr)

    for i in range(0, len(moves)):
        b = moves[i].tileNum
        dist = abs(b//6 - a//6) + abs(b%6 - a%6)
        moves_obj_array.append(Move(b, 0, None, dist, False))

    i = 0
    for m in moves_obj_array:
        print("Move " + str(i) + ": Tile #" + str(m.destination) + ", " + str(m.num_moved) + " tiles away.")
        i += 1
    # method for print all possible moves
    #tile_choice = input("Pick a tile: ")

    print(simulate_combat(ylgr, enemy, 1, 1, 2, {}))

    for u in player_units:
        if u.HPcur == 0: player_units.remove(u)
    for e in enemy_units:
        if e.HPcur == 0: enemy_units.remove(e)

if len(player_units) == 0:
    print("Defeat")
else:
    print("Victory")
