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


def read_bytes(path_to_bytes: str, byte_start: int, byte_stop: int = -1, byte_type='utf-8'):
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


def get_header_data(header_data_map: dict = {}, ecat_file: str = '', byte_offset: int = 0):
    """
    Collects the header data from an ecat file, by default starts at byte position 0 (aka byte offset)
    for any header that is not the main header this offset will need to be provided
    :param header_data_map: The dictionary mapping of header data
    :param ecat_file: the path to the ecat file that is being read
    :param byte_offset: position to start reading bytes at, the data in the header_data_map is relative
    to this value. E.g. the main header lies at byte 0 of the ecat_file while, the subheader for frame n
    lies at byte n*512
    :return: a dictionary w/ keys corresponding to the variable_name in each header field and their
    accompanying values and the last byte position read e.g. -> {'key': value, ....}, 512
    """
    for values in header_data_map:
        byte_position, data_type, variable_name = values['byte'], values['type'], values['variable_name']
        byte_width = get_buffer_size(data_type, variable_name)
        relative_byte_position = byte_position + byte_offset
        something = read_bytes(ecat_test_file, relative_byte_position, byte_width)
        something_filtered = bytes(filter(None, something))
        if 'Character' in data_type:
            something_to_string = str(something_filtered, 'UTF-8')
        elif 'Integer' in data_type:
            something_to_string = int.from_bytes(something_filtered, 'big')
        elif 'Real' in data_type:
            number_of_fs = int(byte_width / 4)
            something_to_real = struct.unpack('>' + number_of_fs * 'f', something)
            if len(something_to_real) > 1:
                something_to_string = list(something_to_real)
            else:
                something_to_string = something_to_real[0]

        print(byte_position, data_type, variable_name, something, something_filtered, something_to_string)
        main_header[variable_name] = something_to_string
        read_head_position = relative_byte_position + byte_width

    return main_header, read_head_position


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
        main_header = {}
        # use ecat header 72 to collect bytes from ecat file
        ecat_main_header = ecat_header_maps['ecat_headers']['ecat72_mainheader']
        main_header_from_func, read_to = get_header_data(ecat_main_header, ecat_test_file)
        # end collect main header

        # Collecting File Directory/Index
        next_block = read_bytes(
            path_to_bytes=ecat_test_file,
            byte_start=read_to,
            byte_stop=read_to + 512)

        read_that_byte_array = numpy.frombuffer(next_block, dtype=numpy.dtype('>i4'), count=-1)
        # reshape 1d array into 2d
        reshaped = numpy.transpose(numpy.reshape(read_that_byte_array, (-1, 4)))
        # chop of rows after 32
        directory = reshaped[:, 0:32]
        # get rid of zero columns
        columns_to_remove = []
        for index, column in enumerate(directory.T):
            if sum(column) == 0:
                columns_to_remove.append(index)
        directory = numpy.delete(directory, columns_to_remove, axis=1)

        # sort the directory contents as they're sometimes out of order
        sorted_directory = directory[:, directory[0].argsort()]

        """
        Some notes about the file directory/sorted directory:
        
        The first or 0th column of the file directory correspond to the nature of the directory itself:
        row 0: ??? No idea, some integer
        row 1: Byte position of this table/directory
        row 2: not sure in testing it seems to be 0 most times..
        row 3: The number of frames/additional columns in the file. If the number of columns of this array
        is n, it would contain n-1 frames. 
        
        The values in sorted_directory correspond to the following for all columns except the first column
        row 0: Not sure, but we sort on this, perhaps it's the frame start time
        row 1: the start byte block position of the fram data
        row 2: end byte block position of the frame data
        row 3: ??? Number of frames contained in w/ in the byte blocks between row 1 and 2?
        """


        print("index found")

        # determine subheader type by checking main header
        subheader_type_number = main_header['FILE_TYPE']

        """
        Subheader types correspond to these enumerated types as defined below:
        00 = unknown, 
        01 = Sinogram, 
        02 = Image - 16, 
        03 = Attenuation Correction, 
        04 = Normalization, 
        05 = PolarMap, 
        06 = Volume 8, 
        07 = Volume 16, 
        08 = Projection 8, 
        09 = Projection 16, 
        10 = Image 8, 
        11 = 3D Sinogram 16, 
        12 = 3D Sinogram 8, 
        13 = 3D Normalization, 
        14 = 3D Sinogram Fit)
        
        Presently, only types 03, 05, 07, 11, and 13 correspond to known subheader types. If the
        value in FILE_TYPE is outside of this range the subheaders will not be read and this will
        raise an exception.
        """

        # here we map the file types to the subheader byte tables/jsons defined in ecat_header_maps
        subheader_types = {
            0: None,
            1: None,
            2: None,
            3: ecat_header_maps['ecat_headers']['ecat72_subheader_matrix_attenuation_files'],
            4: None,
            5: ecat_header_maps['ecat_headers']['ecat72_subheader_matrix_polar_map_files'],
            6: None,
            7: ecat_header_maps['ecat_headers']['ecat72_subheader_matrix_image_files'],
            8: None,
            9: None,
            10: None,
            11: ecat_header_maps['ecat_headers']['ecat72_subheader_3d_matrix_scan_files'],
            12: None,
            13: ecat_header_maps['ecat_headers']['ecat72_subheader_3d_normalized_files']
        }

        # collect the bytes map file for the designated subheader, note some are not supported.
        subheader_map = subheader_types.get(subheader_type_number)

        if not subheader_map:
            raise Exception("Unsupported data type for ")

        # TODO Collect Subheaders and Pixel Data
        # collect subheaders
        subheaders = []
        for i in range(len(sorted_directory) - 1):
            frame_number = i + 1
            print(f"Reading subheader from frame {i}")

            # collect frame info/column
            frame_info = sorted_directory[:, i + 1]
            frame_start = frame_info[1]
            frame_stop = frame_info[2]

            frame_byte_position = 512*(frame_start - 1)  # sure why not

            # read subheader
            subheader, byte_position = get_header_data(subheader_map, ecat_test_file, byte_offset=frame_byte_position)
            subheaders.append(subheader)