from sys import stderr, version_info
from multiprocessing import Process, current_process

# Decide imports based on Python version
if version_info[0] < 3:
    from SocketServer import ThreadingMixIn
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from CGIHTTPServer import CGIHTTPRequestHandler
else:
    from socketserver import ThreadingMixIn
    from http.server import HTTPServer, BaseHTTPRequestHandler, CGIHTTPRequestHandler


class CGIServer(object):
    @staticmethod
    def log(log_format, *args):
        stderr.write('[%s]\t%s\n' % (current_process().name, log_format % args))

    def __init__(self, address=('0.0.0.0', 8080), workers=1, allow_cgi=True):
        self.server = CGIHTTPServer(address, CGIServerRequestHandler if allow_cgi else BaseHTTPRequestHandler)
        self.workers = [Process(target=self.server.serve_forever, name='Worker-%i' % item) for item in range(workers)]
        if len(self.workers):
            CGIServer.log('HTTP Server listening at %s:%i' % address)

    def __exit__(self, *args, **kwargs):
        try:
            for worker in self.workers:
                worker.join()
        except KeyboardInterrupt:
            pass
        finally:
            self.server.server_close()

    def __enter__(self):
        return self

    def start(self):
        for worker in self.workers:
            worker.start()

    def add_worker(self):
        worker = Process(target=self.server.serve_forever, name='Worker-%i' % len(self.workers))
        self.workers.append(worker)
        worker.start()


class CGIHTTPServer(ThreadingMixIn, HTTPServer):
    def serve_forever(self, *args, **kwargs):
        CGIServer.log('Starting HTTP Worker with pid %s' % current_process().pid)
        try:
            HTTPServer.serve_forever(self, *args, **kwargs)
        except KeyboardInterrupt:
            CGIServer.log('Terminating HTTP Worker with pid %s' % current_process().pid)
            HTTPServer.server_close(self)


class CGIServerRequestHandler(CGIHTTPRequestHandler):
    def log_message(self, log_format, *args):
        CGIServer.log('[%s]\t%s\n' % (current_process().name, log_format % args))
