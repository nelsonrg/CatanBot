from utils import *

class Board:
    def __init__(self):
        self.hex_list = ['17', '39', '5b', '7d',
                         '15', '37', '59', '7b', '9d',
                         '13', '35', '57', '79', '9b', 'bd',
                         '11', '33', '55', '77', '99', 'bb', 'dd',
                         '31', '53', '75', '97', 'b9', 'db',
                         '51', '73', '95', 'b7', 'd9',
                         '71', '93', 'b5', 'd7']
        self.board_layout = None
        self.resource_dict = None
        self.num_dict = None
        self.available_settlements = set()
        self.not_available_roads = {'0x28', '0x4a', '0x6c', '0x8d', '0xad', '0xcd', '0xdc', '0xda', '0xd8',
                                    '0xc6', '0xa4', '0x82', '0x61', '0x41', '0x21', '0x12', '0x14', '0x16'}
        # dont worry about robber

    def set_up_board(self, board_layout):
        self.board_layout = board_layout
        self.resource_dict = self.parse_resources()
        self.num_dict = self.parse_num()

    def parse_resources(self):
        # first 37 elements are resource and port info
        resources = [x for x in self.board_layout[:37]]
        # should convert to hex for ports at some point
        resource_dict = {}
        for idx, tile in enumerate(resources):
            if tile == 0:
                resource_dict[self.hex_list[idx]] = 'DESERT'
            elif tile == 1:
                resource_dict[self.hex_list[idx]] = 'CLAY'
            elif tile == 2:
                resource_dict[self.hex_list[idx]] = 'ORE'
            elif tile == 3:
                resource_dict[self.hex_list[idx]] = 'SHEEP'
            elif tile == 4:
                resource_dict[self.hex_list[idx]] = 'WHEAT'
            elif tile == 5:
                resource_dict[self.hex_list[idx]] = 'WOOD'
            elif tile == 6:
                resource_dict[self.hex_list[idx]] = 'WATER'
            else:
                # TODO: add port logic
                resource_dict[self.hex_list[idx]] = 'PORT'
        return resource_dict

    def parse_num(self):
        # 38-75 are numbers associated with each tile
        numbers = [x for x in self.board_layout[37:74]]
        # should convert to hex for ports at some point
        num_dict = {}
        for idx, num in enumerate(numbers):
            num_dict[self.hex_list[idx]] = num
        return num_dict

    def remove_settlement(self, location):
        if location in self.available_settlements:
            self.available_settlements.remove(location)

    def remove_adjacent_nodes(self, location):
        # reference page 186 of original PhD thesis
        first_digit = location[2]
        second_digit = location[3]
        if is_even(first_digit) and is_odd(second_digit):
            self.remove_settlement(create_hex(first_digit, second_digit, -1, -1))
            self.remove_settlement(create_hex(first_digit, second_digit, 1, 1))
            self.remove_settlement(create_hex(first_digit, second_digit, 1, -1))
        elif is_odd(first_digit) and is_even(second_digit):
            self.remove_settlement(create_hex(first_digit, second_digit, -1, 1))
            self.remove_settlement(create_hex(first_digit, second_digit, 1, 1))
            self.remove_settlement(create_hex(first_digit, second_digit, -1, -1))
