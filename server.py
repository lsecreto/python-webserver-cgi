from os import chdir
from sys import argv
from cgiserver import CGIServer

# Server configuration
NUM_OF_WORKERS = 4
ALLOW_CGI = True
DEFAULT_INTERFACE = '0.0.0.0'
DEFAULT_PORT = 8080

if __name__ == '__main__':
    interface = DEFAULT_INTERFACE
    port = DEFAULT_PORT
    if argv[1:]:
        address = argv[1]
        if ':' in address:
            interface = address.split(':')[0]
            port = int(address.split(':')[1])
        else:
            port = int(address)
    if argv[2:]:
        chdir(argv[2])

    with CGIServer(address=(interface, port), workers=NUM_OF_WORKERS, allow_cgi=ALLOW_CGI) as server:
        server.start()
