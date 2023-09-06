import pygame
import random
import dicewar_AI
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
dark_gray = (50,50,50)

# Define hexagon
hexagon_size = 20
player_num = 8
rows=15
cols=20

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dice Wars Map")

# Set up parameters
max_dice = 8
max_undistributed = 50
button_rect = pygame.Rect(600, 30, 100, 40)
human = -1

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

# Run the game
def game():
    players, territories = initialize()
    calculate_player_territory( players, territories )

    game_continues = True
    targets = []
    while game_continues:
        targets.clear
        targets.append(None)
        for i in players:
            if i.territories_num == 0:
                players.remove(i)
                continue
            targets.append(turn(i, players, territories))
            if targets[-1] == "finish":
                game_continues = False
                break

# A single turn for a single player 
def turn(current_player, players, territories):
    selected_attacker = None
    selected_defender = None
    running = True
    targeted = None
    display_map(None, None, current_player, players, territories)
    while running:
        winner = check_victory(players, territories)
        if winner != None:
                print("Player " + str(winner) +" win!")
                running = False
                return "finish"
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return "finish"
        running = False
        selected_attacker = None
        selected_defender = None
        count_total_dice(players, territories)
        display_map(None, None, current_player, players, territories)
        if current_player.index == human: # Click on the attack first, and then click on the defender
            while selected_attacker == None or selected_defender == None:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        if button_rect.collidepoint(mouse_pos):
                            distribute_dice(current_player, territories)
                            return
                        for territory in territories:
                            territory_vertices = [pygame.math.Vector2(x, y) for x, y in territory.vertex]
                            mouse_pos = pygame.math.Vector2(mouse_pos)
                            if is_point_inside_polygon(mouse_pos, territory_vertices):
                                if selected_attacker is None:
                                    if territory.dice_count > 1 and territory.owner == current_player:
                                        selected_attacker = territory
                                        display_map(selected_attacker, None, current_player, players, territories)
                                elif selected_defender is None:
                                    if territory == selected_attacker:
                                        selected_attacker = None
                                        display_map(None, None, current_player, players, territories)
                                        break
                                    elif territory.owner != current_player:
                                        if territory in selected_attacker.neighbor:
                                            selected_defender = territory
                                            break
                        continue
        else:
            selected_attacker, selected_defender, targeted = dicewar_AI.primary_AI(current_player, territories, players)
        if selected_attacker and selected_defender:
            display_map(selected_attacker, selected_defender, current_player, players, territories)
            resolve_combat(selected_attacker, selected_defender)
            calculate_player_territory(players, territories)
            display_map(None, None, current_player, players, territories)
            selected_attacker = None
            selected_defender = None
            running = True

    distribute_dice(current_player, territories)
    return targeted

# display the whole map
def display_map (selected_attacker, selected_defender, current_player, players, territories):
    screen.fill(white)
    for territory in territories:

        if territory == selected_attacker:
            territory_color = black  # Attacker color
            font_color = selected_attacker.owner.color
        elif territory == selected_defender:
            territory_color = dark_gray  # Defender color
            font_color = selected_defender.owner.color
        else: 
            territory_color = territory.owner.color
            font_color = black if sum(territory_color) > 400 else white


        pygame.draw.polygon(screen, territory_color, territory.vertex, 0)
        pygame.draw.polygon(screen, black, territory.vertex, 2)

        font = pygame.font.Font(None, 36)
        text = font.render(str(territory.dice_count), True, font_color)
        text_rect = text.get_rect(center=territory.hexagon[0].center)
        screen.blit(text, text_rect)

        font = pygame.font.Font(None, 30)
        pygame.draw.rect(screen, black, button_rect)
        text = font.render("End Turn", True, white)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
    
    for player in players:
        player_font = pygame.font.Font(None, 30)
        player_text = f"P{player.index}: {player.territories_num}"
        player_surface = player_font.render(player_text, True, player.color)
        screen.blit(player_surface, (20,100 + player.index * 70 ))

        player_text = f"{player.undistributed} left"
        player_surface = player_font.render(player_text, True, player.color)
        screen.blit(player_surface, (20,120 + player.index * 70 ))

    # Display owner information
    current_player_font = pygame.font.Font(None, 24)
    current_player_text = f"Current Player: {current_player.index}"
    current_player_surface = current_player_font.render(current_player_text, True, current_player.color)
    screen.blit(current_player_surface, (20,20))

    current_player_text = f"Total territories: {len(territories)}"
    current_player_surface = current_player_font.render(current_player_text, True, black)
    screen.blit(current_player_surface, (300,20))
        
    pygame.display.flip()

def count_total_dice(players, territories):
    for player in players:
        total_dice = 0
        for territory in territories:
            if territory.owner == player:
                total_dice +=  territory.dice_count

        total_dice += player.undistributed
        player.total_dice = total_dice

# hold every combat
def resolve_combat(attacker, defender):
    attacker_rolls = roll_dice(attacker.dice_count)
    defender_rolls = roll_dice(defender.dice_count)
    
    attacker_sum = sum(attacker_rolls)
    defender_sum = sum(defender_rolls)
    
    display_dice_rolls(attacker.owner.color, attacker_rolls, defender.owner.color, defender_rolls)  # Display dice rolls
    
    if attacker_sum > defender_sum:
        defender.owner = attacker.owner
        defender.dice_count = attacker.dice_count - 1
        attacker.dice_count = 1
    else:
        attacker.dice_count = 1

