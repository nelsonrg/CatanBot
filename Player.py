from utils import *

class Player:
    def __init__(self, player_number):
        self.victory_points = 0
        self.roads = set()
        self.settlements = set()
        self.cities = set()
        self.potential_settlements = set()
        self.potential_roads = set()
        self.player_number = player_number
        self.resources_dict = {'CLAY': 0,
                               'ORE': 0,
                               'SHEEP': 0,
                               'WHEAT': 0,
                               'WOOD': 0}

    def place_road(self, location, not_available_roads):
        self.roads.add(location)
        self.potential_roads.discard(location)
        self.update_potential_roads()
        self.potential_roads = self.potential_roads - not_available_roads

    def place_settlement(self, location, not_available_roads, board):
        # assign initial resources on 2nd settlement
        if len(self.settlements) == 1:
            resource_list = board.get_resources_from_settlement(location)
            for resource in resource_list:
                self.resources_dict[resource] += 1
        self.settlements.add(location)
        self.potential_settlements.discard(location)
        self.update_potential_roads()
        self.potential_roads = self.potential_roads - not_available_roads
        self.victory_points += 1

    def place_city(self, location):
        # only do this if settlement at location already
        if location in self.settlements:
            self.settlements.remove(location)
            self.cities.add(location)
            self.victory_points += 1

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

    def update_potential_settlements(self, available_settlements):
        self.potential_settlements = set()
        for location in self.roads:
            first_digit = location[2]
            second_digit = location[3]
            if is_even(first_digit) and is_odd(second_digit):
                self.potential_settlements.add(create_hex(first_digit, second_digit, 0, 0))
                self.potential_settlements.add(create_hex(first_digit, second_digit, 1, 1))
            if is_odd(first_digit) and is_even(second_digit):
                self.potential_settlements.add(create_hex(first_digit, second_digit, 0, 0))
                self.potential_settlements.add(create_hex(first_digit, second_digit, 1, 1))
            if is_even(first_digit) and is_even(second_digit):
                self.potential_settlements.add(create_hex(first_digit, second_digit, 1, 0))
                self.potential_settlements.add(create_hex(first_digit, second_digit, 0, 1))
        self.potential_settlements.intersection_update(available_settlements)

    def how_many_roads_can_build(self):
        return min(min(self.resources_dict['WOOD'], self.resources_dict['CLAY']), len(self.potential_roads))

    def how_many_settlements_can_build(self):
        return min(min(self.resources_dict['WOOD'], self.resources_dict['CLAY'],
                   self.resources_dict['SHEEP'], self.resources_dict['WHEAT']),
                   len(self.potential_settlements))

    def how_many_cities_can_build(self):
        return min(min(self.resources_dict['ORE'] // 3, self.resources_dict['WHEAT'] // 2),
                   len(self.settlements))

    def trade_resources(self, resource_give, resource_receive, ratio = 4):
        self.resources_dict[resource_give] -= ratio
        self.resources_dict[resource_receive] += 1

    def spend_city_resources(self):
        self.resources_dict['WHEAT'] -= 2
        self.resources_dict['ORE'] -= 3

    def spend_settlement_resources(self):
        self.resources_dict['WOOD'] -= 1
        self.resources_dict['CLAY'] -= 1
        self.resources_dict['SHEEP'] -= 1
        self.resources_dict['WHEAT'] -= 1

    def spend_road_resources(self):
        self.resources_dict['CLAY'] -= 1
        self.resources_dict['WOOD'] -= 1

