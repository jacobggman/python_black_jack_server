
class Config:
    def __init__(self, code_enum_type):
        self.code_enum_type = code_enum_type

    host = "127.0.0.1"
    port = 1337

    # TODO:
    # if not give required field or wrong type of filed return it on await or callback
    return_wrong_field_message = False

    # TODO:
    # if not None return this message when get fields in message that is wrong
    auto_return_for_wrong_field_message = None
    # TODO:
    # if not None return this message when get message that is wrong
    auto_return_for_wrong_format_message = None

    # TODO:
    return_error_to_callback = False
