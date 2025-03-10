from socket import socket, AF_INET, SOCK_DGRAM
import random
import os
import threading
import time
from Frame import Frame
from QuicHeader import *
from Exceptions import *
from QuicStream import *

"""
This class is the main class of the quic protocol.
in this clas we will define the way in  which data will be sent and received over
the Quic connection. This class will inherit from the socket class to use it functionality.
"""


class QuicSocket(socket):
    """
    Constructor of the quic socket.
    """

    def __init__(self):
        super().__init__(AF_INET, SOCK_DGRAM)
        self.__connection_id = 1000  # random.randint(0, 1500000)
        self.__connected = False
        self.__number_of_packets_sent = 0
        self.__file_streams = {}
        self.__chunk_size = random.randint(1000, 2000)  #1500
        self.__port = None
        self.__server_addr = None
        self.__client_addr = None
        self.__closed = False
        self.__total_bytes = 0
        self.__total_packets = 0
        self.__start_time = 0
        self.__end_time = 0

    """
    This function will be used in the beginning of the code in the server and the client side.
    the server and the client will send their hello messages and the client will send
    which files he wants to receive.
    """

    def quic_connect(self, addr, port):
        self.__server_addr = addr
        self.__port = port
        self.send_client_hello(addr, port)
        timeout = 4
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                data, _ = self.recvfrom(1024)
                if data is None:
                    raise Receive_exceptions("0 bytes received")
                deserialize = Header.deserialize(data)
                if deserialize.get_length() == 'l':  # Long header
                    if deserialize.get_payload() == "Server Hello":
                        self.end_connect()
                        return 1
                    else:
                        raise Not_the_right_payload("payload isn't server hello")
            except TimeOutException as e:
                print(e.message)
        raise TimeoutError("Timeout occurred while waiting for server response")

    """
    This function will be responsible for the receiving part of the Quic protocol.
    Will Receive exception if no data is received.
    """

    def quic_recv(self):
        data_with_header, address = self.recvfrom(65000)
        if (self.__client_addr is None) and (address[0] != self.__server_addr):  #set the client addr in the server side
            self.__client_addr = address[0]
            self.__port = address[1]
        if data_with_header is None:
            raise Receive_exceptions("no data was received")
        if not self.__connected:  #will send the hello server message to the client
            self.__send_server_hello(data_with_header, address)
            return data_with_header, address
        else:
            if address[0] == self.__client_addr:  #server side receives the files that the client are asking for.
                _, temp = data_with_header.decode('utf-8').split("/f")
                self.get_streams_from_files(temp.split(","))
            else:  #in this part of the code we are at the client side and we are receiving data.
                self.__total_packets += 1
                self.__total_bytes += sys.getsizeof(data_with_header)
                return self.data_recv_client_side(data_with_header)

    """
    This function will be responsible for the sending part of the Quic protocol.
    This function will use thread to read from different files at the same 
    time into different streams. After reading the files will be sent inside
    a frame that will be serialized. 
    Will raise exception if there was a problem with the sending part.
    """

    def quic_send(self):
        threads = []
        first_packet_sent = False
        while True:
            if first_packet_sent:
                self.receive_ack()
            flag = False
            for key in self.__file_streams:
                stream = self.__file_streams[key]
                current_position = stream.get_current_position()
                file_size = os.path.getsize(stream.get_file_name())
                if current_position < file_size:
                    thread = threading.Thread(target=self.__read_to_stream, args=(stream,))
                    thread.start()
                    threads.append(thread)
                    flag = True
            if not flag:
                break
            for thread in threads:
                thread.join()
            frame = Frame(self.__file_streams, self.__connection_id, self.__total_packets)
            try:
                self.sendto(frame.serialize(), (self.__client_addr, self.__port))
            except Exceptions as e:
                raise Sendto_exceptions("Exception while sending data")
            first_packet_sent = True
        self.__close_server_side()
        return "finished"

    #### auxiliary functions #####

    """
    The connect part auxiliary functions:
    """

    #function just to print the request for the files that the client is interested in.
    def __ask_for_files(self):
        print("Enter the names of the files that you want to receive from the server\n"
              "[a.txt,b.txt,c.txt,d.txt,e.txt,f.txt,g.txt,h.txt,i.txt,j.txt]\n"
              "Between each file name insert comma without space")

    """
    This method will send the client hello message from the client to the sever to initiate the connection.
    Will raise Sendto_exceptions if the data will have a problem with sending the data.
    """

    def send_client_hello(self, addr, port):
        payload = "Client Hello"
        header = LongHeader(self.__connection_id, 1, payload)
        byte = self.sendto(header.serialize(), (addr, port))
        if byte == 0:
            raise Sendto_exceptions("Error: 0 bytes was sent")
        self.__number_of_packets_sent += 1
        print("Client sent handshake packet.")
        return byte

    """
    This method will send the server hello message from the client to the sever to initiate the connection.
    Will raise Sendto_exceptions if the data will have a problem with sending the data.
    Will raise exceptions if the payload that is received is not the hello clint.
    """

    def __send_server_hello(self, header_rec, address):
        deserialize = Header.deserialize(header_rec)
        if deserialize.get_payload() == "Client Hello":
            payload = "Server Hello"
            header = LongHeader(self.__connection_id, self.__number_of_packets_sent, payload)
            byte = self.sendto(header.serialize(), address)
            if byte == 0:
                raise Sendto_exceptions("0 bytes was sent")
            self.__number_of_packets_sent += 1
            self.__connected = True
        else:
            raise print("Error: payload isn't client hello")

    """
    Will ask for the input in the client side for the files that the client wants.
    will let the client insert the file names from the list that is been determined for the files.
    if the client didnt insert the proper file names 3 times will raise exception.
    will send the files request to the server using send_client_choice() method.
    At the end will start the time of the file transfer proces.
    """

    def end_connect(self):
        file_names = ("a.txt", "b.txt", "c.txt", "d.txt", "e.txt", "f.txt", "g.txt", "h.txt", "i.txt", "j.txt")
        print("The handshake is completed successfully!")
        self.__connected = True
        self.__ask_for_files()
        user_input = ''
        for attempt in range(3):
            user_input = input()
            user_input_split = set(user_input.split(","))
            if user_input_split.issubset(file_names):
                break
            else:
                print("insert valid file names")
            if attempt == 2:
                self.close()
                raise ValueError("Invalid input format. Please provide file names in the format")
        self.get_streams_from_files(user_input.split(","))
        self.send_client_choice(user_input)
        if self.__start_time == 0:
            self.__start_time = time.time()

    """
    This method will get the users input and will send it with the short header.
    if the data will not be sent will raise Sendto_exceptions.
    Than will set the steams dictionary at the client side.
    """

    def send_client_choice(self, user_input):
        header = self.__short_header_builder()
        try:
            self.sendto((header.__str__() + "/f" + user_input).encode('utf-8'),
                        (self.__server_addr, self.__port))
        except Exceptions as e:
            e.print("Socket error occurred:", e)
        self.get_streams_from_files(user_input.split(","))

    """
    This part of auxiliary functions is for the streams part:
    """

    #This method will set the streams of the socket.
    def get_streams_from_files(self, files):
        for file in files:
            self.__file_streams[file] = QuicStream(file)

    def __read_to_stream(self, stream):
        stream.read_from_file(self.__chunk_size)

    def get_streams(self):
        return self.__file_streams

    """
    building the short header.
    """

    def __short_header_builder(self):
        short = ShortHeader(self.__connection_id, self.__number_of_packets_sent)
        return short

    """
    This part of auxiliary functions is for closing the socket connection:
    """
    """
    
    will be responsible for sending the fin message to the client and will
    close the server connection.
    """

    def __close_server_side(self):
        fin = {"fin": "fin"}
        frame = Frame(fin, self.__connection_id, self.__total_packets)
        _bytes = self.sendto(frame.serialize(), (self.__client_addr, self.__port))
        if _bytes == 0:
            raise Sendto_exceptions("0 bytes was sent for fin packet")
        self.close()

    """
    will set the ending time of the process, will print the statistics
    and will close the socket connection on the client side.
    """

    def __close_client_side(self):
        self.__end_time = time.time()
        self.__print_statistics()
        self.close()

    """
    This part of auxiliary functions is for the receiving part of the code:
    """

    """
    This method will be responsible for receiving the data in the client side,
    will use threads to write to the files at the same time.
    after the receiving process is done, this function will send an ack to the 
    server side to notify him that the data received properly.
    """

    def data_recv_client_side(self, data_with_header):
        threads = []
        streams = Frame.deserialize(data_with_header).get_streams()
        if "fin" in streams and streams["fin"] == "fin":
            self.__close_client_side()
            return "finished"
        for key in streams:
            stream = streams[key]
            thread = threading.Thread(target=stream.write_to_file())
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        self.__file_streams = streams
        frame = Frame(streams, self.__connection_id, self.__total_packets)
        _bytes = self.sendto(frame.serialize(), (self.__server_addr, self.__port))
        if _bytes == 0:
            raise Sendto_exceptions("0 bytes was sent for fin packet")

    """
    This function will be responsible for receiving the ack in the server side.
    if the ack wand received properly will raise an exception that ack wasn't received.
    """

    def receive_ack(self):
        ack_packet, _ = self.recvfrom(10000)
        frame = Frame.deserialize(ack_packet)
        streams_rec = frame.get_streams()
        for key in streams_rec:
            if streams_rec[key].get_ack() != 'ack':
                raise Receive_exceptions("Error: didnt receive ack")
        self.__file_streams = streams_rec

    """
    This part of auxiliary functions is for statistics part:
    """

    def __print_statistics(self):
        print("************* STATISTICS FOR THIS RUN *************")
        print("The chunk size for this run will be(random): ", self.__chunk_size)
        total_time = self.__end_time - self.__start_time
        print("The time that this run took: ", total_time)
        for key in self.__file_streams:
            print("Number of bytes sent on", self.__file_streams[key].get_file_name(), "is: ",
                  self.__file_streams[key].get_total_bytes(), "bytes, via", self.__file_streams[key].get_packets_sent(),
                  "packets.")
        for key in self.__file_streams:
            print("In the stream:",
                  self.__file_streams[key].get_file_name(), "The average data sending rate was: ",
                  self.__file_streams[key].get_total_bytes() / total_time,
                  " bytes/seconds.\n",
                  "The average packets rates was:",
                  self.__file_streams[key].get_packets_sent() / total_time,
                  " packets/seconds.")
        print("The average rate of data for all the files was:", self.__total_bytes / total_time, "bytes/seconds.")
        total_rate = self.__total_packets / total_time
        print("The average rate of packets for all the files was: {:.10f} packets/second".format(total_rate))
