import math
import random

# Set up display
screen_width = 800
screen_height = 800

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
orange = (255, 165, 0)
coral = (255, 127, 80)
red = (255, 0, 0)
cyan = (0, 255, 255)
indigo = (75, 0, 130)
purple = (128, 0, 128)
teal = (0, 128, 128)
pink = (255, 192, 203)
maroon = (128, 0, 0)

# Define hexagon
hexagon_size = 20
player_num = 8
rows=15
cols=10

# Define a single hexagon
class Hexagon():
    def __init__(self, index, row_index, col_index, center, hexagons):
        self.index = index
        self.row_index = row_index
        self.col_index = col_index
        self.center = center
        self.neighbor = []
        self.border_direction = []
        self.territory = None

        for hexagon in hexagons:
            if hexagon.row_index == row_index:
                if hexagon.col_index == col_index + 1 or hexagon.col_index == col_index-1:
                    self.neighbor.append( hexagon )
                    hexagon.neighbor.append( self )
            if hexagon.row_index == row_index + 1 or hexagon.row_index == row_index - 1 :
                if hexagon.col_index == col_index:
                    self.neighbor.append( hexagon )
                    hexagon.neighbor.append( self )
            if hexagon.col_index % 2 == 0 and hexagon.row_index == row_index +1 :
                if hexagon.col_index == col_index + 1 or hexagon.col_index == col_index-1:
                    self.neighbor.append( hexagon )
                    hexagon.neighbor.append( self )
            if hexagon.col_index % 2 == 1 and hexagon.row_index == row_index -1 :
                if hexagon.col_index == col_index + 1 or hexagon.col_index == col_index-1:
                    self.neighbor.append( hexagon )
                    hexagon.neighbor.append( self )

# Define territory class
class Territory:
    def __init__(self, index, owner, dice_count):
        self.owner = owner
        self.index = index
        self.dice_count = dice_count
        self.hexagon = []
        self.neighbor = []
        self.vertex = []

# Define each player and color
class Player:
    def __init__(self, index):
        self.index = index
        self.territories_num = 0
        self.undistributed = 0
        self.total_dice = 0

        colors = [orange, red, cyan, indigo, purple,
                  teal, pink, maroon, coral]
        self.color = colors[index % len(colors)]

# Generate hexagon vertices
def generate_hexagon_vertices(center_x, center_y):
    vertices = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        x = center_x + hexagon_size * math.cos(angle_rad)
        y = center_y + hexagon_size * math.sin(angle_rad)
        vertices.append((x, y))
    return vertices

# Generate map territories
def generate_map(hexagons, territories, players):
    
    # Calculate the total width and height of the hexagonal grid
    total_width = cols * 3/2 * hexagon_size
    total_height = (rows + 0.5) * 2 * hexagon_size * math.sin(math.radians(60))

    # Calculate the offset to center the grid on the screen
    offset_x = (screen_width - total_width) / 2
    offset_y = (screen_height - total_height) / 2

    # Generate players
    for i in range(player_num):
        players.append(Player(i))

    # Generate hexagon centers
    hexagon_index = 0
    for row in range(rows):
        for col in range(cols):
            center_x = offset_x + col * 3/2 * hexagon_size
            center_y = offset_y + row * (2 * hexagon_size * math.sin(math.radians(60)))
            if col % 2 == 1:
                center_y += hexagon_size * math.sin(math.radians(60))
            hexagons.append(Hexagon(hexagon_index, row, col, (center_x, center_y), hexagons))
            hexagon_index += 1

    # Generate territory and distritube the hexagons to territories
    current_terrindex = 0
    territories.append(Territory(current_terrindex, random.choice(players), random.randint(1, 6)))
    while True:
        starting_hexagon = None
        for hexagon in hexagons:
            if hexagon.territory == None:
                starting_hexagon = hexagon
                break
        if starting_hexagon == None:
            if len(territories[current_terrindex].hexagon)== 0:
                territories.pop()
            break
        starting_hexagon.territory = territories[current_terrindex]
        find_neighbor_hexagon(starting_hexagon, territories[current_terrindex])

        if len(territories[current_terrindex].hexagon) < 4 :
            for hexagon in territories[current_terrindex].hexagon:
                new_territory = random.choice(hexagon.neighbor).territory
                new_territory.hexagon.append (hexagon)
                hexagon.territory = new_territory
            territories[current_terrindex].hexagon = []
        else: 
            current_terrindex += 1
            territories.append(Territory(current_terrindex, random.choice(players), random.randint(1, 6)))

# Find neighbor hexagons to form a territory using recursion
def find_neighbor_hexagon(current_hexagon, current_territory):
    current_territory.hexagon.append ( current_hexagon )
    neighbor_list = current_hexagon.neighbor
    random.shuffle(neighbor_list)
    for neighbor in neighbor_list:
        if neighbor.territory == None and len(current_territory.hexagon) < 7:
            neighbor.territory = current_territory
            find_neighbor_hexagon(neighbor, current_territory)

