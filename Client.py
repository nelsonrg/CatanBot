import socket
import struct
import io
import sys
from MCTSController import *
from RandomController import *
from multiprocessing import Process
import threading
from Controller import *
from Game import *
import random
from time import sleep


class Client:
    scheme = 1
    password = ''
    role = 'P'

    def __init__(self, nick_name, host, port, controller):
        self.nick_name = nick_name
        self.controller = controller
        self.player_number = controller.player_number
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        source_port = int(f'5555{self.player_number}')
        self.socket.bind((f'0.0.0.0', source_port))
        self.socket.settimeout(False)
        self.socket.setblocking(True)
        self.socket.connect((host, port))
        self.resource_code_dict = {1: 'CLAY',
                                   2: 'ORE',
                                   3: 'SHEEP',
                                   4: 'WHEAT',
                                   5: 'WOOD'}

    def run(self, game_name, player_number):
        print('In run()')
        #self.start_connection()
        #self.auth()
        #self.begin_game(game_name, self.player_number)
        #self.sit_down(game_name)
        if player_number == 0:
            self.begin_game(game_name)

        while True:
            server_message = self.read_message()
            print('Server:', server_message)
            self.process_message(server_message, game_name)

    def close(self):
        try:
            self.socket.close()
        except:
            pass

    def start_connection(self):
        message = f"9998|2500,2.5.00,JM20211025,;6pl;sb;sc=2500;,en_US"
        self.write_message(message)

    def auth(self):
        message = f'999|{self.role},{self.nick_name},{self.scheme},{self.host},{self.password}'
        self.write_message(message)

    def begin_game(self, game_name):
        # start game
        message = f'1018|{game_name}'
        self.write_message(message)

    def create_game(self, game_name, player_number):
        # make game
        message = f'1078|{self.nick_name},{self.password},-,P,{game_name},BC=t4,_SC_SANY=f,NT=t,PLB=f,_SC_CLVI=f,' \
                  f'SC=,PLP=f,_EXT_CLI=,SBL=f,_SC_FOG=f,_EXT_GAM=,_SC_3IP=f,N7=t100,_SC_PIRI=f,_SC_SEAC=f,_SC_FTRI=f,' \
                  f'RD=f,_SC_WOND=f,_SC_0RVP=f,_EXT_BOT=,VP=f10,N7C=f,PL=4'
        self.write_message(message)
        # sit down
        message = f'1012|{game_name},{self.nick_name},{player_number},false'
        self.write_message(message)
        # be pepe
        message = f'1058|{game_name},{player_number},26'
        self.write_message(message)

    def join_game(self, game_name):
        message = f'1013|{self.nick_name},{self.password},,{game_name}'
        self.write_message(message)

    def sit_down(self, game_name):
        message = f'1012|{game_name},{self.nick_name},{self.player_number},false'
        self.write_message(message)

    def read_message(self):
        # https://github.com/mir-pucrs/PyCatron/blob/master/Client/Client.py
        def recvwait(size):
            sofar = 0
            r = b''
            while True:
                r += self.socket.recv(size - len(r))
                if len(r) >= size:
                    break
            return r

        try:
            highByte = ord(recvwait(1))
            lowByte = ord(recvwait(1))
            transLength = highByte * 256 + lowByte
            msg = recvwait(transLength)
            return msg
        except socket.timeout:
            print("Error, socket timeout")
            return -1

    def write_message(self, string_message):
        stream = io.BytesIO()
        dos = DataOutputStream(stream)
        dos.write_utf(string_message.encode('utf-8'))
        print('Client:', stream.getvalue())
        self.socket.send(stream.getvalue())

    def process_message(self, server_message, game_name):
        decoded_message = server_message.decode('utf-8')
        message_head = decoded_message[0:4]
        message_body = decoded_message[4:]
        if message_head == '1014':
            # board layout message
            self.create_board(message_body, game_name)
        elif message_head == '1057':
            # potential settlement location message
            self.update_potential_settlements(message_body, game_name)
        elif message_head == '1018':
            # game started message
            print('Game Started!')
        elif message_head == '1026':
            # turn message
            turn_list = self.turn(message_body)
            self.send_player_moves(turn_list, game_name)
        elif message_head == '1009':
            # player puts a piece
            self.process_piece_placement(message_body)
        elif message_head == '1086':
            # player elements/resources
            self.set_player_resources(message_body)
        elif message_head == '1092':
            # dice result resources
            self.dice_result_resources(message_body)

    def create_board(self, message_body, game_name):
        # remove |gameName, from beginning of str
        left_cut = len(game_name) + 2
        board_layout = message_body[left_cut:]
        board_layout = [x for x in board_layout.split(',')]
        # create the board
        self.controller.create_board(board_layout)

    def update_potential_settlements(self, message_body, game_name):
        # remove |gameName, from beginning of str
        left_cut = len(game_name) + 2
        settlements = message_body[left_cut:]
        settlements = [hex(int(x)) for x in settlements.split(',')]
        player_number = int(settlements[0], 16)
        self.controller.update_potential_settlements(player_number, settlements)

    def turn(self, message_body):
        message_list = [x for x in message_body.split(',')]
        return self.controller.turn(int(message_list[1]))

    def send_player_moves(self, turn_list, game_name):
        for move in turn_list:
            move_type = move[0]
            if move_type == '1009':
                # place piece
                player_number = move[1]
                piece_code = move[2]
                location = move[3]
                message = f'1009|{game_name},{player_number},{piece_code},{location}'
            elif move_type == '1043':
                # build request
                piece_code = move[1]
                message = f'1043|{game_name},{piece_code}'
            elif move_type == '1040':
                # player trade
                resource_give = move[1]
                resource_receive = move[2]
                give_amount = move[3]
                player_number = move[4]
                give_dict = {resource: 0 for resource in self.resource_code_dict.values()}
                receive_dict = {resource: 0 for resource in self.resource_code_dict.values()}
                give_dict[resource_give] = give_amount
                # always receive one
                receive_dict[resource_receive] = 1
                message = f'1040|{game_name},{give_dict["CLAY"]},{give_dict["ORE"]},{give_dict["SHEEP"]},' \
                          f'{give_dict["WHEAT"]},{give_dict["WOOD"]},' \
                          f'{receive_dict["CLAY"]},{receive_dict["ORE"]},{receive_dict["SHEEP"]},' \
                          f'{receive_dict["WHEAT"]},{receive_dict["WOOD"]},{player_number}'
            else:
                message = f'{move_type}|{game_name}'
            self.write_message(message)
            # sleep(1)

    def process_piece_placement(self, message_body):
        message_list = [x for x in message_body.split(',')]
        player_number = int(message_list[1])
        piece_code = int(message_list[2])
        location = hex(int(message_list[3]))
        piece_dict = {'player_number': player_number,
                      'piece_code': piece_code,
                      'location': location}
        self.controller.process_piece_placement(piece_dict)

    def set_player_resources(self, message_body):
        # remove game name and first empty value
        message_list = message_body.split('|')[2:]
        player_number = int(message_list[0])
        action = int(message_list[1])
        resource_list = [int(x) for x in message_list[2:]]
        # translate resource list to human-readable format
        resources_dict = dict()
        for idx in range(len(resource_list)):
            if idx % 2 == 0:
                if resource_list[idx] == 1:
                    resources_dict['CLAY'] = resource_list[idx + 1]
                elif resource_list[idx] == 2:
                    resources_dict['ORE'] = resource_list[idx + 1]
                elif resource_list[idx] == 3:
                    resources_dict['SHEEP'] = resource_list[idx + 1]
                elif resource_list[idx] == 4:
                    resources_dict['WHEAT'] = resource_list[idx + 1]
                elif resource_list[idx] == 5:
                    resources_dict['WOOD'] = resource_list[idx + 1]
        self.controller.set_player_resources(player_number, action, resources_dict)

    def dice_result_resources(self, message_body):
        # remove game name
        param_list = [int(x) for x in message_body.split('|')[2:]]
        num_players = param_list.pop(0)
        for player in range(num_players):
            resource_dict = dict()
            player_number = param_list.pop(0)
            total_player_resources = param_list.pop(0)
            while True:
                try:
                    x = param_list.pop(0)
                except:
                    x = 0
                if x == 0:
                    break
                resource_amount = x
                resource_code = param_list.pop(0)
                resource_dict[self.resource_code_dict[resource_code]] = resource_amount
            self.controller.set_player_resources(player_number, 101, resource_dict)


