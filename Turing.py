from subprocess import run, TimeoutExpired
from os         import remove
from re         import match

def mpcall(program, args, timeout):
    try:
        return run([*program, *args], timeout = timeout, capture_output = True)
    except TimeoutExpired:
        return None

def c_fifo_mpcall(program, args, timeout, file_name, data):
    with open(file_name, 'w') as file: file.write(data)

    result = mpcall(program, args, timeout)

    remove(file_name)

    return result

def parse_command(text):
    result = match("(?s)[Tt]uring\s*:\s*([^ \n]+)\n```(.*?)\n(.*?)\n```", text)

    if result:
        return result.groups()

    return None
