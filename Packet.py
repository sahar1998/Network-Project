"""

    This is the format of packets in our network:



                                                **  NEW Packet Format  **
     __________________________________________________________________________________________________________________
    |           Version(2 Bytes)         |         Type(2 Bytes)         |           Length(Long int/4 Bytes)          |
    |------------------------------------------------------------------------------------------------------------------|
    |                                            Source Server IP(8 Bytes)                                             |
    |------------------------------------------------------------------------------------------------------------------|
    |                                           Source Server Port(4 Bytes)                                            |
    |------------------------------------------------------------------------------------------------------------------|
    |                                                    ..........                                                    |
    |                                                       BODY                                                       |
    |                                                    ..........                                                    |
    |__________________________________________________________________________________________________________________|

    Version:
        For now version is 1

    Type:
        1: Register
        2: Advertise
        3: Join
        4: Message
        5: Reunion
                e.g: type = '2' => Advertise packet.
    Length:
        This field shows the character numbers for Body of the packet.

    Server IP/Port:
        We need this field for response packet in non-blocking mode.



    ***** For example: ******

    version = 1                 b'\x00\x01'
    type = 4                    b'\x00\x04'
    length = 12                 b'\x00\x00\x00\x0c'
    ip = '192.168.001.001'      b'\x00\xc0\x00\xa8\x00\x01\x00\x01'
    port = '65000'              b'\x00\x00\\xfd\xe8'
    Body = 'Hello World!'       b'Hello World!'

    Bytes = b'\x00\x01\x00\x04\x00\x00\x00\x0c\x00\xc0\x00\xa8\x00\x01\x00\x01\x00\x00\xfd\xe8Hello World!'




    Packet descriptions:

        Register:
            Request:

                                 ** Body Format **
                 ________________________________________________
                |                  REQ (3 Chars)                 |
                |------------------------------------------------|
                |                  IP (15 Chars)                 |
                |------------------------------------------------|
                |                 Port (5 Chars)                 |
                |________________________________________________|

                For sending IP/Port of the current node to the root to ask if it can register to network or not.

            Response:

                                 ** Body Format **
                 _________________________________________________
                |                  RES (3 Chars)                  |
                |-------------------------------------------------|
                |                  ACK (3 Chars)                  |
                |_________________________________________________|

                For now only should just send an 'ACK' from the root to inform a node that it
                has been registered in the root if the 'Register Request' was successful.

        Advertise:
            Request:

                                ** Body Format **
                 ________________________________________________
                |                  REQ (3 Chars)                 |
                |________________________________________________|

                Nodes for finding the IP/Port of their neighbour peer must send this packet to the root.

            Response:

                                ** Packet Format **
                 ________________________________________________
                |                RES(3 Chars)                    |
                |------------------------------------------------|
                |              Server IP (15 Chars)              |
                |------------------------------------------------|
                |             Server Port (5 Chars)              |
                |________________________________________________|

                Root will response Advertise Request packet with sending IP/Port of the requester peer in this packet.

        Join:

                                ** Body Format **
                 ________________________________________________
                |                 JOIN (4 Chars)                 |
                |________________________________________________|

            New node after getting Advertise Response from root must send this packet to the specified peer
            to tell him that they should connect together; When receiving this packet we should update our
            Client Dictionary in the Stream object.



        Message:
                                ** Body Format **
                 ________________________________________________
                |             Message (#Length Chars)            |
                |________________________________________________|

            The message that want to broadcast to hole network. Right now this type only includes a plain text.

        Reunion:
            Hello:

                                ** Body Format **
                 ________________________________________________
                |                  REQ (3 Chars)                 |
                |------------------------------------------------|
                |           Number of Entries (2 Chars)          |
                |------------------------------------------------|
                |                 IP0 (15 Chars)                 |
                |------------------------------------------------|
                |                Port0 (5 Chars)                 |
                |------------------------------------------------|
                |                 IP1 (15 Chars)                 |
                |------------------------------------------------|
                |                Port1 (5 Chars)                 |
                |------------------------------------------------|
                |                     ...                        |
                |------------------------------------------------|
                |                 IPN (15 Chars)                 |
                |------------------------------------------------|
                |                PortN (5 Chars)                 |
                |________________________________________________|

                In every interval (for now 20 seconds) peers must send this message to the root.
                Every other peer that received this packet should append their (IP, port) to
                the packet and update Length.

            Hello Back:

                                    ** Body Format **
                 ________________________________________________
                |                  REQ (3 Chars)                 |
                |------------------------------------------------|
                |           Number of Entries (2 Chars)          |
                |------------------------------------------------|
                |                 IPN (15 Chars)                 |
                |------------------------------------------------|
                |                PortN (5 Chars)                 |
                |------------------------------------------------|
                |                     ...                        |
                |------------------------------------------------|
                |                 IP1 (15 Chars)                 |
                |------------------------------------------------|
                |                Port1 (5 Chars)                 |
                |------------------------------------------------|
                |                 IP0 (15 Chars)                 |
                |------------------------------------------------|
                |                Port0 (5 Chars)                 |
                |________________________________________________|

                Root in an answer to the Reunion Hello message will send this packet to the target node.
                In this packet, all the nodes (IP, port) exist in order by path traversal to target.


"""
import struct
from tools.Node import Node

