from Game import *
import random

class Controller:
    def __init__(self):
        self.turn_number = 0
        self.player_number = 0
        self.game = Game()

    def create_board(self, board_layout):
        self.game.create_board(board_layout)

    def update_potential_settlements(self, player_number, settlements):
        self.game.update_potential_settlements(player_number, settlements)

    def turn(self, player_number):
        message_list = []
        if player_number == self.player_number:
            print("CatanBot's Turn")
            if self.turn_number < 2:
                message_list = self.make_opening_turn()
            else:
                message_list = self.execute_turn()
            self.turn_number += 1
        return message_list

    def make_opening_turn(self):
        move_list = []
        # generate random settlement
        potential_settlements = list(self.game.player_list[self.player_number].potential_settlements)
        print('Potential Settlements:', potential_settlements)
        settlement_location_idx = random.randint(0, len(potential_settlements)-1)
        settlement_location = potential_settlements[settlement_location_idx]
        move_list.append(self.put_piece(settlement_location, 'SETTLEMENT'))
        # generate random road
        potential_roads = list(self.get_potential_roads_from_location(settlement_location))
        print('Potential Roads:', potential_roads)
        road_location_idx = random.randint(0, len(potential_roads)-1)
        road_location = potential_roads[road_location_idx]
        move_list.append(self.put_piece(road_location, 'ROAD'))
        return move_list

    def put_piece(self, location, piece_type):
        player = self.game.player_list[self.player_number]
        piece_code = None
        if piece_type == 'ROAD':
            piece_code = 0
        elif piece_type == 'SETTLEMENT':
            piece_code = 1
        elif piece_type == 'CITY':
            piece_code = 2
        location = int(location, 16)
        print(f'Trying to build a {piece_type} at {hex(location)}')
        return ['1009', self.player_number, piece_code, location]

    def execute_turn(self):
        return 0

    def process_piece_placement(self, piece_dict):
        player_number = piece_dict.get('player_number')
        piece_code = piece_dict.get('piece_code')
        location = piece_dict.get('location')
        piece_name = None
        if piece_code == 0:
            # road
            piece_name = 'ROAD'
        elif piece_code == 1:
            # settlement
            piece_name = 'SETTLEMENT'
        self.game.process_piece_placement(piece_dict)
        print(f'Placing Player Number {player_number} {piece_name} at {location}')

    def get_potential_roads_from_location(self, location):
        potential_roads = set()
        first_digit = location[2]
        second_digit = location[3]
        if is_even(first_digit) and is_odd(second_digit):
            potential_roads.add(create_hex(first_digit, second_digit, -1, -1))
            potential_roads.add(create_hex(first_digit, second_digit, 0, 0))
            potential_roads.add(create_hex(first_digit, second_digit, 0, -1))
        elif is_odd(first_digit) and is_even(second_digit):
            potential_roads.add(create_hex(first_digit, second_digit, -1, 0))
            potential_roads.add(create_hex(first_digit, second_digit, 0, 0))
            potential_roads.add(create_hex(first_digit, second_digit, -1, -1))
        return potential_roads - self.game.board.not_available_roads



