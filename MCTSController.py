from MCTSBot import *
import csv
import os


class MCTSController:
    def __init__(self, player_number):
        self.turn_number = 0
        self.player_number = player_number
        self.turn_counter = 0
        self.game = Game()
        self.resource_code_dict = {1: 'CLAY',
                                   2: 'ORE',
                                   3: 'SHEEP',
                                   4: 'WHEAT',
                                   5: 'WOOD'}
        self.current_best_node: MCTSNode = None
        self.n_moves = 0

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
                    message_list = self.make_2_opening_turns()
                    self.turn_number += 1
                elif self.turn_counter == 8:
                    # make one move
                    message_list = self.make_opening_turn_and_first_turn()
                    self.turn_number += 1
                else:
                    message_list = self.make_opening_turn()
            else:
                message_list = self.execute_turn()
            #self.write_record()
            self.turn_number += 1
            self.game.increment_turn()
        return message_list

    def make_2_opening_turns(self):
        move_list = []
        # calculate from opening
        best_node, action_list = self.think(search_depth=20, n_scale=1000)
        best_node2, action_list2 = self.think(search_depth=20, n_scale=1000, previous_node=best_node)
        for action in action_list:
            move_list.append(self.put_piece(action['location'], action['piece_code']))
        for action in action_list2:
            move_list.append(self.put_piece(action['location'], action['piece_code']))
        return move_list

    def make_opening_turn_and_first_turn(self):
        player = self.game.player_list[self.player_number]
        move_list = []
        # calculate from opening
        best_node, action_list = self.think(search_depth=20, n_scale=1000)
        best_node2, action_list2 = self.think(search_depth=20, n_scale=1000, previous_node=best_node)
        for action in action_list:
            move_list.append(self.put_piece(action['location'], action['piece_code']))
        # prompt dice roll
        move_list.append(['1031'])
        if action_list2 is None:
            move_list.append(['1032'])
            return move_list
        for action in action_list2:
            move_type = action['action']
            if move_type == 'put':
                piece_type = action['piece_code']
                location = action['location']
                if piece_type == 'ROAD':
                    move_list.append(['1043', 0])
                    move_list.append(self.put_piece(location, 'ROAD'))
                elif piece_type == 'SETTLEMENT':
                    move_list.append(['1043', 1])
                    move_list.append(self.put_piece(location, 'SETTLEMENT'))
                elif piece_type == 'CITY':
                    move_list.append(['1043', 2])
                    move_list.append(self.put_piece(location, 'CITY'))
            if move_type == 'trade':
                resource_away = action['resource_away']
                resource_receive = action['resource_receive']
                player.trade_resources(resource_away, resource_receive)
                move_list.append(['1040', resource_away, resource_receive, 4, self.player_number])
        move_list.append(['1032'])
        return move_list

    def make_opening_turn(self):
        move_list = []
        # calculate from opening
        best_node, action_list = self.think(search_depth=20, n_scale=1000)
        for action in action_list:
            move_list.append(self.put_piece(action['location'], action['piece_code']))
        return move_list

    def put_piece(self, location, piece_type):
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
        print(f'Resources: {player.resources_dict}')
        print('Potential Settlements:', player.potential_settlements)
        print('Potential Roads:', player.potential_roads)
        move_list = []
        # prompt dice roll
        move_list.append(['1031'])
        # think
        best_node, action_list = self.think(search_depth=20, n_scale=1000)
        if action_list is None:
            move_list.append(['1032'])
            return move_list
        for action in action_list:
            move_type = action['action']
            if move_type == 'put':
                piece_type = action['piece_code']
                location = action['location']
                if piece_type == 'ROAD':
                    move_list.append(['1043', 0])
                    move_list.append(self.put_piece(location, 'ROAD'))
                elif piece_type == 'SETTLEMENT':
                    move_list.append(['1043', 1])
                    move_list.append(self.put_piece(location, 'SETTLEMENT'))
                elif piece_type == 'CITY':
                    move_list.append(['1043', 2])
                    move_list.append(self.put_piece(location, 'CITY'))
            if move_type == 'trade':
                resource_away = action['resource_away']
                resource_receive = action['resource_receive']
                player.trade_resources(resource_away, resource_receive)
                move_list.append(['1040', resource_away, resource_receive, 4, self.player_number])
        move_list.append(['1032'])
        return move_list

    def think(self, search_depth=10, n_scale=2, max_iter=2000, previous_node=None):
        if previous_node is None:
            game = self.game
        else:
            game = previous_node.game
        root = MCTSNode(self.player_number, game, 0, 0, None, None, 0, search_depth)
        total_moves = len(root.original_legal_moves)
        n = min(total_moves * n_scale, max_iter)
        print(f'Simulating {n} Games at depth {search_depth}')
        mcts_agent: MCTSAgent = MCTSAgent(root)
        # best_node: MCTSNode = mcts_agent.best_action(simulations_number=n)
        best_node: MCTSNode = mcts_agent.best_action(total_simulation_seconds=20)
        action_list = best_node.previous_action
        self.current_best_node = best_node
        self.n_moves = len(root.original_legal_moves)
        return best_node, action_list

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

    def write_record(self):
        file_name = f'./logs/mcts_vs_heuristic/mcts_{self.player_number}.csv'
        file_exists = os.path.isfile(file_name)
        player = self.game.player_list[self.player_number]
        player_resource_dict = player.resources_dict
        with open(file_name, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            if not file_exists:
                print('Writing header')
                writer.writerow(['turn', 'clay', 'ore', 'sheep', 'wheat', 'wood', 'roads',
                                 'settlements', 'cities', 'vp', 'num_moves'])
            writer.writerow([f'{self.turn_counter}', f'{player_resource_dict["CLAY"]}',
                             f'{player_resource_dict["ORE"]}', f'{player_resource_dict["SHEEP"]}',
                             f'{player_resource_dict["WHEAT"]}', f'{player_resource_dict["WOOD"]}',
                             f'{len(player.roads)}', f'{len(player.settlements)}', f'{len(player.cities)}',
                             f'{player.victory_points}',
                             f'{self.n_moves}'])
