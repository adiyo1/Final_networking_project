import string
from QuicSocket import *


def create_text_files():
    file_names = ['a.txt', 'b.txt', 'c.txt', 'd.txt', 'e.txt', 'f.txt', 'g.txt', 'h.txt', 'i.txt', 'j.txt']
    for file_name in file_names:
        with open(file_name, 'w') as file:
            random_text = ''.join(
                random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=1024 * 1024))
            file.write(random_text)


class Server:
    @staticmethod
    def main():
        create_text_files()
        serverPort = 12001
        quic = QuicSocket()
        quic.bind(("127.0.0.2", serverPort))
        print("The server is ready...")
        connected = False
        data = None
        while True:
            if connected:
                data = quic.quic_recv()
                flag = quic.quic_send()
                if flag == "finished":
                    break
            else:
                quic.quic_recv()
                connected = True


if __name__ == '__main__':
    Server().main()
