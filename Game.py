from Player import *
from Board import *
from random import randint

class Game:
    def __init__(self):
        self.player_list = [Player(0), Player(1), Player(2), Player(3)]
        self.board = Board()
        self.turn_number = 0
        self.is_opening = True

    def increment_turn(self):
        self.turn_number += 1

    def create_board(self, board_layout):
        print("Creating Board")
        self.board.set_up_board(board_layout)

    def update_potential_settlements(self, player_number, settlements):
        # message applies to all players
        if player_number == -1:
            for player in self.player_list:
                player.potential_settlements = set(settlements[1:])
            self.board.available_settlements = set(settlements[1:])
        # message applies to only one player
        else:
            self.player_list[player_number].potential_settlements = set(settlements[1:])

    def process_piece_placement(self, piece_dict):
        # 1. update board available places
        # 2. update player piece sets
        # 3. update player potential locations
        player_number = piece_dict.get('player_number')
        piece_code = piece_dict.get('piece_code')
        location = piece_dict.get('location')
        if piece_code == 0:
            # road
            # step 1
            self.board.not_available_roads.add(location)
            # step 2 and 3
            for idx, player in enumerate(self.player_list):
                if idx == player_number:
                    player.place_road(location, self.board.not_available_roads)
                else:
                    player.potential_roads.discard(location)
                if self.turn_number > 1:
                    player.update_potential_settlements(self.board.available_settlements)
        elif piece_code == 1:
            # settlement
            # step 1
            self.board.remove_settlement(location)
            self.board.remove_adjacent_nodes(location)
            # step 2 and 3
            for idx, player in enumerate(self.player_list):
                if idx == player_number:
                    player.place_settlement(location, self.board.not_available_roads, self.board)
                else:
                    player.potential_settlements = self.board.available_settlements
                if self.turn_number > 1:
                    player.update_potential_settlements(self.board.available_settlements)
        elif piece_code == 2:
            # city
            # step 1 - don't need to do that here
            # step 2
            player = self.player_list[player_number]
            player.place_city(location)
            # step 3 - don't need to do this
        # check that the opening is over
        if self.is_opening:
            total_settlements = 0
            for player in self.player_list:
                total_settlements += len(player.settlements)
            if total_settlements >= 8:
                self.is_opening = False

    def set_player_resources(self, player_number, resources_dict):
        player = self.player_list[player_number]
        for resource in resources_dict.keys():
            player.resources_dict[resource] = resources_dict[resource]

    def gain_player_resources(self, player_number, resources_dict):
        player = self.player_list[player_number]
        for resource in resources_dict.keys():
            player.resources_dict[resource] += 1

    def lose_player_resources(self, player_number, resources_dict):
        player = self.player_list[player_number]
        for resource in resources_dict.keys():
            player.resources_dict[resource] -= 1

    def player_trade(self, player_number, resource_give, resource_receive, ratio=4):
        self.player_list[player_number].trade_resources(resource_give, resource_receive, ratio)

    def roll_dice(self):
        die_1 = randint(1, 6)
        die_2 = randint(1, 6)
        total_roll = die_1 + die_2
        self.update_from_dice_roll(total_roll)

    def update_from_dice_roll(self, dice_roll):
        #print('Simulated Dice:', dice_roll)
        # get tiles from dice roll
        tile_set = set()
        for tile, number in self.board.num_dict.items():
            if number == dice_roll:
                tile_set.add(tile)
        # get nodes from tiles
        for tile in tile_set:
            node_set = self.board.get_node_from_tile(tile)
            # give resources from tiles
            for player in self.player_list:
                for settlement in player.settlements:
                    if settlement in node_set:
                        player.resources_dict[self.board.resource_dict[tile]] += 1
                        print(f'Player number {player.player_number} received 1 {self.board.resource_dict[tile]}')



