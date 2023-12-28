from combat import *
from map import Map
import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import os
import json

PLAYER = 0
ENEMY = 1

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

class Move():
    def __init__(self, dest, action, target, num_moved, is_warp):
        self.destination = dest     # tile ID
        self.action = action        # 0 - move, 1 - assist, 2 - attack, -1 - end turn (screw you B!Corrin)
        self.target = target        # Hero/Structure targeted by assist/attack
        self.num_moved = num_moved  # num tiles between start and this tile
        self.is_warp = is_warp      # does this move use a warp space?

#map definition
map0 = Map(0)
with open(__location__ + "\\Maps\\story0-0-0.json") as read_file:
    data = json.load(read_file)
map0.define_map(data)



#map0.add_start_space(18, PLAYER)
#map0.add_start_space(35, ENEMY)

# hero definitions
bolt = Weapon("Tactical Bolt", "Tactical Bolt", "idk", 14, 2, "Sword", {"colorlessAdv": 0}, ["Robin"])
robin = Hero("Robin", "M!Robin", 0, "BTome", 0, [40,29,29,29,22], [50, 50, 50, 50, 40], 30, 67)
#enemy = Hero("Swordguy", "Swordguy", 22, "Sword", 0, [30, 30, 30, 30, 30], [50, 50, 50, 50, 50], 0, 24)
robin.set_skill(bolt, 0)

# PLACE UNITS ONTO MAP

robin.tile = map0.tiles[18]

player_units_all = [robin]
enemy_units_all = []

player_units = [robin]
enemy_units = []

i = 0
while i < len(data["enemyData"]):
    curHero = makeHero(data["enemyData"][i]["name"])

    curHero.side = 1
    curHero.set_rarity(data["enemyData"][i]["rarity"])
    curHero.set_level(data["enemyData"][i]["level"])

    if "alt_stats" in data["enemyData"][i]:
        curHero.visible_stats = data["enemyData"][i]["alt_stats"]


    if "weapon" in data["enemyData"][i]:
        curWpn = makeWeapon("Iron Sword")
        curHero.set_skill(curWpn,0)

    curHero.tile = map0.enemy_start_spaces[i]
    enemy_units_all.append(curHero)
    enemy_units.append(curHero)
    i += 1

# METHODS

#given a hero on a map, generate a list of tiles they can move to
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

# given an adjacent tile and hero, calculate the movement cost to get to it
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


turn_count = 0
TURN_LIMIT = 50

'''
while (len(player_units) != 0 and len(enemy_units) != 0) and turn_count < TURN_LIMIT:
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

if len(enemy_units) != 0:
    print("Defeat")
else:
    print("Victory")
'''

def move_sprite_to_tile(my_canvas, item_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num//6))

    my_canvas.coords(item_ID, x_move-40, y_move-40)

def start_sim(player_units, enemy_units, chosen_map):
    if not chosen_map.player_start_spaces or not chosen_map.enemy_start_spaces:
        print("Error 100: No starting tiles")
        return -1

    if not player_units or len(player_units) > len(chosen_map.player_start_spaces):
        print("Error 101: Invalid number of player units")
        return -1

    def on_click(event):
        # Get the current mouse coordinates
        x, y = event.x, event.y

        # Find all items overlapping with the mouse coordinates
        overlapping_items = canvas.find_overlapping(x, y, x, y)

        # Check if any of the overlapping items are player units
        player_units_overlapping = [item for item in overlapping_items if item in player_sprite_IDs]

        if player_units_overlapping:
            # Remember the starting position of the drag and the item
            item_id = player_units_overlapping[0]
            start_x, start_y = canvas.coords(item_id)
            canvas.drag_data = {'x': x, 'y': y, 'item': item_id, 'start_x': start_x, 'start_y': start_y}
        else:
            canvas.drag_data = None

    def on_drag(event):
        # Check if there is any drag data
        if canvas.drag_data:
            # Calculate the distance moved
            delta_x = event.x - canvas.drag_data['x']
            delta_y = event.y - canvas.drag_data['y']

            # Move the item based on the distance moved
            canvas.move(canvas.drag_data['item'], delta_x, delta_y)

            # Update the starting position for the next drag event
            canvas.drag_data['x'] = event.x
            canvas.drag_data['y'] = event.y

    def on_release(event):
        if canvas.drag_data is not None:
            # Set sprite to new position
            if event.y > 90 and event.y < 810 and event.x > 0 and event.x < 540:
                #x_comp = ((720 - event.x)//90) + 1
                #y_comp = event.y//90
                x_comp = event.x//90
                y_comp = ((720 - event.y)//90) + 1
                new_tile = x_comp + y_comp * 6

                move_sprite_to_tile(canvas, canvas.drag_data['item'], new_tile)

            # Restore the item to the starting position, case happens if moved to invalid start position
            else:
                canvas.coords(canvas.drag_data['item'], canvas.drag_data['start_x'], canvas.drag_data['start_y'])

            canvas.drag_data = None

    # window
    window = ttk.Window(themename='darkly')
    window.title('Fire Emblem Heroes Simulator')
    window.geometry('540x900') #tile size: 90x90
    window.iconbitmap(__location__ + "\\Sprites\\Marth.ico")

    frame = ttk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame, width=540, height=810)  # Adjust the canvas size
    canvas.pack()

    # map
    map_image = Image.open(__location__ + "\\Maps\\" + "story0_0_0" + ".png")
    map_photo = ImageTk.PhotoImage(map_image)
    canvas.create_image(0, 90, anchor=tk.NW, image=map_photo)

    # units
    player_sprites = []
    player_sprite_IDs = []
    enemy_sprites = []
    enemy_sprite_IDs = []
    for x in player_units:
        respString = "-R" if x.resp else ""
        curImage = Image.open(__location__ + "\\Sprites\\" + x.intName + respString + ".png")
        modifier = curImage.height/85
        resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)
        curPhoto = ImageTk.PhotoImage(resized_image)
        player_sprites.append(curPhoto)

    for i, player_sprite in enumerate(player_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor=tk.NW, image=player_sprite)
        player_sprite_IDs.append(item_id)

    for x in enemy_units:
        respString = "-R" if x.resp else ""
        curImage = Image.open(__location__ + "\\Sprites\\" + x.intName + respString + ".png")
        curImage = curImage.transpose(Image.FLIP_LEFT_RIGHT)
        modifier = curImage.height/85
        resized_image = curImage.resize((int(curImage.width / modifier), 85), Image.LANCZOS)
        curPhoto = ImageTk.PhotoImage(resized_image)
        enemy_sprites.append(curPhoto)

    for i, enemy_sprite in enumerate(enemy_sprites):
        item_id = canvas.create_image(100 * i, 200, anchor=tk.NW, image=enemy_sprite)
        enemy_sprite_IDs.append(item_id)

    i = 0
    while i < len(player_units):
        move_sprite_to_tile(canvas, player_sprite_IDs[i], chosen_map.player_start_spaces[i]) # place sprite
        player_units[i].tile = chosen_map.tiles[chosen_map.player_start_spaces[i]]
        player_units[i].tile.hero_on = player_units[i]
        i += 1

    i = 0
    while i < len(enemy_units):
        move_sprite_to_tile(canvas, enemy_sprite_IDs[i], chosen_map.enemy_start_spaces[i])
        enemy_units[i].tile = chosen_map.tiles[chosen_map.enemy_start_spaces[i]]
        enemy_units[i].tile.hero_on = enemy_units[i]
        i += 1

    # Bind mouse events for drag-and-drop
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    window.mainloop()
    return 0

start_sim(player_units,enemy_units, map0)