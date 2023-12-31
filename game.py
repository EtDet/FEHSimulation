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

# A possible movement action by a unit
class Move():
    def __init__(self, dest, action, target, num_moved, is_warp, trav_str):
        self.destination = dest     # tile ID
        self.action = action        # 0 - move, 1 - assist, 2 - attack, -1 - end turn (screw you divine vein this needs to be separate)
        self.target = target        # Hero/Structure targeted by assist/attack
        self.num_moved = num_moved  # num tiles between start and this tile
        self.is_warp = is_warp      # does this move use a warp space?
        self.trav_string = trav_str # traversal string, holds default optimal path



# Create blank to be played upon
map0 = Map(0)

# Read JSON data associated with loaded map
with open(__location__ + "\\Maps\\story0-0-0.json") as read_file: data = json.load(read_file)

# Fill in terrain, starting tiles, enemy units, etc. into map
map0.define_map(data)

# hero definitions, used just for now
bolt = Weapon("Tactical Bolt", "Tactical Bolt", "idk", 14, 2, "Sword", {"colorlessAdv": 0}, ["Robin"])
robin = Hero("Robin", "M!Robin", 0, "BTome", 0, [40,29,29,29,22], [50, 50, 50, 50, 40], 30, 67)
robin.set_skill(bolt, 0)



# PLACE UNITS ONTO MAP

#robin.tile = map0.tiles[18]

player_units_all = [robin]
enemy_units_all = []

player_units = [robin]
enemy_units = []

i = 0
while i < len(data["enemyData"]):
    curEnemy = makeHero(data["enemyData"][i]["name"])

    curEnemy.side = 1
    curEnemy.set_rarity(data["enemyData"][i]["rarity"])
    curEnemy.set_level(data["enemyData"][i]["level"])

    if "alt_stats" in data["enemyData"][i]:
        curEnemy.visible_stats = data["enemyData"][i]["alt_stats"]


    if "weapon" in data["enemyData"][i]:
        curWpn = makeWeapon("Iron Sword")
        curEnemy.set_skill(curWpn, 0)

    curEnemy.tile = map0.enemy_start_spaces[i]
    enemy_units_all.append(curEnemy)
    enemy_units.append(curEnemy)
    i += 1

# METHODS

def allowed_movement(hero):
    move_type = hero.move

    spaces_allowed = 3 - abs(move_type - 1)

    spaces_allowed += 1 * (Status.MobilityUp in hero.statusPos)
    if Status.Gravity in hero.statusNeg or Status.MobilityUp in hero.statusPos and Status.Stall in hero.statusNeg:
        spaces_allowed = 1

    return spaces_allowed

#given a hero on a map, generate a list of tiles they can move to
def get_possible_move_tiles(hero):
    curTile = hero.tile

    spaces_allowed = allowed_movement(hero)

    visited = set()         # tiles that have already been visited
    # queue = [(curTile, 0)]  # array of tuples of potential movement tiles, current costs, and current optimal pattern
    queue = [(curTile, 0, "")]  # array of tuples of potential movement tiles, current costs, and current optimal pattern
    possible_tiles = []     # unique, possible tiles, to be returned
    optimal_moves = []

    char_arr = ['N', 'S', 'E', 'W']

    # while possibilities exist
    while queue:
        # get current tuple
        current_tile, cost, path_str = queue.pop(0)

        # not possible if too far
        if cost > spaces_allowed: break

        # add tile to possible movements & visited
        possible_tiles.append(current_tile)
        optimal_moves.append(path_str)
        visited.add(current_tile)

        # get all neighbors, including None neighbors
        current_neighbors = []
        for x in (current_tile.north, current_tile.south, current_tile.east, current_tile.west):
            current_neighbors.append(x)

        i = 0
        for x in current_neighbors:
            # if not already visited or None
            if x not in visited and x is not None:

                # get cost to visit this tile
                neighbor_cost = get_tile_cost(x, hero)

                # if tile cost within allowed cost and
                if cost + neighbor_cost <= spaces_allowed and neighbor_cost >= 0 and x.hero_on is None:
                    queue.append((x, cost + neighbor_cost, path_str + char_arr[i]))
                    visited.add(x)
            i += 1

    return (possible_tiles, optimal_moves)

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
phase = ENEMY


