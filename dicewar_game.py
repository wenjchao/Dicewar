import pygame
import random
import math
import random
import time

# Define a single hexagon
class Hexagon():
    def __init__(self, row_index, col_index, center, hexagons):
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

        orange = (255, 165, 0)
        coral = (255, 127, 80)
        red = (255, 0, 0)
        cyan = (0, 255, 255)
        indigo = (75, 0, 130)
        purple = (128, 0, 128)
        teal = (0, 128, 128)
        pink = (255, 192, 203)
        maroon = (128, 0, 0)
        
        colors = [orange, red, cyan, indigo, purple,
                  teal, pink, maroon, coral]
        self.color = colors[index % len(colors)]

class DicewarGame(Hexagon, Territory, Player):
    def __init__(self, rows = 15, cols = 10, player_num = 8):

        self.hexagons = []
        self.territories = []
        self.players = []

        # key = (hex.col - neigh.col, hex.row - neigh.row, hex.col % 2 ), value = direction
        self.direction_dict = {(0,1,0):4, (0,1,1):4, (0,-1,0):1, (0,-1,1):1, 
                               (-1,0,0):0, (-1,1,0):5, (-1,-1,1):0, (-1,0,1):5, 
                               (1,0,0):2, (1,1,0):3, (1,-1,1):2, (1,0,1):3}

        # Set up parameters
        self.player_num = player_num
        self.rows = rows
        self.cols = cols
        self.max_dice = 8
        self.max_undistributed = 50

        self.reset()

    def reset(self):
        self.hexagons.clear()
        self.territories.clear()
        self.players.clear()

        self.generate_map()
        self.find_neighbor_territories()
        self.calculate_player_territory(None, None)

    # Generate map territories
    def generate_map(self):
        hexagons = self.hexagons
        territories = self.territories
        players = self.players

        # Generate players
        for i in range(self.player_num):
            players.append(Player(i))

        # Generate hexagons
        hexagon_index = 0
        for row in range(self.rows):
            for col in range(self.cols):
                hexagons.append(Hexagon(row, col, None, hexagons))
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
            self.find_neighbor_hexagon(starting_hexagon, territories[current_terrindex])

            if len(territories[current_terrindex].hexagon) < 3 :
                for hexagon in territories[current_terrindex].hexagon:
                    new_territory = random.choice(hexagon.neighbor).territory
                    new_territory.hexagon.append (hexagon)
                    hexagon.territory = new_territory
                territories[current_terrindex].hexagon = []
            else: 
                current_terrindex += 1
                territories.append(Territory(current_terrindex, random.choice(players), random.randint(1, 6)))

    # Find neighbor hexagons to form a territory using recursion
    def find_neighbor_hexagon(self, current_hexagon, current_territory):
        current_territory.hexagon.append ( current_hexagon )
        neighbor_list = current_hexagon.neighbor
        random.shuffle(neighbor_list)
        for neighbor in neighbor_list:
            if neighbor.territory == None and len(current_territory.hexagon) < 4:
                neighbor.territory = current_territory
                self.find_neighbor_hexagon(neighbor, current_territory)

    # Find neighbor territories for each territory
    def find_neighbor_territories(self):
        for territory in self.territories:
            for hexagon in territory.hexagon:
                for neighbor_hex in hexagon.neighbor:
                    temp_col = hexagon.col_index
                    temp_row = hexagon.row_index
                    neigh_col = neighbor_hex.col_index
                    neigh_row = neighbor_hex.row_index
                    if neighbor_hex.territory != territory:
                        if neighbor_hex.territory not in territory.neighbor:
                            territory.neighbor.append(neighbor_hex.territory)

                        # confirm the border vertex and the direction of the border with neighbors
                        # the index of the vertice starts form the right and go clockwise
                        # the index of the direction of the border starts form the lower_right and go clockwise
                        self.border_direction(hexagon, {self.direction_dict[(temp_col - neigh_col, temp_row - neigh_row, temp_col % 2 )]})

                # confirm the border vertex and the direction of the border without neighbors
                if temp_col == 0: self.border_direction(hexagon,{2,3})
                if temp_col == self.cols - 1: self.border_direction(hexagon,{5,0})
                if temp_row == 0:
                    if temp_col % 2 == 0: self.border_direction(hexagon,{3,4,5})
                    else: self.border_direction(hexagon,{4})
                if temp_row == self.rows - 1:
                    if temp_col % 2 == 0: self.border_direction(hexagon,{1})
                    else: self.border_direction(hexagon,{0,1,2})

    # To simplify the function find_neighbor_territories
    def border_direction(self, hexagon, direction):
        for i in direction:
            if i not in hexagon.border_direction: 
                hexagon.border_direction.append(i)
        
    # calculate all player's score
    def calculate_player_territory(self, previous_attacker, previous_defender):
        maxi = len(self.territories) / 2 + 1
        if previous_attacker == None or previous_defender == None:
            player_list = self.players
        else:
            player_list = [previous_attacker, previous_defender]

        for player in player_list:
            territory_count = 0
            list = []
            for territory in self.territories:
                if territory.owner == player and territory not in list:
                    list.clear()
                    list.append(territory)
                    temp = self.find_adjecant_territory(list, territory, player)
                    if temp > territory_count:
                        territory_count = temp
                    if temp > maxi:
                        break
            player.territories_num = territory_count

    # calculate adjecant territory using recursion
    def find_adjecant_territory (self, current_list, current_territory, current_player):
        current_count = 1
        for neighbor in current_territory.neighbor:
            if neighbor.owner == current_player and neighbor not in current_list:
                current_list.append(neighbor)
                current_count += self.find_adjecant_territory(current_list, neighbor, current_player)
        return current_count
    
    # hold every combat
    def resolve_combat(self, attacker, defender):
        attacker_rolls = [random.randint(1, 6) for _ in range(attacker.dice_count)]
        defender_rolls = [random.randint(1, 6) for _ in range(defender.dice_count)]
        attacker_sum = sum(attacker_rolls)
        defender_sum = sum(defender_rolls)
        
        if attacker_sum > defender_sum:
            defender.owner = attacker.owner
            defender.dice_count = attacker.dice_count - 1
            attacker.dice_count = 1
            success = True
        else:
            attacker.dice_count = 1
            success = False

        return success, attacker_rolls, defender_rolls
    
    # unclever AI with fixed algorithm
    def primary_AI (self, current_player):
        territories = self.territories
        # identify strong enemies
        strong_enemy = []
        strength = [0]
        for player in self.players:
            player_dice = self.count_player_dice(player)
            if player.territories_num + player_dice >= len(territories) and player != current_player:
                if strength[0] - player.territories_num - player_dice >= len(territories)/ 3:
                    continue
                if player.territories_num + player_dice - strength[0] >= len(territories)/ 3:
                    strong_enemy.clear()
                    strength.clear()
                strong_enemy.append(player)
                strength.append(player.territories_num + player_dice)
                strength.sort(reverse=True)

        # attack
        for territory in territories:
            if territory.owner == current_player and territory.dice_count > 1:
                random_neighbor = territory.neighbor
                random.shuffle(random_neighbor)
                for neighbor in random_neighbor:
                    if territory.dice_count >= neighbor.dice_count and neighbor.owner != current_player:
                        if len(strong_enemy) == 0 or strength[0] - current_player.territories_num - self.count_player_dice(current_player) < len(territories)/ 2 :
                            return True, territory, neighbor
                        else:
                            if neighbor.owner in strong_enemy:
                                return True, territory, neighbor
        return False, None, None
    
    def old_primary_AI (self, current_player):
        territories = self.territories
        # identify strong enemies
        strong_enemy = []
        strength = [0]
        for player in self.players:
            player_dice = self.count_player_dice(player)
            if player.territories_num >= len(territories)/4 and player != current_player:
                if strength[0] - player.territories_num - player_dice >= len(territories)/ 10:
                    continue
                if player.territories_num + player_dice - strength[0] >= len(territories)/ 10:
                    strong_enemy.clear()
                    strength.clear()
                strong_enemy.append(player)
                strength.append(player.territories_num + player_dice)
                strength.sort(reverse=True)

        # attack
        for territory in territories:
            if territory.owner == current_player and territory.dice_count > 1:
                random_neighbor = territory.neighbor
                random.shuffle(random_neighbor)
                for neighbor in random_neighbor:
                    if territory.dice_count >= neighbor.dice_count and neighbor.owner != current_player:
                        if len(strong_enemy) == 0 :
                            return True, territory, neighbor
                        else:
                            if neighbor.owner in strong_enemy:
                                return True, territory, neighbor
        return False, None, None

    # for primary AI to evaluate other players
    def count_player_dice(self, player):
        total_dice = 0
        for territory in self.territories:
            if territory.owner == player:
                total_dice +=  territory.dice_count
        return total_dice + player.undistributed

    # distribute dice after each turn: undistributed dice + current adjacent territory counts (player's score)
    def distribute_dice(self, current_player):
        list = []
        for territory in self.territories:
            if territory.owner == current_player and territory.dice_count < self.max_dice:
                list.append(territory)
                
        current_dice = current_player.territories_num + current_player.undistributed
        current_player.undistributed = 0
        for i in range(current_dice):
            if len(list) == 0:
                current_player.undistributed = min(current_dice - i, self.max_undistributed)
                break
            temp_territory = random.choice(list)
            temp_territory.dice_count += 1
            if temp_territory.dice_count == self.max_dice:
                list.remove(temp_territory)
        
    # check if someone wins
    def check_victory(self):
        for player in self.players:
            if player.territories_num == len(self.territories):
                return player.index
        return None

