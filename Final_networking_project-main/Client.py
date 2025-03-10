from QuicSocket import *


class Client:
    @staticmethod
    def main():
        quic = QuicSocket()
        quic.quic_connect("127.0.0.2", 12001)
        while True:
            if quic.quic_recv() == "finished":
                break


if __name__ == "__main__":
    Client.main()
