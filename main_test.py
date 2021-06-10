import unittest

from main import does_string_start_with_two_dashes, get_element_after_value, get_optional_value_from_input, \
    get_mandatory_value_from_input


class TestHelperMethods(unittest.TestCase):

    def test_does_string_start_with_two_dashes(self):
        # Two dashes
        self.assertTrue(does_string_start_with_two_dashes("--"))
        # Three Dashes
        self.assertTrue(does_string_start_with_two_dashes("---"))
        # Two dashes, then text
        self.assertTrue(does_string_start_with_two_dashes("--hello"))
        # Empty String
        self.assertFalse(does_string_start_with_two_dashes(""))
        # One Dash
        self.assertFalse(does_string_start_with_two_dashes("-"))
        # One Dash, then text
        self.assertFalse(does_string_start_with_two_dashes("-hello"))
        # Text without a dash
        self.assertFalse(does_string_start_with_two_dashes("hello"))
        # Text ending in two dashes
        self.assertFalse(does_string_start_with_two_dashes("hello--"))

    def test_get_element_after_value(self):
        test_list = "--one valueForOne --two two --three three --four --five five".split()
        # Get first value in list
        self.assertEqual(get_element_after_value(test_list, "--one", ""), "valueForOne")
        # Get value from the middle of the list
        self.assertEqual(get_element_after_value(test_list, "--two", ""), "two")
        # Throw error when label isn't in list
        with self.assertRaises(ValueError):
            get_element_after_value(test_list, "--six", "")
        # Throw error when label doesn't have a corresponding value
        with self.assertRaises(ValueError):
            get_element_after_value(test_list, "--four", "")

    def test_get_optional_value_from_input(self):
        test_list = "--one valueForOne --two two --three three --four --five five".split()
        # Get value from the list
        self.assertEqual(get_optional_value_from_input(test_list, "--two"), "two")
        # Return empty string when label isn't in list
        self.assertEqual(get_optional_value_from_input(test_list, "--six"), "")
        # Throw error when label doesn't have a corresponding value
        with self.assertRaises(ValueError):
            get_optional_value_from_input(test_list, "--four")

    def test_get_mandatory_value_from_input(self):
        test_list = "--one valueForOne --two two --three three --four --five five".split()
        # Get value from the list
        self.assertEqual(get_mandatory_value_from_input(test_list, "--two", ""), "two")
        # Throw error when label isn't in list
        with self.assertRaises(ValueError):
            get_mandatory_value_from_input(test_list, "--six", "")
        # Throw error when label doesn't have a corresponding value
        with self.assertRaises(ValueError):
            get_mandatory_value_from_input(test_list, "--four", "")


if __name__ == '__main__':
    unittest.main()
