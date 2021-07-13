import json
import os.path
import struct
from os import path
from os.path import join
import pathlib
import re
import numpy


parent_dir = pathlib.Path(__file__).parent.resolve()


# collect ecat header map
try:
    with open(join(parent_dir, 'ecat_headers.json'), 'r') as infile:
        ecat_header_maps = json.load(infile)
except FileNotFoundError:
    raise Exception("Unable to load header definitions and map from ecat_headers.json. Aborting.")


def ecat_datatype_to_python(ecat_data_type):
    """
    Given a datatype gathered from an ecat description returns a python version of that datatype.
    :param ecat_data_type: a string such as Integer*2, Integer*4, Real*4, or Character*
    :return:
    """
    pass

def get_ecat_bytes(path_to_ecat: str):
    """
    Opens an ecat file and reads the entrie file into memory to return a bytes object
    not terribly memory efficient for large or parallel reading of ecat files.
    :param path_to_ecat: path to an ecat file, however will literally open any file an read it
    in as bytes. TODO Perhaps add some validation to this.
    :return: a bytes object
    """
    # check if file exists
    if path.isfile(path_to_ecat):
        with open(path_to_ecat, 'rb') as infile:
            ecat_bytes = infile.read()
    else:
        raise Exception(f"No such file found at {path_to_ecat}")

    return ecat_bytes


def read_bytes(path_to_bytes: str, byte_start: int, byte_stop: int, byte_type='utf-8'):
    if not os.path.isfile(path_to_bytes):
        raise Exception(f"{path_to_bytes} is not a valid file.")

    # open that file
    bytes_to_read = open(path_to_bytes, 'rb')

    # move to start byte
    bytes_to_read.seek(byte_start, 0)

    # read a section of bytes from bytestart to byte stop
    byte_width = byte_stop
    sought_bytes = bytes_to_read.read(byte_width)

    byte_types = {
        "Integer*2": 'blah'
    }

    # attempt to decode the bytes
    #decoded = sought_bytes.decode(byte_type)

    #print(sought_bytes)

    bytes_to_read.close()
    return sought_bytes


def collect_specific_bytes(bytes_object, start_position, width, relative_to=0):
    """
    Moves
    :param bytes_object: an opened bytes object
    :param start_position: the position to start to read at
    :param width: how far to read from the start position
    :param relative_to: position relative to 0 -> start of file/object, 1 -> current position of seek head,
    2 -> end of file/object
    :return: the bytes starting at position
    """
    # navigate to byte position
    content = bytes_object[start_position: start_position + width]
    return {"content": content, "new_position": start_position + width}


def get_buffer_size(data_type, variable_name):

    first_split = variable_name.split('(')
    if len(first_split) == 2:
        fill_scalar = int(first_split[1][:-1])
    
    else:
        fill_scalar = 1

    scalar = int(re.findall(r'\d+', data_type)[0]) * fill_scalar

    return scalar


if __name__ == "__main__":
    """
    Verifying that the byte positions and widths correspond to their datatype size as 
    stated in ecat_headers.json (this is mostly a sanity check).
    """

    check_header_json = False

    if check_header_json:
        for header, header_values in ecat_header_maps['ecat_headers'].items():

            print(header)
            byte_position = 0

            for each in header_values:
                print(each.get('byte'), each.get('variable_name'), each.get('type'), get_buffer_size(each.get('type'), each.get('variable_name')), byte_position)
                if byte_position != each.get('byte'):
                    print(f"Mismatch in {header} between byte position {each.get('byte')} and calculated position {byte_position}.")
                    try:
                        paren_error = re.findall(r'^.*?\([^\d]*(\d+)[^\d]*\).*$', each.get('variable_name'))
                    except TypeError:
                        pass
                byte_position = get_buffer_size(each['type'], each['variable_name']) + byte_position

    check_byte_reading = True
    if check_byte_reading:
        from dotenv import load_dotenv, find_dotenv

        # load a test ecat file (this really should live at a url somewhere)
        load_dotenv(find_dotenv())
        ecat_test_file = os.environ.get("TEST_ECAT_PATH")

        # use ecat header 72 to collect bytes from ecat file
        ecat_main_header = ecat_header_maps['ecat_headers']['ecat72_mainheader']
        for values in ecat_main_header:
            byte_position, data_type, variable_name = values['byte'], values['type'], values['variable_name']
            byte_width = get_buffer_size(data_type, variable_name)
            something = read_bytes(ecat_test_file, byte_position, byte_width)
            something_filtered = bytes(filter(None, something))
            if 'Character' in data_type:
                something_to_string = str(something_filtered, 'UTF-8')
            elif 'Integer' in data_type:
                something_to_string = int.from_bytes(something_filtered, 'big')
            elif 'Real' in data_type:
                number_of_fs = int(byte_width/4)
                something_to_real = struct.unpack('>' + number_of_fs*'f', something)
                if len(something_to_real) > 1:
                    something_to_string = list(something_to_real)
                else:
                    something_to_string = something_to_real[0]

            print(byte_position, data_type, variable_name, something, something_filtered, something_to_string)
            read_head_position = byte_position + byte_width

        print("let's read some stuff!")
        next_block = read_bytes(
            path_to_bytes=ecat_test_file,
            byte_start=read_head_position,
            byte_stop=read_head_position + 512)
        print("the above should be an array of some sort")

        read_that_byte_array = numpy.frombuffer(next_block, dtype=numpy.dtype('>i4'), count=-1)
        print("READ!")

