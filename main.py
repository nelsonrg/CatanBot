import socket
import struct
import io
import random


class CatanBotClient:
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
        self.board = None
        self.potential_settlements = None
        self.game_name = None
        self.player_number = None
        self.turn_number = 0
        self.potential_roads = set()
        self.settlements = []
        self.roads = []
        '''
        self.potential_roads = ['0x00', '0x01', '0x02', '0x03', '0x04', '0x05', '0x06', '0x07',
                                '0x10', '0x12', '0x14', '0x16', '0x18',
                                '0x20', '0x21', '0x22', '0x23', '0x24', '0x25', '0x26', '0x27', '0x28', '0x29',
                                '0x30', '0x32', '0x34', '0x36', '0x38', '0x3a',
                                '0x40', '0x41', '0x42', '0x43', '0x44', '0x45', '0x46', '0x47', '0x48', '0x49', '0x4a',
                                '0x4b',
                                '0x50', '0x52', '0x54', '0x56', '0x58', '0x5a', '0x5c',
                                '0x60', '0x61', '0x62', '0x63', '0x64', '0x65', '0x66', '0x67', '0x68', '0x69', '0x6a',
                                '0x6b', '0x6c', '0x6d',
                                '0x70', '0x72', '0x74', '0x76', '0x78', '0x7a', '0x7c', '0x7e',
                                '0x81', '0x82', '0x83', '0x84', '0x85', '0x86', '0x87', '0x88', '0x89', '0x8a', '0x8b',
                                '0x8c', '0x8d', '0x8e',
                                '0x92', '0x94', '0x96', '0x98', '0x9a', '0x9c', '0x9e',
                                '0xa3', '0xa4', '0xa5', '0xa6', '0xa7', '0xa8', '0xa9', '0xaa', '0xab', '0xac', '0xad',
                                '0xae',
                                '0xb4', '0xb6', '0xb8', '0xba', '0xbc', '0xbe',
                                '0xc5', '0xc6', '0xc7', '0xc8', '0xc9', '0xca', '0xcb', '0xcc', '0xcd', '0xce',
                                '0xd6', '0xd8', '0xda', '0xdc', '0xde',
                                '0xe7', '0xe8', '0xe9', '0xea', '0xeb', '0xec', '0xed', '0xee']
                                '''

    def close(self):
        try:
            self.socket.close()
        except:
            pass

    def run(self, game_name, player_number):
        self.start_connection()
        self.auth()
        self.begin_game(game_name, player_number)
        self.sit_down(game_name)
        self.game_name = game_name
        self.player_number = player_number


        while True:
            server_message = self.read_message_2()
            print('Server:', server_message)
            self.process_message(server_message, game_name)
        '''
        while True:
            try:
                server_message = self.read_message_2()
                print('Server:', server_message)
                self.process_message(server_message, game_name)
            except Exception as e:
                print("* Error receiving/parsing message: " + str(e))
                self.close()
        '''

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
        stream = io.BytesIO(self.socket.recv(256))
        dis = DataInputStream(stream)
        return dis.read_utf()

    def read_message_2(self):
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
            self.update_potential_settlements(message_body)
        elif message_head == '1018':
            # game started message
            print('Game Started!')
        elif message_head == '1026':
            # turn message
            self.turn(message_body)
        elif message_head == '1009':
            # player puts a piece
            self.process_piece_put(message_body)


    def create_board(self, message_body, game_name):
        # remove |gameName, from beginning of str
        left_cut = len(game_name) + 2
        board_layout = message_body[left_cut:]
        board_layout = [x for x in board_layout.split(',')]
        # create the board
        self.board = Board(board_layout)

    def update_potential_settlements(self, message_body):
        # remove |gameName, from beginning of str
        left_cut = len(self.game_name) + 2
        settlements = message_body[left_cut:]
        settlements = [hex(int(x)) for x in settlements.split(',')]
        player_number = int(settlements[0], 16)
        if player_number == self.player_number or player_number == -1:
            self.potential_settlements = settlements[1:]

    def turn(self, message_body):
        message_list = [x for x in message_body.split(',')]
        if int(message_list[1]) == self.player_number:
            print("CatanBot's Turn")
            self.execute_turn()
            self.turn_number += 1

    def execute_turn(self):
        # play randomly for now
        if self.turn_number < 2:
            # place a settlement
            print('Potential Settlements:', self.potential_settlements)
            settlement_location_idx = random.randint(0, len(self.potential_settlements))
            settlement_location = self.potential_settlements[settlement_location_idx]
            print(f'Trying to Build SETTLEMENT at {settlement_location}')
            self.put_piece(settlement_location, 'SETTLEMENT')
            # road_location_idx = random.randint(0, len(self.potential_roads))
            print('Potential Roads:', self.potential_roads)
            road_location_idx = random.randint(0, len(self.potential_roads))
            road_location = list(self.potential_roads)[road_location_idx]
            print(f'Trying to Build ROAD at {road_location}')
            self.put_piece(road_location, 'ROAD')

    def put_piece(self, location, piece_type):
        if piece_type == 'ROAD':
            piece_code = 0
            self.roads.append(location)
        elif piece_type == 'SETTLEMENT':
            piece_code = 1
            self.settlements.append(location)
        elif piece_type == 'CITY':
            piece_code = 2
        else:
            return
        location = int(location, 16)
        message = f'1009|{self.game_name},{self.player_number},{piece_code},{location}'
        self.write_message(message)
        print(f'Built a {piece_type} at {hex(location)}')
        self.update_potential_roads()

    def process_piece_put(self, message_body):
        message_list = [x for x in message_body.split(',')]
        player_number = int(message_list[1])
        piece_code = int(message_list[2])
        location = hex(int(message_list[3]))

        #if player_number == self.player_number:
        #    return

        if piece_code == 0:
            # road
            print('Removing road at location ', location)
            self.remove_road(location)
        elif piece_code == 1:
            # settlement
            print('Removing settlement at location ', location)
            self.remove_settlement(location)
            self.remove_adjacent_nodes(location)

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

    def remove_settlement(self, location):
        if location in self.potential_settlements:
            self.potential_settlements.remove(location)

    def remove_road(self, location):
        if location in self.potential_roads:
            self.potential_roads.remove(location)

    def opening_potential_roads(self, location):
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


