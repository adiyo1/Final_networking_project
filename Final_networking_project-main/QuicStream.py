import pickle
import sys
import time

import Exceptions

"""
This class is our QuicStream class, the streams are going to be the objects
that will read and write from and to files in the server and the client sides.
"""


class QuicStream:
    def __init__(self, filename):
        self.__filename = filename
        self.__data = ""
        self.__current_position = 0
        self.__size_of_short_header = 60
        self.__total_bytes = 0
        self.__packets_sent = 0

    """
    method to read from a file to the stream that will be sent to the client.
    this method will start to read from the file from the current position that is 
    held inside the stream values.
    """

    def read_from_file(self, chunk_size):
        try:
            with open(self.__filename, 'r') as file:
                file.seek(self.__current_position)
                self.__data = file.read(chunk_size - sys.getsizeof(self.__filename) - self.__size_of_short_header)
                if self.__data is None:
                    raise Exceptions.None_data_exceptions("Error: the data is None")
                self.__current_position += chunk_size - sys.getsizeof(self.__filename) - self.__size_of_short_header
                file.close()
        except Exceptions as e:
            raise e("File cannot be opened")

    """
    method to write to file in the client side.
    after the data has been written, the stream will contain an ack message the 
    will be sent back to the server if the data has been sent correctly.
    """

    def write_to_file(self):
        try:
            self.__total_bytes += sys.getsizeof(self.__data)
            self.__packets_sent += 1
            with open("client." + self.__filename, "a") as file:
                file.write(self.__data)
                file.close()
                self.__data = "ack"
        except Exceptions as e:
            raise e("File cannot be opened")

    def get_file_name(self):
        return self.__filename

    def get_current_position(self):
        return self.__current_position

    def get_total_bytes(self):
        return self.__total_bytes

    def get_packets_sent(self):
        return self.__packets_sent

    def get_ack(self):
        return self.__data
