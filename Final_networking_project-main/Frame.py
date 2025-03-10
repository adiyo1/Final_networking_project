import pickle

from QuicHeader import *

"""
This class is responsible for the Frame object that is sent over the quic socket.
The frame has a short header that is passed with the streams that the frame contain. 
"""


class Frame:
    #constructor of one frame:
    def __init__(self, streams, connection_id, packet_number):
        self.__header = ShortHeader(connection_id, packet_number)
        self.__streams = streams

    #This method will be used to serialize the frame before sending
    def serialize(self):
        return pickle.dumps(self)

    #static method that is responsible for deserializing the frame back to an object.
    @staticmethod
    def deserialize(serialized_data):
        return pickle.loads(serialized_data)

    def get_header(self):
        return self.__header

    def get_streams(self):
        return self.__streams