# Dice rolling and combat resolution
def roll_dice(num_dice):
    return [random.randint(1, 6) for _ in range(num_dice)]

# Add a function to display dice rolls graphically
def display_dice_rolls(attacker_color, attacker_rolls, defender_color, defender_rolls):
    dice_size = 50
    x_spacing = 10
    y_position = 670  # Adjust the Y position as needed
    attacker_x = 20  # Adjust the X position as needed
    defender_x = 20  # Adjust the X position as needed
    for roll in attacker_rolls:
        draw_dice(attacker_x, y_position, roll, attacker_color)
        attacker_x += dice_size + x_spacing
    for roll in defender_rolls:
        draw_dice(defender_x, y_position + dice_size + x_spacing, roll, defender_color)
        defender_x += dice_size + x_spacing

    # Display the sums of dice rolls
    attacker_sum = sum(attacker_rolls)
    defender_sum = sum(defender_rolls)
    sum_font = pygame.font.Font(None, 24)
    sum_text = f"Attacker Sum: {attacker_sum}   Defender Sum: {defender_sum}"
    sum_surface = sum_font.render(sum_text, True, black)
    screen.blit(sum_surface, (20, 45))  # Adjust the position as needed
    pygame.display.flip()
    #pygame.time.wait(2000)  # Display for 2 seconds
    pygame.display.flip()

# Draw a simple dice
def draw_dice(x, y, value, color):
    dice_size = 50
    dice_color = color
    dot_color = black if sum(color) > 400 else white
    pygame.draw.rect(screen, dice_color, (x, y, dice_size, dice_size))
    
    if value in [1, 3, 5]:
        pygame.draw.circle(screen, dot_color, (x + dice_size // 2, y + dice_size // 2), dice_size // 10)
    if value in [2, 3, 4, 5, 6]:
        pygame.draw.circle(screen, dot_color, (x + dice_size // 4, y + dice_size // 4), dice_size // 10)
        pygame.draw.circle(screen, dot_color, (x + 3 * dice_size // 4, y + 3 * dice_size // 4), dice_size // 10)
    if value in [4, 5, 6]:
        pygame.draw.circle(screen, dot_color, (x + dice_size // 4, y + 3 * dice_size // 4), dice_size // 10)
        pygame.draw.circle(screen, dot_color, (x + 3 * dice_size // 4, y + dice_size // 4), dice_size // 10)

# calculate all player's score
def calculate_player_territory(players, territories):
    maxi = len(territories) / 2 + 1
    for player in players:
        territory_count = 0
        for territory in territories:
            if territory.owner == player:
                list = []
                list.append(territory)
                temp = find_adjecant_territory(list, territory, player)
                if temp > territory_count:
                    territory_count = temp
                if temp > maxi:
                    break
        player.territories_num = territory_count

# calculate adjecant territory using recursion
def find_adjecant_territory (current_list, current_territory, current_player):
    current_count = 1
    for neighbor in current_territory.neighbor:
        if neighbor.owner == current_player and neighbor not in current_list:
            current_list.append(neighbor)
            current_count += find_adjecant_territory(current_list, neighbor, current_player)
    return current_count


# distribute dice after each turn
def distribute_dice(current_player, territories):
    list = []
    for territory in territories:
        if territory.owner == current_player and territory.dice_count < max_dice:
            list.append(territory)
            
    current_dice = current_player.territories_num + current_player.undistributed
    current_player.undistributed = 0
    for i in range(current_dice):
        if len(list) == 0:
            current_player.undistributed = min(current_dice - i, max_undistributed)
            break
        temp_territory = random.choice(list)
        temp_territory.dice_count += 1
        if temp_territory.dice_count == max_dice:
            list.remove(temp_territory)
     
# check if the game ends
def check_victory(players, territories):
    for player in players:
        if player.territories_num == len(territories):
            return player.index
    return None

# check if the point is inside the polygon
def is_point_inside_polygon(point, vertices):
    intersections = 0
    prev_vertex = vertices[-1]

    for current_vertex in vertices:
        if (point.y > prev_vertex.y) != (point.y > current_vertex.y):
            if point.x < (current_vertex.x - prev_vertex.x) * (point.y - prev_vertex.y) / (current_vertex.y - prev_vertex.y) + prev_vertex.x:
                intersections += 1
        prev_vertex = current_vertex

    return intersections % 2 == 1


def primary_AI (current_player, territories, players):
    strong_enemy = []
    strength = []
    for player in players:
        if player.territories_num >= len(territories) / 4 and player != current_player:
            strong_enemy.append(player)
            strength.append(player.territories_num + player.total_dice)
            strength.sort(reverse=True)
    if len(strength) >= 2:
        if strength[0] - strength[1] >=  len(territories)/ 10:
            for player in strong_enemy:
                if player.territories_num + player.total_dice != strength[0]: 
                    strong_enemy.remove(player) 
    if len(strong_enemy) == 1:
        target = strong_enemy[0]
    else: target = None

    for territory in territories:
        if territory.owner == current_player and territory.dice_count > 1:
            random_neighbor = territory.neighbor
            random.shuffle(random_neighbor)
            for neighbor in random_neighbor:
                if territory.dice_count >= neighbor.dice_count and neighbor.owner != current_player:
                    if len(strong_enemy) == 0:
                        return territory, neighbor, None
                    else:
                        if neighbor.owner in strong_enemy:
                            return territory, neighbor, None
    return None, None, target


game()

# Quit pygame
pygame.quit()