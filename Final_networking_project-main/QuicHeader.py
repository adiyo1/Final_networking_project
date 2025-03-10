import pickle
from abc import ABC

"""
This class will represent an Header object that will be sent with each packet of data.
2 class will inherit from this class. The short header and the long header.
Will have serialize and deserialize methods that will use pickle module to serialize and deserialize data.
"""


class Header(ABC):
    def __init__(self):
        pass

    def serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def deserialize(serialized_data):
        return pickle.loads(serialized_data)


"""
The long header will be sent within the connection part of the code, 
Will have payload for the client and the server hello message.
"""


class LongHeader(Header):
    def __init__(self, connection_id, packet_number, payload):
        super().__init__()
        self.__length = 'l'
        self.__connection_id = connection_id
        self.__packet_number = packet_number
        self.__payload = payload

    def get_length(self):
        return self.__length

    def get_payload(self):
        return self.__payload


"""
The short header will be sent with packets that are sent after the connection part of the code.
Client request, the files data packets from the server, the acks from the client and fin packet to end the connection.
"""


class ShortHeader(Header):
    def __init__(self, connection_id, packet_number):
        super().__init__()
        self.__length = 's'
        self.__packet_number = packet_number
        self.__connection_id = connection_id

    def get_length(self):
        return self.__length
