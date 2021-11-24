from Game import *
import random
from MCTSBot import *

class MCTSController:
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
        self.current_best_node = None

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
        return move_list

    def make_opening_turn(self):
        move_list = []
        # calculate from opening
        best_node, action_list = self.think(search_depth=20, n_scale=1000)
        for action in action_list:
            move_list.append(self.put_piece(action['location'], action['piece_code']))
        return move_list
        '''
        # generate random settlement
        potential_settlements = list(self.game.player_list[self.player_number].potential_settlements)
        print('Potential Settlements:', potential_settlements)
        settlement_location_idx = random.randint(0, len(potential_settlements) - 1)
        settlement_location = potential_settlements[settlement_location_idx]
        move_list.append(self.put_piece(settlement_location, 'SETTLEMENT'))
        # generate random road
        potential_roads = list(self.get_potential_roads_from_location(settlement_location))
        print('Potential Roads:', potential_roads)
        road_location_idx = random.randint(0, len(potential_roads) - 1)
        road_location = potential_roads[road_location_idx]
        move_list.append(self.put_piece(road_location, 'ROAD'))
        return move_list
        '''

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
        best_node: MCTSNode = mcts_agent.best_action(simulations_number=n)
        action_list = best_node.previous_action
        return best_node, action_list

    def think_easy(self, search_depth=10):
        root = MCTSNode(self.player_number, self.game, 0, 0, None, None, 0, search_depth)
        total_moves = len(root.original_legal_moves)
        n = total_moves * 2
        print(f'Simulating {n} Games at depth {search_depth}')
        mcts_agent: MCTSAgent = MCTSAgent(root)
        best_node: MCTSNode = mcts_agent.best_action(simulations_number=n)
        action_list = best_node.previous_action
        return action_list

    def think_hard(self, search_depth=10):
        root = MCTSNode(self.player_number, self.game, 0, 0, None, None, 0, search_depth)
        total_moves = len(root.original_legal_moves)
        n = total_moves * 5
        print(f'Simulating {n} Games at depth {search_depth}')
        mcts_agent: MCTSAgent = MCTSAgent(root)
        best_node: MCTSNode = mcts_agent.best_action(simulations_number=n)
        action_list = best_node.previous_action
        return action_list

    def think_really_hard(self):
        root = MCTSNode(self.player_number, self.game, 0, 0, None, None, 0, 100)
        mcts_agent: MCTSAgent = MCTSAgent(root)
        best_node: MCTSNode = mcts_agent.best_action(simulations_number=10000)
        action_list = best_node.previous_action
        return action_list

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