class Packet:
    def __init__(self, buf):
        """
        The decoded buffer should convert to a new packet.

        :param buf: Input buffer was just decoded.
        :type buf: bytearray

        """
        self.buf = buf
        header_buf = buf[0:8]
        self.header = struct.unpack('>HHI', header_buf)
        self.version = self.header[0]
        self.type = self.header[1]
        self.length = self.header[2]
        self.header = str(self.version) + "," + str(self.type) + "," + str(self.length)

        format = '>HHIHHHHI' + str(self.length) + 's'
        buf_unpacked = struct.unpack(format, buf)
        self.server_ip = (str(buf_unpacked[3]) + "." + str(buf_unpacked[4]) + "." + str(buf_unpacked[5]) + "." + str(buf_unpacked[6]))
        self.server_port = str(buf_unpacked[7])
        self.body = buf_unpacked[8]

    def get_header(self):
        """

        :return: Packet header
        :rtype: str
        """
        return self.header

    def get_version(self):
        """

        :return: Packet Version
        :rtype: int
        """
        return self.version

    def get_type(self):
        """

        :return: Packet type
        :rtype: int
        """
        return self.type

    def get_length(self):
        """

        :return: Packet length
        :rtype: int
        """
        return self.length

    def get_body(self):
        """

        :return: Packet body
        :rtype: str
        """
        return self.body.decode('utf-8')

    def get_buf(self):
        """
        In this function, we will make our final buffer that represents the Packet with the Struct class methods.

        :return The parsed packet to the network format.
        :rtype: bytearray
        """
        # in nmidunam dorose ya na
        return self.buf

    def get_source_server_ip(self):
        """

        :return: Server IP address for the sender of the packet.
        :rtype: str
        """
        # print("server IP for packet : ", self.server_ip, " ", self.server_ip.decode("utf-8"))
        return Node.parse_ip(self.server_ip)

    def get_source_server_port(self):
        """

        :return: Server Port address for the sender of the packet.
        :rtype: str
        """
        return Node.parse_ip(self.server_port)

    def get_source_server_address(self):
        """

        :return: Server address; The format is like ('192.168.001.001', '05335').
        :rtype: tuple
        """
        return (self.get_source_server_ip(), self.get_source_server_port())