# calculate center_x, center_y for each hexagon, by ChatGPT
def set_hexagon_center (hexagon, screen_width, screen_height, rows, cols, hexagon_size):

    # Calculate the total width and height of the hexagonal grid
    total_width = cols * 3/2 * hexagon_size
    total_height = (rows + 0.5) * 2 * hexagon_size * math.sin(math.radians(60))

    # Calculate the offset to center the grid on the screen
    offset_x = (screen_width - total_width) / 2
    offset_y = (screen_height - total_height) / 2

    center_x = offset_x + hexagon.col_index * 3/2 * hexagon_size
    center_y = offset_y + hexagon.row_index * (2 * hexagon_size * math.sin(math.radians(60)))
    if hexagon.col_index % 2 == 1:
        center_y += hexagon_size * math.sin(math.radians(60))
    hexagon.center = (center_x, center_y)

# find the border vertex of a territory using recursion
def find_next_vertex(hexagons, current_territory, current_direction, current_hexagon, hexagon_size, cols, direction_dict):

    vertex = generate_hexagon_vertices(current_hexagon.center[0], current_hexagon.center[1], hexagon_size)[(current_direction + 1) % 6]
    if vertex in current_territory.vertex: return
    else: current_territory.vertex.append(vertex)
    
    # either current_direction + 1 in curent_hexagon is the next border, or current_direction + 5 in the hexagon with direction current_direction + 1 is
    if (current_direction + 1) % 6 in current_hexagon.border_direction: find_next_vertex(hexagons, current_territory, (current_direction + 1) % 6, current_hexagon, hexagon_size, cols, direction_dict)
    else:
        temp_dir = {i for i in direction_dict if direction_dict[i] == (current_direction + 1) % 6}
        for i in temp_dir:
            if (current_direction + 5) % 6 in hexagons[ current_hexagon.col_index - i[0] + cols*(current_hexagon.row_index - i[1]) ].border_direction and current_hexagon.col_index % 2 == i[2]:
                find_next_vertex(hexagons, current_territory, (current_direction + 5) % 6, hexagons[ current_hexagon.col_index - i[0] + cols*(current_hexagon.row_index - i[1]) ], hexagon_size, cols, direction_dict)
                break

