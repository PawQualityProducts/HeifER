import builtins

outfile = None
echo = 'off'

def echo_on():
    global echo
    echo = 'on'

def echo_off():
    global echo
    echo = 'off'

def open(filename):
    global outfile
    outfile = builtins.open(filename, 'w')


def close():
    global outfile
    if outfile:
        outfile.close()


def writeln(value):
    global outfile
    if echo.lower() == 'on':
        print(value)

    if hasattr(outfile, 'write'):
        outfile.write(value + "\n")


def write(value):
    global outfile
    if echo.lower() == 'off':
        print(value, end=' ')

    if hasattr(outfile, 'write'):
        outfile.write(value)
