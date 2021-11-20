from utils import *

class Player:
    def __init__(self, player_number):
        self.victory_points = 0
        self.roads = set()
        self.settlements = set()
        self.potential_settlements = set()
        self.potential_roads = set()
        self.player_number = player_number

    def place_road(self, location, not_available_roads):
        self.roads.add(location)
        self.potential_roads.discard(location)
        self.update_potential_roads()
        self.potential_roads = self.potential_roads - not_available_roads

    def place_settlement(self, location, not_available_roads):
        self.settlements.add(location)
        self.potential_settlements.discard(location)
        self.update_potential_roads()
        self.potential_roads = self.potential_roads - not_available_roads

    def update_potential_roads(self):
        for location in self.settlements:
            first_digit = location[2]
            second_digit = location[3]
            if is_even(first_digit) and is_odd(second_digit):
                self.potential_roads.add(create_hex(first_digit, second_digit, -1, -1))
                self.potential_roads.add(create_hex(first_digit, second_digit, 0, 0))
                self.potential_roads.add(create_hex(first_digit, second_digit, 0, -1))
            elif is_odd(first_digit) and is_even(second_digit):
                self.potential_roads.add(create_hex(first_digit, second_digit, -1, 0))
                self.potential_roads.add(create_hex(first_digit, second_digit, 0, 0))
                self.potential_roads.add(create_hex(first_digit, second_digit, -1, -1))
        for location in self.roads:
            first_digit = location[2]
            second_digit = location[3]
            if is_even(first_digit) and is_odd(second_digit):
                self.potential_roads.add(create_hex(first_digit, second_digit, 0, 1))
                self.potential_roads.add(create_hex(first_digit, second_digit, 1, 1))
                self.potential_roads.add(create_hex(first_digit, second_digit, 0, -1))
                self.potential_roads.add(create_hex(first_digit, second_digit, -1, -1))
            if is_odd(first_digit) and is_even(second_digit):
                self.potential_roads.add(create_hex(first_digit, second_digit, -1, -1))
                self.potential_roads.add(create_hex(first_digit, second_digit, -1, 0))
                self.potential_roads.add(create_hex(first_digit, second_digit, 1, 0))
                self.potential_roads.add(create_hex(first_digit, second_digit, 1, 1))
            if is_even(first_digit) and is_even(second_digit):
                self.potential_roads.add(create_hex(first_digit, second_digit, -1, 0))
                self.potential_roads.add(create_hex(first_digit, second_digit, 0, 1))
                self.potential_roads.add(create_hex(first_digit, second_digit, 0, -1))
                self.potential_roads.add(create_hex(first_digit, second_digit, 1, 0))