class PacketFactory:
    """
    This class is only for making Packet objects.
    """

    @staticmethod
    def parse_buffer(buffer):  #ToDo : why not make a new instance of Packet class?
        """
        In this function we will make a new Packet from input buffer with struct class methods.

        :param buffer: The buffer that should be parse to a validate packet format

        :return new packet
        :rtype: Packet

        """
        # Parse incoming packets and convert to packet class
        return Packet(buffer)

    @staticmethod
    def new_reunion_packet(type, source_address, nodes_array):   #ToDo : how to know the difference between Hello and HelloBack
        """
        :param type: Reunion Hello (REQ) or Reunion Hello Back (RES)
        :param source_address: IP/Port address of the packet sender.
        :param nodes_array: [(ip0, port0), (ip1, port1), ...] It is the path to the 'destination'.

        :type type: str
        :type source_address: tuple
        :type nodes_array: list

        :return New reunion packet.
        :rtype Packet
        """
        version = 1
        packet_type = 5
        server_ip = source_address[0]
        server_port = source_address[1]
        parts = server_ip.split(".")
        number_of_nodes = len(nodes_array)
        length_of_body = 3 + 2 + 20 * number_of_nodes   # number of chars in body
        number_of_nodes = str(number_of_nodes).zfill(2)
        to_pack = [version, packet_type, length_of_body, int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(server_port), type.encode('utf-8'), number_of_nodes.encode('utf-8')]
        format = '>HHIHHHHI3s2s'
        for node in nodes_array:
            to_pack.append(node[0].encode('utf-8'))
            to_pack.append(node[1].encode('utf-8'))
            format += '15s'
            format += '5s'
        # print("format after adding body : ", format)
        buf = struct.pack(format, *to_pack)
        return Packet(buf)

    @staticmethod
    def new_advertise_packet(type, source_server_address, neighbour=None):
        """
        :param type: Type of Advertise packet
        :param source_server_address Server address of the packet sender.
        :param neighbour: The neighbour for advertise response packet; The format is like ('192.168.001.001', '05335').

        :type type: str
        :type source_server_address: tuple
        :type neighbour: tuple

        :return New advertise packet.
        :rtype Packet

        """
        version = 1
        packet_type = 2
        server_ip = source_server_address[0]
        server_port = source_server_address[1]
        parts = server_ip.split(".")
        if type == 'REQ':
            length_of_body = 3
            format = '>HHIHHHHI3s'
            to_pack = [version, packet_type, length_of_body, int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(server_port),
                       type.encode('utf-8')]

        elif type == 'RES':
            length_of_body = 23
            neighbor_ip = neighbour[0]
            neighbor_port = neighbour[1]
            format = '>HHIHHHHI3s15s5s'
            to_pack = [version, packet_type, length_of_body, int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(server_port),
                       type.encode('utf-8'), neighbor_ip.encode('utf-8'), neighbor_port.encode('utf-8')]

        else:
            print("wrong type for advertise packet")
            return

        buf = struct.pack(format, *to_pack)
        return Packet(buf)

    @staticmethod
    def new_join_packet(source_server_address):
        """
        :param source_server_address: Server address of the packet sender.

        :type source_server_address: tuple

        :return New join packet.
        :rtype Packet

        """
        version = 1
        packet_type = 3
        server_ip = source_server_address[0]
        server_port = source_server_address[1]
        parts = server_ip.split(".")
        join_message = 'JOIN'
        length_of_body = 4
        format = '>HHIHHHHI4s'
        to_pack = [version, packet_type, length_of_body, int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(server_port),
                       join_message.encode('utf-8')]
        buf = struct.pack(format, *to_pack)
        return Packet(buf)

    @staticmethod
    def new_register_packet(type, source_server_address, address=(None, None)):
        """
        :param type: Type of Register packet
        :param source_server_address: Server address of the packet sender.
        :param address: If 'type' is 'request' we need an address; The format is like ('192.168.001.001', '05335').

        :type type: str
        :type source_server_address: tuple
        :type address: tuple

        :return New Register packet.
        :rtype Packet

        """
        version = 1
        packet_type = 1
        server_ip = source_server_address[0]
        server_port = source_server_address[1]
        parts = server_ip.split(".")
        if type == 'REQ':
            IP = address[0]
            PORT = address[1]
            length_of_body = 23
            format = '>HHIHHHHI3s15s5s'
            to_pack = [version, packet_type, length_of_body, int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(server_port),
                       type.encode('utf-8'), IP.encode('utf-8'), PORT.encode('utf-8')]
        elif type == 'RES':
            ack_message = 'ACK'
            length_of_body = 6
            format = '>HHIHHHHI3s3s'
            to_pack = [version, packet_type, length_of_body, int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(server_port),
                       type.encode('utf-8'), ack_message.encode('utf-8')]

        else:
            print("wrong type for register packet")
            return
        # print(to_pack)
        buf = struct.pack(format, *to_pack)
        return Packet(buf)

    @staticmethod
    def new_message_packet(message, source_server_address):
        """
        Packet for sending a broadcast message to the whole network.

        :param message: Our message
        :param source_server_address: Server address of the packet sender.

        :type message: str
        :type source_server_address: tuple

        :return: New Message packet.
        :rtype: Packet
        """
        version = 1
        packet_type = 4
        server_ip = source_server_address[0]
        server_port = source_server_address[1]
        parts = server_ip.split(".")
        length_of_body = len(message)
        format = '>HHIHHHHI' + str(length_of_body) + 's'
        to_pack = [version, packet_type, length_of_body,int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(server_port),
                   message.encode('utf-8')]
        buf = struct.pack(format, *to_pack)
        return Packet(buf)
