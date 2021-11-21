from Player import *
from Board import *

class Game:
    def __init__(self):
        self.player_list = [Player(0), Player(1), Player(2), Player(3), Player(4)]
        self.board = Board()
        self.turn_number = 0

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
                    player.place_settlement(location, self.board.not_available_roads)
                else:
                    player.potential_settlements = self.board.available_settlements
                if self.turn_number > 1:
                    player.update_potential_settlements(self.board.available_settlements)

    def set_player_resources(self, player_number, resources_dict):
        player = self.player_list[player_number]
        for resource in resources_dict.keys():
            player.resources_dict[resource] += resources_dict[resource]

    def gain_player_resources(self, player_number, resources_dict):
        player = self.player_list[player_number]
        for resource in resources_dict.keys():
            player.resources_dict[resource] += 1

    def lose_player_resources(self, player_number, resources_dict):
        player = self.player_list[player_number]
        for resource in resources_dict.keys():
            player.resources_dict[resource] -= 1


