class Sendto_exceptions(Exception):
    pass


class Receive_exceptions(Exception):
    pass


class Not_the_right_payload(Exception):
    pass


class None_data_exceptions(Exception):
    pass


class ID_exception(Exception):
    pass


class TimeOutException(Exception):
    def _init_(self, message="Time out exception"):
        self.message = message
        super().__init__(self.message)

    def print_exception(self):
        raise TimeOutException("Time out exception")
