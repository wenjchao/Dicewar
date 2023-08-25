import pygame
import random
import dicewar_initialization
import dicewar_AI

# Initialize pygame
pygame.init()

# Set up display
screen_width = dicewar_initialization.screen_width
screen_height = dicewar_initialization.screen_height
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dice Wars Map")

# Set up parameters
white = (255, 255, 255)
black = (0, 0, 0)
dark_gray = (50,50,50)
max_dice = 8
max_undistributed = 50
button_rect = pygame.Rect(600, 30, 100, 40)
human = -1

# Run the game
def game():
    players, territories = dicewar_initialization.initialize()
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

game()

# Quit pygame
pygame.quit()
