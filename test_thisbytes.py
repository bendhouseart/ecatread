import unittest
import os
from dotenv import load_dotenv, find_dotenv
from thisbytes import get_ecat_bytes, collect_specific_bytes

# load a test ecat file (this really should live at a url somewhere)
load_dotenv(find_dotenv())
ecat_test_file = os.environ.get("TEST_ECAT_PATH")


class MyTestCase(unittest.TestCase):
    def test_get_ecat_bytes(self):
        ecat_bytes = get_ecat_bytes(ecat_test_file)
        self.assertEqual(type(ecat_bytes), bytes)

    def test_locate_main_header(self):
        ecat_bytes = get_ecat_bytes(ecat_test_file)
        header_bytes = collect_specific_bytes(ecat_bytes, 0, 512)
        return header_bytes


if __name__ == '__main__':
    unittest.main()
    test_var = MyTestCase().test_locate_main_header()
