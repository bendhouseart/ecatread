import json
from os import path

# collect ecat header map
try:
    with open('ecat_headers.json', 'r') as infile:
        ecat_header_maps = json.load(infile)
except FileNotFoundError:
    raise Exception("Unable to load header definitions and map from ecat_headers.json. Aborting.")


def get_ecat_bytes(path_to_ecat):
    # check if file exists
    if path.isfile(path_to_ecat):
        with open(path_to_ecat, 'rb') as infile:
            ecat_bytes = infile.read()
    else:
        raise Exception(f"No such file found at {path_to_ecat}")

    return ecat_bytes


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