# Generate hexagon vertices, 0 on the right, rotate clockwise
def generate_hexagon_vertices(center_x, center_y, hexagon_size):
    vertices = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        x = center_x + hexagon_size * math.cos(angle_rad)
        y = center_y + hexagon_size * math.sin(angle_rad)
        vertices.append((x, y))
    return vertices

# display the whole map
def display_map (selected_attacker, selected_defender, current_player, players, territories, button_rect):
    white = (255, 255, 255)
    black = (0, 0, 0)
    dark_gray = (50,50,50)

    screen.fill(white)
    for territory in territories:

        # Draw each territory with player's color
        if territory == selected_attacker:
            territory_color = black  # Attacker color
            font_color = selected_attacker.owner.color
        elif territory == selected_defender:
            territory_color = dark_gray  # Defender color
            font_color = selected_defender.owner.color
        else: 
            territory_color = territory.owner.color
            res=[]
            for i in range(0,len(territory_color)):
                res.append(255 * (1 - (territory.dice_count + 22) / 30) + territory_color[i] * (territory.dice_count + 22) / 30)
            territory_color = tuple(res)
            font_color = black if sum(territory_color) > 400 else white
        pygame.draw.polygon(screen, territory_color, territory.vertex, 0)
        pygame.draw.polygon(screen, black, territory.vertex, 2)

        # Display dice count on each territory
        font = pygame.font.Font(None, 36)
        text = font.render(str(territory.dice_count), True, font_color)
        text_rect = text.get_rect(center=territory.hexagon[0].center)
        screen.blit(text, text_rect)
    
    # Display player indormation on the left
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

    # Display Endturn button
    font = pygame.font.Font(None, 30)
    pygame.draw.rect(screen, black, button_rect)
    text = font.render("End Turn", True, white)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)
        
    pygame.display.flip()

