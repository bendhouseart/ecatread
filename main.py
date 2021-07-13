import os
from dotenv import load_dotenv, find_dotenv
from thisbytes import get_ecat_bytes, collect_specific_bytes, ecat_header_maps

# load a test ecat file (this really should live at a url somewhere)
load_dotenv(find_dotenv())
ecat_test_file = os.environ.get("TEST_ECAT_PATH")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_bytes = get_ecat_bytes(ecat_test_file)

    header_bytes = collect_specific_bytes(file_bytes, 0, 512)
    print('collected')