# Find neighbor territories for each territory
def find_neighbor_territories(territories):
    for territory in territories:
        for hexagon in territory.hexagon:
            for neighbor_hex in hexagon.neighbor:
                temp_col = hexagon.col_index
                temp_row = hexagon.row_index
                if neighbor_hex.territory != territory:
                    if neighbor_hex.territory not in territory.neighbor:
                        territory.neighbor.append(neighbor_hex.territory)

                    temp_index = hexagon.index - neighbor_hex.index
                    # confirm the border vertex and the direction of the border with neighbors
                    # the index of the vertice starts form the right and go clockwise
                    # the index of the direction of the border starts form the lower_right and go clockwise
                    if temp_index == cols:
                        border_direction(hexagon,4)
                    if temp_index == -cols:
                        border_direction(hexagon,1)
                    if temp_index == cols-1:
                        border_direction(hexagon,5)
                    if temp_index == -cols+1:
                        border_direction(hexagon,2)
                    if temp_index == cols+1:
                        border_direction(hexagon,3)
                    if temp_index == -cols-1:
                        border_direction(hexagon,0)
                    if temp_index == 1:
                        if temp_col % 2 == 0:
                            border_direction(hexagon,2)
                        elif temp_col % 2 == 1:
                            border_direction(hexagon,3)
                    if temp_index == -1:
                        if temp_col % 2 == 0:
                            border_direction(hexagon,0)
                        elif temp_col % 2 == 1:
                            border_direction(hexagon,5)

            # confirm the border vertex and the direction of the border without neighbors
            if temp_col == 0:
                border_direction(hexagon,2)
                border_direction(hexagon,3)
            if temp_col == cols-1:
                border_direction(hexagon,5)
                border_direction(hexagon,0)
            if temp_row == 0:
                if temp_col % 2 == 0:
                    border_direction(hexagon,3)
                    border_direction(hexagon,4)
                    border_direction(hexagon,5)
                elif temp_col % 2 == 1:
                    border_direction(hexagon,4)
            if temp_row == rows - 1:
                if temp_col % 2 == 0:
                    border_direction(hexagon,1)
                elif temp_col % 2 == 1:
                    border_direction(hexagon,0)
                    border_direction(hexagon,1)
                    border_direction(hexagon,2)

# To simplify the function find_neighbor_territories
def border_direction(hexagon, direction):
    if direction not in hexagon.border_direction:
        hexagon.border_direction.append(direction)


# find the border vertex of a territory using recursion
def find_next_vertex(hexagons, current_territory, current_direction, current_hexagon):

    vertex = generate_hexagon_vertices(current_hexagon.center[0],current_hexagon.center[1])[(current_direction + 1) % 6]
    if vertex in current_territory.vertex:
        return
    else:
        current_territory.vertex.append(vertex)

    if current_direction == 0:
        if 1 in current_hexagon.border_direction:
            find_next_vertex(hexagons, current_territory, 1, current_hexagon)
        else:
            if 5 in hexagons[current_hexagon.index + cols].border_direction: 
                find_next_vertex(hexagons, current_territory, 5, hexagons[current_hexagon.index + cols])
            else: print("ERROR")
    if current_direction == 1:
        if 2 in current_hexagon.border_direction:
            find_next_vertex(hexagons, current_territory, 2, current_hexagon)
        else:
            if 0 in hexagons[current_hexagon.index -1].border_direction and current_hexagon.col_index % 2 == 0: 
                find_next_vertex(hexagons, current_territory, 0, hexagons[current_hexagon.index -1])
            elif 0 in hexagons[current_hexagon.index + cols - 1].border_direction and current_hexagon.col_index % 2 == 1: 
                find_next_vertex(hexagons, current_territory, 0, hexagons[current_hexagon.index + cols -1])
            else: print("ERROR")
    if current_direction == 2:
        if 3 in current_hexagon.border_direction:
            find_next_vertex(hexagons, current_territory, 3, current_hexagon)
        else:
            if 1 in hexagons[current_hexagon.index -1].border_direction and current_hexagon.col_index % 2 == 1: 
                find_next_vertex(hexagons, current_territory, 1, hexagons[current_hexagon.index -1])
            elif 1 in hexagons[current_hexagon.index - cols -1].border_direction and current_hexagon.col_index % 2 == 0: 
                find_next_vertex(hexagons, current_territory, 1, hexagons[current_hexagon.index - cols -1])
            else: print("ERROR")
    if current_direction == 3:
        if 4 in current_hexagon.border_direction:
            find_next_vertex(hexagons, current_territory, 4, current_hexagon)
        else:
            if 2 in hexagons[current_hexagon.index - cols].border_direction: 
                find_next_vertex(hexagons, current_territory, 2, hexagons[current_hexagon.index - cols])
            else: print("ERROR")
    if current_direction == 4:
        if 5 in current_hexagon.border_direction:
            find_next_vertex(hexagons, current_territory, 5, current_hexagon)
        else:
            if 3 in hexagons[current_hexagon.index +1].border_direction and current_hexagon.col_index % 2 == 1: 
                find_next_vertex(hexagons, current_territory, 3, hexagons[current_hexagon.index +1])
            elif 3 in hexagons[current_hexagon.index - cols +1].border_direction and current_hexagon.col_index % 2 == 0: 
                find_next_vertex(hexagons, current_territory, 3, hexagons[current_hexagon.index - cols +1])
            else: print("ERROR")
    if current_direction == 5:
        if 0 in current_hexagon.border_direction:
            find_next_vertex(hexagons, current_territory, 0, current_hexagon)
        else:
            if 4 in hexagons[current_hexagon.index +1].border_direction and current_hexagon.col_index % 2 == 0: 
                find_next_vertex(hexagons, current_territory, 4, hexagons[current_hexagon.index +1])
            elif 4 in hexagons[current_hexagon.index + cols +1].border_direction and current_hexagon.col_index % 2 == 1: 
                find_next_vertex(hexagons, current_territory, 4, hexagons[current_hexagon.index + cols +1])
            else: print("ERROR")

def initialize ():

    hexagons = []
    territories = []
    players = []

    generate_map(hexagons, territories, players)
    find_neighbor_territories(territories)
    for territory in territories:
        find_next_vertex(hexagons, territory, territory.hexagon[0].border_direction[0] , territory.hexagon[0])

    return players, territories