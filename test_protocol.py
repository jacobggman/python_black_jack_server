import unittest
from protocol import Message, Codes


class TestSum(unittest.TestCase):
    def test_message_formatting(self):
        m = Message(Codes.FILLED_TO_CONNECT_TO_GAME, "hi!")
        self.assertEqual(m.code, Codes.FILLED_TO_CONNECT_TO_GAME, "Should be the code failed to connect")
        self.assertEqual(m.data, "hi!", "Should be the data that entered")
        m_bytes = m.to_bytes()
        new_m = Message.format(m_bytes)

        self.assertEqual(m.code, new_m.code, "Should have the same code")
        self.assertEqual(m.data, new_m.data, "Should have the same data")

    def test_message_print_formatting(self):
        m = Message(Codes.FILLED_TO_CONNECT_TO_GAME, "hi!")
        self.assertEqual(repr(m), f"Message({Codes.FILLED_TO_CONNECT_TO_GAME}, 'hi!')", "Class print format")

    def test_failed_message_to_bytes(self):
        m = Message(Codes.OVER_MAX, "ho?")
        as_bytes = m.to_bytes()
        self.assertEqual(as_bytes, b'0', "Should be zero when have number that is to big")
        m = Message(Codes.PONG, "h" * 65536)
        as_bytes = m.to_bytes()
        self.assertEqual(as_bytes, b'0', "Should be zero when the msg is to big")

    def test_failed_message_format(self):
        m = Message.format(b'sf')
        self.assertEqual(m.code, Codes.LOCAL_FORMAT_ERROR, "Should return format error when data is too short")


if __name__ == '__main__':
    unittest.main()
