import filecmp
import unittest
from unittest.mock import Mock, patch

from Server import *
from Client import *
from Frame import *
from QuicSocket import *
from QuicHeader import *
from QuicStream import *
from unittest import mock


class Test_connect(unittest.TestCase):
    """
    this test will test the client hello method, we want to check that the
    client hello function is working correctly and sends the hello message to the server.
    """

    def test_client_hello(self):
        quic_sock_for_server = QuicSocket()
        quic_sock_for_client = QuicSocket()
        quic_sock_for_server.bind(("127.0.0.2", 12005))
        quic_sock_for_client.send_client_hello("127.0.0.2", 12005)
        while True:
            data, addr = quic_sock_for_server.quic_recv()
            exp = Header.deserialize(data).get_payload()
            self.assertEqual(exp, "Client Hello")
            quic_sock_for_server.close()
            quic_sock_for_client.close()
            break

    """
    this test will test the server hello method, we want to check that the 
    server hello function is working correctly and sends the servers message to the client.
    """

    def test_server_hello(self):
        quic_sock_for_server = QuicSocket()
        quic_sock_for_client = QuicSocket()
        quic_sock_for_server.bind(("127.0.0.2", 12005))
        quic_sock_for_client.send_client_hello("127.0.0.2", 12005)
        while True:
            data, addr = quic_sock_for_server.quic_recv()
            if Header.deserialize(data).get_payload() == "Client Hello":
                break
        while True:
            data = quic_sock_for_client.recv(10000)
            exp = Header.deserialize(data).get_payload()
            self.assertEqual(exp, "Server Hello")
            quic_sock_for_server.close()
            quic_sock_for_client.close()
            break

    '''
    this test will check that tif the client didnt enter valid file name than error will be raised.
    while running insert 'a' 'a' 'a' to check that the exception is rising.
    '''

    def test_end_connect(self):
        quic = QuicSocket()
        with self.assertRaisesRegex(ValueError, "Invalid input format. Please provide file names in the format"):
            quic.end_connect()

    '''
    this test will check that the get_streams_from_files function is returning the correct streams.
    '''

    def test_get_streams_from_files(self):
        quic = QuicSocket()
        files = [None] * (115 - 97)
        j = 0
        for i in range(97, 115):
            files[j] = chr(i) + ".txt"
            j += 1
        quic.get_streams_from_files(files)
        quic.close()
        for file_name in files:
            self.assertEqual(quic.get_streams()[file_name].get_file_name(), file_name)


class Test_rec(unittest.TestCase):
    """
    this test will test the rec method, will test that the rec method is working correctly and the
    files in the server and the client are the same.
    To run this test firstly please run the server and the client files once to create the files.
    While running pleas make sure that in the client side you ask for all the files from the server.
    """

    def test_file_compare(self):
        for m in range(97, 107):
            server_side = chr(m) + ".txt"
            client_side = "client." + chr(m) + ".txt"
            self.assertTrue(filecmp.cmp(server_side, client_side))
