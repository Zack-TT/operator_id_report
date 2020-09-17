import datetime
import io

g_verbose = False
g_outfile = None


def __get_timestamp():
    return str(datetime.datetime.now())


def set_outfile(f):
    if f is not None:
        global g_outfile
        g_outfile = io.open(f, 'w', encoding='utf-8')


def shutdown():
    global g_outfile
    if g_outfile:
        g_outfile.close()


def set_verbose(value):
    global g_verbose
    g_verbose = value
    if g_verbose:
        log_verbose('Verbose logging enabled')


def log(message):
    print(message)
    global g_outfile
    if g_outfile:
        g_outfile.write(u'[{0}] {1}\n'.format(__get_timestamp(), message))


def log_verbose(message):
    global g_verbose
    if g_verbose:
        log(message)
