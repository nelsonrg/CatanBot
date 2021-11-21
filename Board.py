from utils import *


class Board:
    def __init__(self):
        self.hex_list = ['0x17', '0x39', '0x5b', '0x7d',
                         '0x15', '0x37', '0x59', '0x7b', '0x9d',
                         '0x13', '0x35', '0x57', '0x79', '0x9b', '0xbd',
                         '0x11', '0x33', '0x55', '0x77', '0x99', '0xbb', '0xdd',
                         '0x31', '0x53', '0x75', '0x97', '0xb9', '0xdb',
                         '0x51', '0x73', '0x95', '0xb7', '0xd9',
                         '0x71', '0x93', '0xb5', '0xd7']
        self.land_hex_list = ['0x37', '0x59', '0x7b',
                              '0x35', '0x57', '0x79', '0x9b',
                              '0x33', '0x55', '0x77', '0x99', '0xbb',
                              '0x53', '0x75', '0x97', '0xb9',
                              '0x73', '0x95', '0xb7']
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
        resources = [int(x) for x in self.board_layout[:37]]
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

    def get_tile_from_node(self, location):
        # reference page 186 of original PhD thesis
        first_digit = location[2]
        second_digit = location[3]
        tile_set = set()
        if is_even(first_digit) and is_odd(second_digit):
            tile_set.add(create_hex(first_digit, second_digit, -1, 0))
            tile_set.add(create_hex(first_digit, second_digit, -1, -1))
            tile_set.add(create_hex(first_digit, second_digit, 1, 0))
        elif is_odd(first_digit) and is_even(second_digit):
            tile_set.add(create_hex(first_digit, second_digit, -2, -1))
            tile_set.add(create_hex(first_digit, second_digit, 0, -1))
            tile_set.add(create_hex(first_digit, second_digit, 0, 1))
        return tile_set

    def get_resources_from_settlement(self, location):
        tile_set = self.get_tile_from_node(location)
        return [self.resource_dict[tile] for tile in tile_set if tile in self.land_hex_list
                and self.resource_dict[tile] != 'DESERT']
