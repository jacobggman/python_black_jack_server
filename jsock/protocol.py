from jsock.code import Code


class Protocol:

    # get module with classes of Code
    def __init__(self, protocol_module):
        self.codes = dict()

        for field_name in dir(protocol_module):
            if field_name.startswith("__"):
                continue
            var = getattr(protocol_module, field_name)
            try:
                if issubclass(var, Code) and var is not Code:
                    print(var)
                    self.add_code_class(var)
            except TypeError:
                pass

    def add_code_class(self, class_type: Code):
        self.codes[class_type.get_code(None)] = class_type

    def get_class(self, code) -> Code:
        return self.codes.get(code)

    def get_docs(self):
        # TODO
        pass
