from random import randint, sample
from itertools import chain, combinations
import copy
from Game import *
from Player import *
import time
import numpy as np
import pickle


class MCTSNode:
    def __init__(self, player_number, game, q_value, n_value, parent, previous_action, depth, search_depth):
        self.player_number = player_number
        self.game = game
        self.q_value = q_value
        self.n_value = n_value
        self.parent = parent
        self.children = []
        self.previous_action = previous_action
        self.depth = depth + 1
        self.search_depth = search_depth
        # is this the root node?
        if self.parent is None:
            self.is_root = True
        else:
            self.is_root = False
        # generate possible actions
        self.untried_actions = self.get_legal_moves(self.game, self.player_number)
        self.original_legal_moves = self.get_legal_moves(self.game, self.player_number)
        self.is_terminal = self.is_terminal_game(self.game)
        self.expand_count = 0

    # update Q-value for the node from simulation results
    # todo fix this
    def update_q(self):
        player = self.game.player_list[self.player_number]
        self.q_value += player.victory_points

    # update number of times this node has been simulated
    def update_n(self):
        self.n_value += 1

    # check if any player won the game
    def is_terminal_game(self, game):
        for player in game.player_list:
            if player.victory_points > 9:
                print('Found real terminal Game!')
                return True
        # print(f'Game Number {game.turn_number}')
        # print(f'Node Game Number {self.game.turn_number}')
        if game.turn_number - self.game.turn_number > self.search_depth:
            return True
        return False

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def expand(self):
        self.expand_count += 1
        random_idx = randint(0, len(self.untried_actions) - 1)
        next_game, action = self.untried_actions.pop(random_idx)
        # next_game.roll_dice()
        next_game.increment_turn()
        next_player = (self.player_number + 1) % 4
        child = MCTSNode(next_player,
                         next_game,
                         0,
                         0,
                         self,
                         action,
                         self.depth,
                         self.search_depth)
        self.children.append(child)
        return child

    def rollout(self):
        rollout_state = self.game
        current_player = self.player_number
        # roll the dice
        rollout_state.roll_dice()
        while not self.is_terminal_game(rollout_state):
            possible_moves = self.get_legal_moves(rollout_state, current_player)
            possible_moves = (pickle.loads(pickle.dumps(possible_moves, -1)))
            # if len(possible_moves) > 1:
            # rollout_state, action = self.rollout_policy(possible_moves)
            rollout_state, action = self.rollout_policy(possible_moves)
            rollout_state.roll_dice()
            rollout_state.increment_turn()
            # control if adversarial or not
            # current_player = (current_player + 1) % 4
            for i in range(3):
                rollout_state.roll_dice()
        player: Player = rollout_state.player_list[0]
        game = rollout_state
        # Reward Function ===============================================================
        # 0. Winning
        reward = int(player.victory_points >= 10) * 0.4
        # 1. Victory Points
        reward += player.victory_points * 0.05
        # 2. Boolean Switch for having at least one Potential Settlement
        reward += int(len(player.potential_settlements) > 0) * 0.0001
        # 3. Slight bump for more resources
        reward += sum([amount for _, amount in player.resources_dict.items()]) * 0.000001
        # 4. Having access to a variety of resources
        production_centers = player.settlements.union(player.cities)
        resource_types = set()
        for settlement in production_centers:
            adjacent_resources = game.board.get_resources_from_settlement(settlement)
            resource_types.update(adjacent_resources)
        reward += len(resource_types) * 0.0001
        # 5. Drawing from more tiles (higher resource yield)
        resource_yield = 0
        for settlement in player.settlements:
            adjacent_tiles = game.board.get_tile_from_node(settlement)
            for tile in adjacent_tiles:
                if tile in game.board.land_hex_list and game.board.resource_dict[tile] != 'DESERT':
                    resource_yield += 1
        for city in player.cities:
            adjacent_tiles = game.board.get_tile_from_node(settlement)
            for tile in adjacent_tiles:
                if tile in game.board.land_hex_list and game.board.resource_dict[tile] != 'DESERT':
                    resource_yield += 2
        reward += resource_yield * 0.00001
        # ===============================================================================
        return reward

    def rollout_policy(self, possible_moves):
        random_idx = randint(0, len(possible_moves) - 1)
        return possible_moves[random_idx]

    def get_legal_moves(self, game, player_number):
        if game.is_opening:
            legal_moves = get_opening_actions(game, player_number)
        else:
            legal_moves = get_possible_actions(game, player_number)
        if len(legal_moves) == 0:
            legal_moves = [(pickle.loads(pickle.dumps(game, -1)), [])]

        return legal_moves

    def backpropagate(self, result):
        self.n_value += 1
        self.q_value += result
        if self.parent is not None:
            self.parent.backpropagate(result)

    def best_child(self, c_param=1.4):
        choices_weights = np.array([
            (c.q_value / c.n_value) + c_param * np.sqrt((2 * np.log(self.n_value) / c.n_value))
            for c in self.children
        ])
        # print('Number of Children', len(self.children))
        if len(self.children) == 0:
            dc = pickle.loads(pickle.dumps(self, -1))
            dc.player_number = (dc.player_number + 1) % 4
            return dc
        else:
            # randomly return a best choice
            # https://stackoverflow.com/a/42071648
            return self.children[np.random.choice(np.flatnonzero(np.isclose(choices_weights, choices_weights.max())))]
            # return self.children[np.argmax(choices_weights)]


