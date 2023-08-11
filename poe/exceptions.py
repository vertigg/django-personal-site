from rest_framework import status


class PoEClientException(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, msg, status_code=None):
        super().__init__(msg)
        self.msg = msg
        self.status_code = status_code or self.status_code