def move_sprite_to_tile(my_canvas, item_ID, num):
    x_move = 45 + 90 * (num % 6)
    y_move = 135 + 90 * (7 - (num//6))

    my_canvas.coords(item_ID, x_move-40, y_move-40)

def get_attack_tiles(tile_num, range):
    if range != 1 and range != 2: return []
    x_comp = tile_num%6
    y_comp = tile_num//6

    result = []

    if x_comp + range < 6: result.append(tile_num + range)
    if x_comp - range >= 0: result.append(tile_num - range)
    if y_comp + range < 8: result.append(tile_num + 6 * range)
    if y_comp - range >= 0: result.append(tile_num - 6 * range)

    if range == 2:
        if x_comp + 1 < 6 and y_comp + 1 < 8: result.append(tile_num + 1 + 6)
        if x_comp + 1 < 6 and y_comp - 1 >= 0: result.append(tile_num + 1 - 6)
        if x_comp - 1 >= 0 and y_comp + 1 < 8: result.append(tile_num - 1 + 6)
        if x_comp - 1 >= 0 and y_comp - 1 >= 0: result.append(tile_num - 1 - 6)

    return result

def get_arrow_offsets(arrow_num):
    if arrow_num == 0: return(16, 0)
    if arrow_num == 1: return(16, 1)
    if arrow_num == 3: return(-1, 0)
    if arrow_num == 4: return(16, 2)
    if arrow_num == 5: return(16, 0)
    if arrow_num == 6: return(0, 2)
    if arrow_num == 7: return(0, 1)
    if arrow_num == 8: return(0, 0)
    if arrow_num == 9: return (0, 1)
    if arrow_num == 10: return(0, 2)
    if arrow_num == 11: return(0, 2)
    if arrow_num == 12: return(0,0)
    if arrow_num == 13: return (0, 0)

    return (0,0)

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
            item_index = player_sprite_IDs.index(item_id)
            start_x, start_y = canvas.coords(item_id)
            canvas.drag_data = {'x': x, 'y': y, 'item': item_id, 'start_x': start_x, 'start_y': start_y, 'index': item_index}

            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            new_tile = x_comp + 6 * y_comp
            x_pivot = x_comp * 90
            y_pivot = (7-y_comp) * 90 + 90

            pivot_cache = (x_pivot, y_pivot)

            cur_hero = player_units[canvas.drag_data['index']]
            moves, paths = get_possible_move_tiles(cur_hero)

            canvas.drag_data['moves'] = []
            canvas.drag_data['paths'] = []
            canvas.drag_data['cur_tile'] = new_tile
            canvas.drag_data['cost'] = 0



            moves_obj_array = []
            a = cur_hero.tile.tileNum

            for i in range(0, len(moves)):
                canvas.drag_data['moves'].append(moves[i].tileNum)
                canvas.drag_data['paths'].append(paths[i])
                b = moves[i].tileNum
                dist = abs(b // 6 - a // 6) + abs(b % 6 - a % 6)
                moves_obj_array.append(Move(b, 0, None, dist, False, paths[i]))

            canvas.drag_data['cur_path'] = paths[canvas.drag_data['moves'].index(new_tile)]

            #i = 0
            tile_arr = []
            canvas.drag_data['blue_tile_id_arr'] = tile_arr

            for m in moves_obj_array:
                x_comp = m.destination % 6
                y_comp = m.destination // 6
                x_pivot = x_comp * 90
                y_pivot = (7 - y_comp) * 90 + 90

                #creates new blue tile
                curTile = canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=bt_photo)
                tile_arr.append(curTile)
                canvas.tag_lower(curTile, item_id)

            dupe_cache = []
            for m in moves_obj_array:
                atk_arr = get_attack_tiles(m.destination, cur_hero.weapon.range)
                for n in atk_arr:
                    if n not in canvas.drag_data['moves'] and n not in dupe_cache:
                        dupe_cache.append(n)

                        x_comp = n % 6
                        y_comp = n // 6
                        x_pivot = x_comp * 90
                        y_pivot = (7 - y_comp) * 90 + 90

                        cur_red_tile = prt_photo
                        if chosen_map.tiles[n].hero_on != None:
                            if chosen_map.tiles[n].hero_on.side != cur_hero.side:
                                cur_red_tile = rt_photo

                        curTile = canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=cur_red_tile)
                        tile_arr.append(curTile)
                        canvas.tag_lower(curTile, item_id)

            #canvas.create_image(x_pivot, y_pivot, anchor=tk.NW, image=arrow_photos[14])
            first_path = canvas.create_image(pivot_cache[0], pivot_cache[1], anchor=tk.NW, image=arrow_photos[14])
            canvas.tag_lower(first_path, item_id)
            canvas.drag_data['arrow_path'] = [first_path]

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

            cur_tile = canvas.drag_data['cur_tile']
            cur_path = canvas.drag_data['cur_path']

            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            new_tile = x_comp + y_comp * 6

            # different tile and within moves
            if cur_tile != new_tile and new_tile in canvas.drag_data['moves']:

                cur_hero = player_units[canvas.drag_data['index']]

                new_tile_cost = get_tile_cost(chosen_map.tiles[new_tile], cur_hero)
                canvas.drag_data['cost'] += new_tile_cost

                spaces_allowed = allowed_movement(cur_hero)
                is_allowed = canvas.drag_data['cost'] <= spaces_allowed


                # west
                if cur_tile - 1 == new_tile and is_allowed:
                    canvas.drag_data['cur_path'] += 'W'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("EW"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[cur_tile], cur_hero)

                # east
                elif cur_tile + 1 == new_tile and is_allowed:
                    canvas.drag_data['cur_path'] += 'E'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("WE"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[cur_tile], cur_hero)

                # south
                elif cur_tile - 6 == new_tile and is_allowed:
                    canvas.drag_data['cur_path'] += 'S'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("NS"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[cur_tile], cur_hero)

                # north
                elif cur_tile + 6 == new_tile and is_allowed:
                    canvas.drag_data['cur_path'] += 'N'
                    if len(canvas.drag_data['cur_path']) >= 2 and canvas.drag_data['cur_path'].endswith("SN"):
                        canvas.drag_data['cur_path'] = canvas.drag_data['cur_path'][:-2]
                        canvas.drag_data['cost'] -= new_tile_cost
                        canvas.drag_data['cost'] -= get_tile_cost(chosen_map.tiles[cur_tile], cur_hero)

                # other
                else:
                    canvas.drag_data['cur_path'] = canvas.drag_data['paths'][canvas.drag_data['moves'].index(new_tile)]

                    x_start_comp = canvas.drag_data['start_x'] // 90
                    y_start_comp = ((720 - canvas.drag_data['start_y']) // 90) + 1
                    recalc_tile = int(x_start_comp + 6 * y_start_comp)

                    new_cost = 0
                    for c in canvas.drag_data['cur_path']:
                        if c == 'N': recalc_tile += 6
                        if c == 'S': recalc_tile -= 6
                        if c == 'E': recalc_tile += 1
                        if c == 'W': recalc_tile -= 1
                        new_cost += get_tile_cost(chosen_map.tiles[recalc_tile], cur_hero)

                    canvas.drag_data['cost'] = new_cost

                canvas.drag_data['cur_tile'] = new_tile


            # get the x/y components of the starting tile, start drawing path from here
            x_arrow_comp = canvas.drag_data['start_x'] // 90
            y_arrow_comp = ((720 - canvas.drag_data['start_y']) // 90) + 1
            x_arrow_pivot = x_arrow_comp * 90
            y_arrow_pivot = (7 - y_arrow_comp) * 90 + 90
            arrow_start_tile = int(x_arrow_comp + 6 * y_arrow_comp)

            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)
            canvas.drag_data['arrow_path'] = []

            if new_tile in canvas.drag_data['moves']:
                if len(canvas.drag_data['cur_path']) == 0:
                    star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=arrow_photos[MOVE_STAR])
                    canvas.drag_data['arrow_path'].append(star)
                    canvas.tag_lower(star, canvas.drag_data['item'])
                else:
                    first_dir = -1
                    if canvas.drag_data['cur_path'][0] == 'N': first_dir = 0
                    if canvas.drag_data['cur_path'][0] == 'S': first_dir = 1
                    if canvas.drag_data['cur_path'][0] == 'E': first_dir = 2
                    if canvas.drag_data['cur_path'][0] == 'W': first_dir = 3

                    arrow_offset_x, arrow_offset_y = get_arrow_offsets(first_dir)

                    first_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=arrow_photos[first_dir])
                    canvas.drag_data['arrow_path'].append(first_arrow)
                    canvas.tag_lower(first_arrow, canvas.drag_data['item'])

                    if canvas.drag_data['cur_path'][0] == 'N': y_arrow_pivot -= 90
                    if canvas.drag_data['cur_path'][0] == 'S': y_arrow_pivot += 90
                    if canvas.drag_data['cur_path'][0] == 'E': x_arrow_pivot += 90
                    if canvas.drag_data['cur_path'][0] == 'W': x_arrow_pivot -= 90

                    i = 0
                    while i < len(canvas.drag_data['cur_path']) - 1:
                        cur_dir = -1
                        cur_element_1 = canvas.drag_data['cur_path'][i]
                        cur_element_2 = canvas.drag_data['cur_path'][i+1]

                        if cur_element_1 == 'N' and cur_element_2 == 'N' or cur_element_1 == 'S' and cur_element_2 == 'S': cur_dir = 8
                        if cur_element_1 == 'E' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'W': cur_dir = 9

                        if cur_element_1 == 'N' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'S': cur_dir = 10
                        if cur_element_1 == 'N' and cur_element_2 == 'W' or cur_element_1 == 'E' and cur_element_2 == 'S': cur_dir = 11
                        if cur_element_1 == 'S' and cur_element_2 == 'E' or cur_element_1 == 'W' and cur_element_2 == 'N': cur_dir = 12
                        if cur_element_1 == 'S' and cur_element_2 == 'W' or cur_element_1 == 'E' and cur_element_2 == 'N': cur_dir = 13

                        arrow_offset_x, arrow_offset_y = get_arrow_offsets(cur_dir)

                        cur_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=arrow_photos[cur_dir])
                        canvas.drag_data['arrow_path'].append(cur_arrow)
                        canvas.tag_lower(first_arrow, canvas.drag_data['item'])

                        if cur_element_2 == 'N': y_arrow_pivot -= 90
                        if cur_element_2 == 'S': y_arrow_pivot += 90
                        if cur_element_2 == 'E': x_arrow_pivot += 90
                        if cur_element_2 == 'W': x_arrow_pivot -= 90

                        i += 1

                    last_dir = -1
                    if canvas.drag_data['cur_path'][-1] == 'N': last_dir = 4
                    if canvas.drag_data['cur_path'][-1] == 'S': last_dir = 5
                    if canvas.drag_data['cur_path'][-1] == 'E': last_dir = 6
                    if canvas.drag_data['cur_path'][-1] == 'W': last_dir = 7

                    arrow_offset_x, arrow_offset_y = get_arrow_offsets(last_dir)

                    last_arrow = canvas.create_image(x_arrow_pivot + arrow_offset_x, y_arrow_pivot + arrow_offset_y, anchor=tk.NW, image=arrow_photos[last_dir])
                    canvas.drag_data['arrow_path'].append(last_arrow)
                    canvas.tag_lower(last_arrow, canvas.drag_data['item'])

            # delete current path, draw move_star at start only
            elif new_tile not in canvas.drag_data['moves']:
                if len(canvas.drag_data['arrow_path']) != 1:
                    for arrow in canvas.drag_data['arrow_path']:
                        canvas.delete(arrow)
                    canvas.drag_data['arrow_path'] = []
                star = canvas.create_image(x_arrow_pivot, y_arrow_pivot, anchor=tk.NW, image=arrow_photos[MOVE_STAR])
                canvas.drag_data['arrow_path'].append(star)
                canvas.tag_lower(star, canvas.drag_data['item'])

            for t in canvas.drag_data['arrow_path']:
                canvas.tag_lower(t, canvas.drag_data['item'])


    def on_release(event):
        if canvas.drag_data is not None:
            x_comp = event.x // 90
            y_comp = ((720 - event.y) // 90) + 1
            new_tile = x_comp + y_comp * 6

            # Set sprite to new position
            if event.y > 90 and event.y < 810 and event.x > 0 and event.x < 540 and new_tile in canvas.drag_data['moves']:


                move_sprite_to_tile(canvas, canvas.drag_data['item'], new_tile)
                player_units[canvas.drag_data['index']].tile.hero_on = None
                player_units[canvas.drag_data['index']].tile = chosen_map.tiles[new_tile]
                chosen_map.tiles[new_tile].hero_on = player_units[canvas.drag_data['index']]



            # Restore the item to the starting position, case happens if moved to invalid start position
            else:
                canvas.coords(canvas.drag_data['item'], canvas.drag_data['start_x'], canvas.drag_data['start_y'])

            for blue_tile_id in canvas.drag_data['blue_tile_id_arr']:
                canvas.delete(blue_tile_id)
            canvas.drag_data['blue_tile_id_arr'] = []

            for arrow in canvas.drag_data['arrow_path']:
                canvas.delete(arrow)
            canvas.drag_data['arrow_path'] = []

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

    # move tiles
    blue_tile = Image.open(__location__ + "\\CombatSprites\\" + "tileblue" + ".png")
    bt_photo = ImageTk.PhotoImage(blue_tile)

    red_tile = Image.open(__location__ + "\\CombatSprites\\" + "tilered" + ".png")
    rt_photo = ImageTk.PhotoImage(red_tile)

    pale_red_tile = Image.open(__location__ + "\\CombatSprites\\" + "tilepalered" + ".png")
    prt_photo = ImageTk.PhotoImage(pale_red_tile)

    # arrows
    arrows = Image.open(__location__ + "\\CombatSprites\\" + "Map" + ".png")
    arrow_photos = []

    START_NORTH = 0; START_SOUTH = 1; START_EAST = 2; START_WEST = 3
    END_NORTH = 4; END_SOUTH = 5; END_EAST = 6; END_WEST = 7
    LINE_VERT = 8; LINE_HORI = 9
    BEND_NE = 10; BEND_ES = 11; BEND_SE = 12; BEND_EN = 13
    MOVE_STAR = 14

    regions = [
        (182, 0, 240, 90),  # start_north
        (182, 91, 240, 180),  # start_south
        (256, 0, 346, 90),  # start_east
        (255, 90, 346, 180),  # start_west
        (182, 182, 240, 270),  # end_north
        (182, 271, 240, 345),  # end_south
        (256, 182, 346, 270),  # end_east
        (256, 271, 346, 345),  # end_west
        (346, 0, 436, 90),  # line_vert
        (346, 91, 436, 180),  # line_hori
        (346, 182, 436, 270),  # bend_NE
        (436, 182, 506, 270),  # bend_ES
        (346, 270, 436, 345),  # bend_SE
        (436, 270, 506, 345),  # bend_EN
        (436, 0, 505, 90)  # move_star
    ]

    # Crop and append each region to arrow_sects
    for region in regions:
        cropped_image = arrows.crop(region)
        arrow_photos.append(ImageTk.PhotoImage(cropped_image))

    # Now, arrow_sects contains all the cropped images





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
        player_units[i].side = PLAYER
        i += 1

    i = 0
    while i < len(enemy_units):
        move_sprite_to_tile(canvas, enemy_sprite_IDs[i], chosen_map.enemy_start_spaces[i])
        enemy_units[i].tile = chosen_map.tiles[chosen_map.enemy_start_spaces[i]]
        enemy_units[i].tile.hero_on = enemy_units[i]
        enemy_units[i].side = ENEMY
        i += 1

    # Bind mouse events for drag-and-drop
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)


    window.mainloop()
    return 0

start_sim(player_units,enemy_units, map0)