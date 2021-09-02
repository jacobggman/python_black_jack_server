import json
from enum import Enum
from arg_type import ArgType


class Code:
    def to_json(self):
        fields = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self, a))]
        dictionary = dict()
        for field in fields:
            dictionary[field] = getattr(self, field)
        return json.dumps(dictionary)

    def get_code(self) -> Enum:
        pass

    def get_description(self) -> str:
        return ""

    # may be client server or both
    def who_send(self) -> str:
        return ""

    def possible_responses(self):
        return []

    @classmethod
    def from_json(cls, j: str):
        return_class = cls()
        json_dictionary = json.loads(j)
        args = return_class.get_args()
        for name, type in args:
            if name in json_dictionary:
                value = json_dictionary[name]
                if type(value) != type:
                    return "type error"
                setattr(return_class, name, value)
            else:
                if not type.optional:
                    return "non optional error"
            json_dictionary[name] = type
        return return_class

    def get_args(self):
        all_fields = map(lambda name: (name, getattr(self, name)), dir(self))
        return filter(lambda name_type: isinstance(name_type[1], ArgType), all_fields)

    def get_docs(self):
        code = self.get_code()
        args = list(self.get_args())
        return_str = code.name + "\n"
        return_str += self.get_description() + "\n"
        return_str += f"Code number: {code.value}\n"
        return_str += f"Who send: {self.who_send()}\n"
        return_str += "\nArguments:\n" if len(args) != 0 else ""
        for name, var in args:
            return_str += f'name: {name}\n'
            return_str += f'{var.docs}\n'
            return_str += f'type: "{var.type.__name__}"\n'
            return_str += f'is optional: {var.optional}\n\n'
        return return_str
