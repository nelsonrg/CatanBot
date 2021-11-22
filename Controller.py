from Game import *
import random

class Controller:
    def __init__(self):
        self.turn_number = 0
        self.player_number = 0
        self.turn_counter = 0
        self.game = Game()
        self.resource_code_dict = {1: 'CLAY',
                                   2: 'ORE',
                                   3: 'SHEEP',
                                   4: 'WHEAT',
                                   5: 'WOOD'}

    def create_board(self, board_layout):
        self.game.create_board(board_layout)

    def update_potential_settlements(self, player_number, settlements):
        self.game.update_potential_settlements(player_number, settlements)

    def turn(self, player_number):
        self.turn_counter += 1
        message_list = []
        if player_number == self.player_number:
            print("CatanBot's Turn")
            if self.turn_number < 2:
                if self.turn_counter == 4:
                    # make two moves
                    message_list = self.make_opening_turn() + self.make_opening_turn()
                    self.turn_number += 1
                elif self.turn_counter == 8:
                    # make one move
                    message_list = self.make_opening_turn() + self.execute_turn()
                    self.turn_number += 1
                else:
                    message_list = self.make_opening_turn()
            else:
                message_list = self.execute_turn()
            self.turn_number += 1
            self.game.increment_turn()
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
        player = self.game.player_list[self.player_number]
        print('Potential Settlements:', player.potential_settlements)
        print('Potential Roads:', player.potential_roads)
        move_list = []
        # prompt dice roll
        move_list.append(['1031'])
        # build cities first if you can
        n_cities = player.how_many_cities_can_build()
        for i in range(n_cities):
            random_city_location = random.sample(player.settlements, 1)[0]
            move_list.append(['1043', 2])
            move_list.append(self.put_piece(random_city_location, 'CITY'))
        # how many settlements
        n_settlements = player.how_many_settlements_can_build()
        n_roads = player.how_many_roads_can_build()
        can_build = (n_roads + n_settlements) > 0
        if can_build:
            potential_settlements = list(self.game.player_list[self.player_number].potential_settlements)
            potential_roads = list(self.game.player_list[self.player_number].potential_roads)
            n_moves = n_roads + n_settlements  # todo make better logic later
            try:
                choice = random.randint(0, n_moves)
            except:
                choice = 0
            print('Random Choice', choice)
            if choice == 0:
                # no move
                x = 0
            elif n_settlements != 0:
                # build all settlements
                num_settlements_to_build = random.randint(1, n_settlements)
                random_location_list = random.sample(player.potential_settlements, num_settlements_to_build)
                for location in random_location_list:
                    move_list.append(['1043', 1])
                    move_list.append(self.put_piece(location, 'SETTLEMENT'))
            else:
                # build all roads
                num_roads_to_build = random.randint(1, n_roads)
                random_location_list = random.sample(player.potential_roads, num_roads_to_build)
                for location in random_location_list:
                    move_list.append(['1043', 0])
                    move_list.append(self.put_piece(location, 'ROAD'))
        # randomly trade if have more than 5 of one resource
        min_trade_amount = 5
        can_trade = max(player.resources_dict.values()) > min_trade_amount
        if can_trade:
            resources_can_trade = [resource for resource, amount in player.resources_dict.items()
                                   if amount > min_trade_amount]
            for resource in resources_can_trade:
                do_trade = random.randint(0, 1)
                resource_receive = self.resource_code_dict[random.randint(1, 5)]
                if do_trade:
                    player.trade_resources(resource, resource_receive)
                    move_list.append(['1040', resource, resource_receive, 4, self.player_number])
        # end turn
        move_list.append(['1032'])
        return move_list

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
        elif piece_code == 2:
            # city
            piece_name = 'CITY'
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

    def set_player_resources(self, player_number, action, resources_dict):
        if action == 100:
            # SET
            self.game.set_player_resources(player_number, resources_dict)
        elif action == 101:
            # GAIN
            self.game.gain_player_resources(player_number, resources_dict)
        elif action == 102:
            # LOSE
            self.game.lose_player_resources(player_number, resources_dict)