# Add a function to display dice rolls graphically, suggested by ChatGPT
def display_dice_rolls(attacker_color, attacker_rolls, defender_color, defender_rolls):
    black = (0, 0, 0)
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
    #pygame.time.wait(1000)  # Display for x/1000 seconds
    #pygame.display.flip()

# Draw a simple dice, suggested by ChatGPT
def draw_dice(x, y, value, color):

    white = (255, 255, 255)
    black = (0, 0, 0)

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

# check if the point is inside the polygon, suggested by ChatGPT
def is_point_inside_polygon(point, vertices):
    intersections = 0
    prev_vertex = vertices[-1]

    for current_vertex in vertices:
        if (point.y > prev_vertex.y) != (point.y > current_vertex.y):
            if point.x < (current_vertex.x - prev_vertex.x) * (point.y - prev_vertex.y) / (current_vertex.y - prev_vertex.y) + prev_vertex.x:
                intersections += 1
        prev_vertex = current_vertex

    return intersections % 2 == 1

# Click on the attack first, and then click on the defender
def human_move (current_player, players, territories, button_rect):

    selected_attacker = None
    selected_defender = None
    while selected_attacker == None or selected_defender == None:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos): # click on the endturn button
                    return False, None, None 
                for territory in territories:
                    territory_vertices = [pygame.math.Vector2(x, y) for x, y in territory.vertex]
                    mouse_pos = pygame.math.Vector2(mouse_pos)
                    if is_point_inside_polygon(mouse_pos, territory_vertices):
                        if selected_attacker is None: # click on the attacking territory
                            if territory.dice_count > 1 and territory.owner == current_player:
                                selected_attacker = territory
                                display_map(selected_attacker, None, current_player, players, territories, button_rect)
                        elif selected_defender is None: # click on the attacking territory again to cancel
                            if territory == selected_attacker:
                                selected_attacker = None
                                display_map(None, None, current_player, players, territories, button_rect)
                                break
                            elif territory.owner != current_player: # click on the defending territory
                                if territory in selected_attacker.neighbor:
                                    selected_defender = territory
                                    return True, selected_attacker, selected_defender

