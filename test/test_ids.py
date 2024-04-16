import unittest
from heare.ids import register_generation, _b62_encode, _b62_decode, new, is_valid, parse, swap_prefix, \
    _VALID_GENERATIONS


class TestIDs(unittest.TestCase):

    def test_register_generation(self):
        # Test that ValueError raised when length > 1
        with self.assertRaises(ValueError):
            register_generation("12")

        # Test that generation is added to _VALID_GENERATIONS
        register_generation("4")
        self.assertIn("4", _VALID_GENERATIONS)

    def test_b62_encode_decode(self):
        # Test that encoding and then decoding returns the original number
        number = 123456789
        encoded = _b62_encode(number)
        decoded = _b62_decode(encoded)
        self.assertEqual(decoded, number)

    def test_new(self):
        # Test that ValueError raised when generation isn't valid
        with self.assertRaises(ValueError):
            new('prefix', '12', None, 10)

        # Test that token is generated correctly
        token = new('prefix', '0')
        self.assertTrue(is_valid(token))

    def test_is_valid(self):
        # Test valid and invalid cases
        self.assertTrue(is_valid("prefix_0123456789"))
        self.assertFalse(is_valid("prefix_!@#"))

    def test_parse(self):
        # Test that invalid tokens return None
        self.assertIsNone(parse("invalid_token-"))

        # Test that valid tokens return a ParsedToken
        token = new("prefix", '0')
        parsed = parse(token)
        self.assertEqual(parsed.prefix, "prefix")
        self.assertEqual(parsed.generation, '0')

    def test_swap_prefix(self):
        # Test that prefix is changed correctly
        token = "oldprefix_0123456789"
        new_token = swap_prefix(token, "newprefix")
        self.assertEqual(new_token, "newprefix_0123456789")


if __name__ == '__main__':
    unittest.main()
