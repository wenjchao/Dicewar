import random

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