if __name__ == "__main__":

    # Set up display
    screen_width = 800
    screen_height = 800
    hexagon_size = 20
    button_rect = pygame.Rect(600, 30, 100, 40)

    visualize = False
    if visualize: human = 0
    else: human = -1 # Player[human] is human or the learning AI
    statistic = True
    game = DicewarGame()

    # Initialize pygame (CAN BE COMMENTED OUT)
    if visualize:
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Dice Wars Map")

    if statistic:
        # calculate each element of time used
        start_game_time = time.time()
        total_decide_time = 0
        total_combat_time = 0
        total_calculate_time = 0
        total_reset_time = 0
        mean_index = 0.99
        turns = 1
        mean_turns = 0
        games = 0
        attacks = 0
        mean_attacks = 0
        #wins = [0,0]

    # Game repeated after finished during loops
    while True:
        
        if visualize:
            # Set up each hexagon's center (CAN BE COMMENTED OUT)
            for hexagon in game.hexagons:
                set_hexagon_center(hexagon, screen_width, screen_height, game.rows, game.cols, hexagon_size)

            # Draw each territory (CAN BE COMMENTED OUT)
            for territory in game.territories:
                find_next_vertex( game.hexagons, territory, territory.hexagon[0].border_direction[0] , territory.hexagon[0], hexagon_size, game.cols, game.direction_dict)
        
        if statistic:
            # CALCULATE TIME
            total_game_time = time.time() - start_game_time
            print("--- %s seconds for game---" % total_game_time)
            print("--- %s seconds for decide---" % total_decide_time)
            print("--- %s seconds for combat---" % total_combat_time)
            print("--- %s seconds for calculate---" % total_calculate_time)
            print("--- %s seconds for residue ---" % (total_game_time - total_decide_time - total_combat_time - total_calculate_time - total_reset_time) )
            print("%s games so far" % games)
            print("%s turns in this game" % turns)
            print("average %s turns a game" % mean_turns )
            print("%s attacks in this game" % attacks)
            print("average %s attacks a game" % mean_attacks )
            print("average %s seconds a turn" % (total_game_time / turns))
            #print("wins = " + str(wins[0]) + " , " + str(wins[1]))
            start_game_time = time.time()
            total_decide_time = 0
            total_combat_time = 0
            total_calculate_time = 0
            mean_turns = (turns + games * mean_turns) / (games +1)
            mean_attacks = (attacks + games * mean_attacks) / (games +1)
            turns = 0
            attacks = 0
            games += 1

        # A single game
        game_continues = True
        current_player_queue = 0
        while game_continues:
            if statistic: turns += 1

            current_player = game.players[current_player_queue]
            # delete eliminated players
            if current_player.territories_num == 0:
                game.players.remove(current_player)
                if current_player_queue == len(game.players): current_player_queue = 0
                continue

            # A single turn for current_player
            in_the_same_turn = True
            while in_the_same_turn:

                # check if game ends
                winner = game.check_victory()
                if winner != None:
                    print("Player " + str(winner) +" win!")
                    game_continues = False

                    if statistic: start_reset_time = time.time() # CALCULATE TIME
                    game.reset()
                    if statistic: total_reset_time = (time.time() - start_reset_time) # CALCULATE TIME
                    if statistic: print("--- %s seconds for reset---" % total_reset_time) # CALCULATE TIME

                    #if winner%2 ==0: wins[0] += 1
                    #else: wins[1] +=1

                    break

                if visualize: display_map(None, None, current_player, game.players, game.territories, button_rect)

                # A single move: define selected_attacker and selected_defender
                if current_player.index == human: 
                    in_the_same_turn, selected_attacker, selected_defender = human_move(current_player, game.players, game.territories, button_rect)
                else:
                    if statistic: start_decide_time = time.time() # CALCULATE TIME
                    #if current_player.index % 2 ==0: 
                    in_the_same_turn, selected_attacker, selected_defender = game.primary_AI(current_player)
                    #else: in_the_same_turn, selected_attacker, selected_defender = game.old_primary_AI (current_player)
                    if statistic: total_decide_time = total_decide_time +  (time.time() - start_decide_time) # CALCULATE TIME

                # Attack
                if in_the_same_turn == True:

                    if statistic: start_combat_time = time.time() # CALCULATE TIME

                    if visualize: display_map(selected_attacker, selected_defender, current_player, game.players, game.territories, button_rect)
                    attacking_player = selected_attacker.owner
                    defending_player = selected_defender.owner
                    success, attacker_rolls, defender_rolls = game.resolve_combat(selected_attacker, selected_defender)

                    if statistic: 
                        total_combat_time = total_combat_time +  (time.time() - start_combat_time) # CALCULATE TIME
                        start_calculate_time = time.time() # CALCULATE TIME
                        attacks += 1

                    if visualize: display_dice_rolls(attacking_player.color, attacker_rolls, defending_player.color, defender_rolls)  # (CAN BE COMMENTED OUT)
                    if success: game.calculate_player_territory(attacking_player, defending_player)

                    if statistic: total_calculate_time = total_calculate_time +  (time.time() - start_calculate_time) # CALCULATE TIME

            game.distribute_dice(current_player)

            # switch to next player
            if current_player_queue == len(game.players) - 1: current_player_queue = 0
            else: current_player_queue += 1