import builtins

_outfile = None
_echo = 'off'

def enum(**enums):
    return type('Enum', (), enums)

Details = enum(BoxName=1,BoxDetails=2)

_detail = Details.BoxName

def set_detail(detail):
    _detail = detail

def echo_on():
    global _echo
    _echo = 'on'

def echo_off():
    global _echo
    _echo = 'off'

def open(filename):
    global _outfile
    _outfile = builtins.open(filename, 'w')


def close():
    global _outfile
    if _outfile:
        _outfile.close()


def writeln(value,detail = Details.BoxName):
    global _outfile
    if type(value) is str:
        outval = value
    elif hasattr(value,'output'):
        outval = value.output()

    if detail <= _detail:
        if _echo.lower() == 'on':
            print(outval)

        if hasattr(_outfile, 'write'):
            _outfile.write(outval + "\n")


def write(value, detail=Details.BoxName):
    global _outfile
    if type(value) is str:
        outval = value
    elif hasattr(value,'output'):
        outval = value.output()

    if detail <= _detail:
        if _echo.lower() == 'off':
            print(outval, end=' ')

        if hasattr(_outfile, 'write'):
            _outfile.write(outval)
