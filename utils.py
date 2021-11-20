def is_even(x):
    try:
        x = int(x)
    except ValueError:
        x = ord(x) + 1
    return x % 2 == 0

def is_odd(x):
    try:
        x = int(x)
    except ValueError:
        x = ord(x) + 1
    return not (x % 2 == 0)

def create_hex(first_digit, second_digit, first_shift=0, second_shift=0):
    first_digit = int(first_digit, 16) + first_shift
    second_digit = int(second_digit, 16) + second_shift
    return '0x' + hex(first_digit)[-1] + hex(second_digit)[-1]
