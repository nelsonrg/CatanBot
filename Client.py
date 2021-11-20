import socket
import struct
import io
from Controller import *
from Game import *
import random


class Client:
    scheme = 1
    password = ''
    role = 'P'

    def __init__(self, nick_name, host, port):
        self.nick_name = nick_name
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(False)
        self.socket.setblocking(True)
        self.socket.connect((host, port))
        self.controller = Controller()

    def run(self, game_name, player_number):
        self.start_connection()
        self.auth()
        self.begin_game(game_name, player_number)
        self.sit_down(game_name)

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

    def begin_game(self, game_name, player_number):
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
        # start game
        message = f'1018|{game_name}'
        self.write_message(message)

    def join_game(self, game_name):
        message = f'1013|{self.nick_name},{self.password},,{game_name}'
        self.write_message(message)

    def sit_down(self, game_name):
        message = f'1012|{game_name},{self.nick_name},0,false'
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
                player_number = move[1]
                piece_code = move[2]
                location = move[3]
                message = f'1009|{game_name},{player_number},{piece_code},{location}'
                self.write_message(message)
            elif move_type == '1072':
                player_number = move[1]
                message = f'1072|{game_name},{player_number}'

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
                    resources_dict['CLAY'] = resource_list[idx+1]
                elif resource_list[idx] == 2:
                    resources_dict['ORE'] = resource_list[idx + 1]
                elif resource_list[idx] == 3:
                    resources_dict['SHEEP'] = resource_list[idx + 1]
                elif resource_list[idx] == 4:
                    resources_dict['WHEAT'] = resource_list[idx + 1]
                elif resource_list[idx] == 5:
                    resources_dict['WOOD'] = resource_list[idx + 1]
        self.controller.set_player_resources(player_number, action, resources_dict)





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
    client = Client("CatanBot", "localhost", 8080)
    client.run('pythonTestGame', 0)
    client.close()