class MCTSAgent:
    # https://github.com/int8/monte-carlo-tree-search/blob/master/mctspy/tree/search.py

    def __init__(self, node, decision_time=20):
        self.game = node.game
        self.decision_time = decision_time
        self.player_number = node.player_number
        self.root = node
        self.current_node = self.root

    def best_action(self, simulations_number=None, total_simulation_seconds=None):
        # handle no actions available
        if len(self.root.original_legal_moves) <= 1:
            return self.root
        if simulations_number is None:
            assert (total_simulation_seconds is not None)
            end_time = time.time() + total_simulation_seconds
            while time.time() < end_time:
                v = self.tree_policy()
                reward = v.rollout()
                v.backpropagate(reward)
        else:
            for idx in range(0, simulations_number):
                if idx % (simulations_number // 10) == 0:
                    print(f'Simulation Number: {idx}')
                v = self.tree_policy()
                reward = v.rollout()
                v.backpropagate(reward)
        # to select best child go for exploitation only
        best_child: MCTSNode = self.root.best_child(0)
        print(f'Number of possible actions: {len(best_child.parent.original_legal_moves)}')
        print(f'Possible actions were: {best_child.parent.original_legal_moves}')
        print(
            f'Best Child has action {best_child.previous_action} with q={best_child.q_value} and n={best_child.n_value}, '
            f'Average Q: {best_child.q_value / best_child.n_value}')
        return best_child

    def tree_policy(self):
        current_node = self.root
        while not current_node.is_terminal:
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node


# static methods
# takes in game and player number, returns list of tuples with game, action_list pairs
def get_opening_actions(game, player_number):
    possible_actions = []
    available_settlements = game.board.available_settlements
    # heuristic 1 - ignore perimeter nodes with 1 adjacent tile
    good_settlements = set(available_settlements) - set(game.board.perimeter_node_list)
    for settlement in good_settlements:
        available_roads = game.board.get_potential_roads_from_location(settlement)
        for road in available_roads:
            dc_game: Game = pickle.loads(pickle.dumps(game, -1))
            build_settlement_dict = {'action': 'put',
                                     'piece_code': 'SETTLEMENT',
                                     'location': settlement,
                                     'player_number': player_number}
            build_road_dict = {'action': 'put',
                               'piece_code': 'ROAD',
                               'location': road,
                               'player_number': player_number}
            settlement_dict = {'player_number': player_number,
                               'piece_code': 1,
                               'location': settlement}
            road_dict = {'player_number': player_number,
                         'piece_code': 0,
                         'location': road}
            dc_game.process_piece_placement(settlement_dict)
            dc_game.process_piece_placement(road_dict)
            action_list = [build_settlement_dict, build_road_dict]
            possible_future = (dc_game, action_list)
            possible_actions.append(possible_future)
    return possible_actions


def get_possible_actions(game, player_number):
    possible_actions = []
    for game, action_list in generate_trade_actions(game, player_number, []):
        for game2, action_list2 in generate_road_actions(game, player_number, action_list):
            for game3, action_list3 in generate_settlement_actions(game2, player_number, action_list2):
                for game4, action_list4 in generate_city_actions(game3, player_number, action_list3):
                    if action_list2 or action_list3 or action_list4:
                        possible_actions.append((game4, action_list4))
                    else:
                        possible_actions.append((game, []))
    return possible_actions


def generate_city_actions(game, player_number, action_list_before):
    player = game.player_list[player_number]
    possible_future_list = []
    # now build cities
    n_cities = player.how_many_cities_can_build()
    city_combination_list = get_subsets(player.settlements, n_cities)
    for city_build_choice in city_combination_list:
        if not city_build_choice:
            possible_future_list.append((game, action_list_before))
        else:
            # make deep copy of game state
            dc_game: Game = pickle.loads(pickle.dumps(game, -1))
            # make move list for this future
            action_list = copy.copy(action_list_before)
            for location in city_build_choice:
                # reflect changes in player
                piece_dict = {'player_number': player_number,
                              'piece_code': 2,
                              'location': location}
                dc_game.process_piece_placement(piece_dict)
                dc_game.player_list[player_number].spend_city_resources()
                # add actions to list
                build_city_dict = {'action': 'put',
                                   'piece_code': 'CITY',
                                   'location': location,
                                   'player_number': player_number}
                action_list.append(build_city_dict)
            possible_future = (dc_game, action_list)
            possible_future_list.append(possible_future)
    return possible_future_list


def generate_settlement_actions(game, player_number, action_list_before):
    player = game.player_list[player_number]
    possible_future_list = []
    # now build settlements
    n_settlements = player.how_many_settlements_can_build()
    settlement_combination_list = get_subsets(player.potential_settlements, n_settlements)
    for settlement_build_choice in settlement_combination_list:
        if not settlement_build_choice:
            possible_future_list.append((game, action_list_before))
        else:
            # make deep copy of game state
            dc_game: Game = pickle.loads(pickle.dumps(game, -1))
            # make move list for this future
            action_list = copy.copy(action_list_before)
            for location in settlement_build_choice:
                # reflect changes in player
                piece_dict = {'player_number': player_number,
                              'piece_code': 1,
                              'location': location}
                dc_game.process_piece_placement(piece_dict)
                dc_game.player_list[player_number].spend_settlement_resources()
                # add actions to list
                build_settlement_dict = {'action': 'put',
                                         'piece_code': 'SETTLEMENT',
                                         'location': location,
                                         'player_number': player_number}
                action_list.append(build_settlement_dict)
            possible_future = (dc_game, action_list)
            possible_future_list.append(possible_future)
    return possible_future_list


def generate_road_actions(game, player_number, action_list_before):
    player = game.player_list[player_number]
    possible_future_list = []
    # now build roads
    n_roads = player.how_many_roads_can_build()
    road_combination_list = get_subsets(player.potential_roads, n_roads)
    for road_build_choice in road_combination_list:
        if not road_build_choice:
            possible_future_list.append((game, action_list_before))
        else:
            # make deep copy of game state
            dc_game: Game = pickle.loads(pickle.dumps(game, -1))
            # make move list for this future
            action_list = copy.copy(action_list_before)
            for location in road_build_choice:
                # reflect changes in player
                piece_dict = {'player_number': player_number,
                              'piece_code': 0,
                              'location': location}
                dc_game.process_piece_placement(piece_dict)
                dc_game.player_list[player_number].spend_road_resources()
                # add actions to list
                build_road_dict = {'action': 'put',
                                   'piece_code': 'ROAD',
                                   'location': location,
                                   'player_number': player_number}
                action_list.append(build_road_dict)
            possible_future = (dc_game, action_list)
            possible_future_list.append(possible_future)
    return possible_future_list


def generate_trade_actions(game, player_number, action_list_before):
    possible_future_list = [(pickle.loads(pickle.dumps(game, -1)), [])]
    player = game.player_list[player_number]
    min_trade_amount = 4
    can_trade = max(player.resources_dict.values()) >= min_trade_amount
    if can_trade:
        resources_can_trade = [resource for resource, amount in player.resources_dict.items()
                               if amount >= min_trade_amount]
        # for now, only consider trading one thing in a turn
        trade_away_combination_list = get_subsets(resources_can_trade, 1)
        for resource_combo in trade_away_combination_list:
            # handle doing nothing
            if not resource_combo:
                possible_future_list.append((game, action_list_before))
            else:
                for resource_away in resource_combo:
                    other_resources = ["ORE", "WOOD", "WHEAT", "SHEEP", "CLAY"]
                    other_resources.remove(resource_away)
                    for resource_receive in other_resources:
                        action_list = copy.copy(action_list_before)
                        dc_game: Game = pickle.loads(pickle.dumps(game, -1))
                        trade_dict = {'action': 'trade',
                                      'resource_away': resource_away,
                                      'resource_receive': resource_receive}
                        action_list.append(trade_dict)
                        dc_game.player_trade(player_number, resource_away, resource_receive)
                        possible_future_list.append((dc_game, action_list))
    return possible_future_list


# https://stackoverflow.com/a/1482316
def get_subsets(iterable, max):
    s = list(iterable)
    output = []
    for r in range(max + 1):
        for combo in combinations(s, r):
            output.append(list(combo))
    return output