class DataOutputStream:
    """
    Writing to Java DataInputStream format.
    https://github.com/arngarden/python_java_datastream
    """

    def __init__(self, stream):
        self.stream = stream

    def write_utf(self, string):
        self.stream.write(struct.pack('>H', len(string)))
        self.stream.write(string)


if __name__ == '__main__':
    # expects a single argument with client type of mcts or random
    args = sys.argv[1:]
    client_type = args[0]
    player_number = int(args[1])
    game_name = args[2]
    print(f'type:{client_type}, player:{player_number}, game_name:{game_name}')
    client = None
    if client_type == 'random':
        client = Client(f'RandomBot{player_number}', 'localhost', 8080, RandomController(player_number=player_number))
    elif client_type == 'mcts':
        client = Client(f'CatanBot', 'localhost', 8080, MCTSController(player_number=player_number))
    else:
        print('Unrecognized Args')
        exit(1)
    # start playing
    client.start_connection()
    client.auth()
    if player_number == 0:
        client.create_game(game_name, player_number)
    else:
        client.join_game(game_name)
    client.sit_down(game_name)
    if player_number == 0:
        sleep(10)
        client.run(game_name, player_number)
    else:
        client.run(game_name, player_number)
    client.close()





# if __name__ == '__main__':
#     # set up the clients
#     mcts_client = Client("CatanBot", "localhost", 8080, MCTSController(player_number=0))
#     random_client1 = Client("RandomBot1", "localhost", 8080, RandomController(player_number=1))
#     random_client2 = Client("RandomBot2", "localhost", 8080, RandomController(player_number=2))
#     random_client3 = Client("RandomBot3", "localhost", 8080, RandomController(player_number=3))
#     client_list = [mcts_client, random_client1, random_client2, random_client3]
#     # connect and authorize
#     for client in client_list:
#         client.start_connection()
#         client.auth()
#     # begin the game
#     game_name = 'BotBattle'
#     mcts_client.create_game(game_name, 0)
#     # other bots join
#     for client in client_list[1:]:
#         client.join_game(game_name)
#     # everyone sit
#     for client in client_list:
#         client.sit_down(game_name)
#     process_list = []
#     # for client in client_list:
#     #     print('Creating Processes')
#     #     process_list.append(Process(target=client.run, args=(game_name,)))
#     # for process in process_list:
#     #     print('Starting Processes')
#     #     process.start()
#     # for process in process_list:
#     #     print('Joining Processes')
#     #     process.join()
#     thread_list = []
#     for client in client_list:
#         print('Creating Thread')
#         thread_list.append(threading.Thread(target=client.run, args=(game_name,)))
#     for thread in thread_list:
#         thread.start()
#     sleep(5)
#     mcts_client.begin_game(game_name)
#     for client in client_list:
#         client.close()
