import builtins

_logfile = None
_echo = True

def echo_on():
    global _echo
    _echo = True

def echo_off():
    global _echo
    _echo = False

def open(filename,append=False):
    global _logfile
    if append:
        _logfile = builtins.open(filename, 'a')
    else:
        _logfile = builtins.open(filename, 'w')

def close():
    global _logfile
    if _logfile:
        _logfile.close()
        _logfile = None

def write(message):
    global _logfile
    if _logfile:
        try:
            _logfile.write(message)
        except:
            print("Could not write to Log file")
    if _echo:
        print(message)

def writeln(message):
    global _outfile
    if _logfile:
        try:
            _logfile.write(message + "\n")
        except Exception as x:
            print(str(x))
    if _echo:
        print(message)