class Board:
    def __init__(self, board_layout):
        self.hex_list = ['17', '39', '5b', '7d',
                         '15', '37', '59', '7b', '9d',
                         '13', '35', '57', '79', '9b', 'bd',
                         '11', '33', '55', '77', '99', 'bb', 'dd',
                         '31', '53', '75', '97', 'b9', 'db',
                         '51', '73', '95', 'b7', 'd9',
                         '71', '93', 'b5', 'd7']
        self.board_layout = board_layout
        self.resource_dict = self.parse_resources()
        self.num_dict = self.parse_num()
        # dont worry about robber

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


def is_even(x):
    try:
        x = int(x)
    except ValueError:
        x = ord(x) + 1
    return x % 2 == 0


def is_odd(x):
    try:
        x = int(x)
    except ValueError:
        x = ord(x) + 1
    return not (x % 2 == 0)


def create_hex(first_digit, second_digit, first_shift = 0, second_shift = 0):
    first_digit = int(first_digit, 16) + first_shift
    second_digit = int(second_digit, 16) + second_shift
    return '0x' + hex(first_digit)[-1] + hex(second_digit)[-1]


class DataInputStream:
    """
    Reading from Java DataInputStream format.
    https://github.com/arngarden/python_java_datastream
    """

    def __init__(self, stream):
        self.stream = stream

    def read_boolean(self):
        return struct.unpack('?', self.stream.read(1))[0]

    def read_byte(self):
        return struct.unpack('b', self.stream.read(1))[0]

    def read_unsigned_byte(self):
        return struct.unpack('B', self.stream.read(1))[0]

    def read_char(self):
        return chr(struct.unpack('>H', self.stream.read(2))[0])

    def read_double(self):
        return struct.unpack('>d', self.stream.read(8))[0]

    def read_float(self):
        return struct.unpack('>f', self.stream.read(4))[0]

    def read_short(self):
        return struct.unpack('>h', self.stream.read(2))[0]

    def read_unsigned_short(self):
        return struct.unpack('>H', self.stream.read(2))[0]

    def read_long(self):
        return struct.unpack('>q', self.stream.read(8))[0]

    def read_utf(self):
        utf_length = struct.unpack('>H', self.stream.read(2))[0]
        return self.stream.read(utf_length)

    def read_int(self):
        return struct.unpack('>i', self.stream.read(4))[0]


class DataOutputStream:
    """
    Writing to Java DataInputStream format.
    https://github.com/arngarden/python_java_datastream
    """

    def __init__(self, stream):
        self.stream = stream

    def write_boolean(self, bool):
        self.stream.write(struct.pack('?', bool))

    def write_byte(self, val):
        self.stream.write(struct.pack('b', val))

    def write_unsigned_byte(self, val):
        self.stream.write(struct.pack('B', val))

    def write_char(self, val):
        self.stream.write(struct.pack('>H', ord(val)))

    def write_double(self, val):
        self.stream.write(struct.pack('>d', val))

    def write_float(self, val):
        self.stream.write(struct.pack('>f', val))

    def write_short(self, val):
        self.stream.write(struct.pack('>h', val))

    def write_unsigned_short(self, val):
        self.stream.write(struct.pack('>H', val))

    def write_long(self, val):
        self.stream.write(struct.pack('>q', val))

    def write_utf(self, string):
        self.stream.write(struct.pack('>H', len(string)))
        self.stream.write(string)

    def write_int(self, val):
        self.stream.write(struct.pack('>i', val))


if __name__ == '__main__':
    catan_bot = CatanBotClient("r2d2", "localhost", 8080)
    catan_bot.run('pythonTestGame', 0)
    catan_bot.close()
