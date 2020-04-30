class UnavailableChannelError(Exception):
    pass


class MissingContextError(Exception):
    def __init__(self, *args, **kwargs):
        self.message = ('Channel ID or context must be provided for '
                        'retrieving chat history')
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.message
