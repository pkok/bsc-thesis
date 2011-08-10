import sys

import collections
import json
import random
import socket
import SocketServer
import threading


class Client(object):
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        self.token = None
        self.proxies = {}
        self.token = self.request(object_id=0, method="get_token")

    def disconnect(self):
        return self.request(object_id=0, method='disconnect')

    def request(self, object_id, method, args=[], kwargs={}):
        message = {"object_id": object_id,\
                "method": method,\
                "args": args,\
                "kwargs": kwargs,\
                "token": self.token,\
                }
        print "***", message
        sock = socket.create_connection((self.host, self.port))
        sock.send(json.dumps(message) + '\n')
        reply = json.loads(sock.recv(4096))
        sock.close()
        if reply['error']:
            raise eval(reply['error'])(reply['result'])
        return unicode2str(reply['result'])


    def ALProxy(self, proxy, r_host="nao.local", r_port=9559):
        proxy_id = self.request(object_id=0, method="ALProxy",
            args=[proxy, r_host, r_port])
        proxy = Remote_ALProxy(proxy_id, self)
        self.proxies[proxy_id] = proxy
        return proxy

    def __getitem__(self, proxy_id):
        return self.proxies[proxy_id]



class Remote_ALProxy(object):
    def __init__(self, proxy_id, client):
        self.proxy_id = proxy_id
        self.client = client

    def __getattr__(self, value):
        def callme(*args, **kwargs):
            return self.client.request(object_id=self.proxy_id,\
                    method=value,\
                    args=args,\
                    kwargs=kwargs)
        return callme




# This part of the system is made to run on 32-bit systems (those are
# apparently the only ones that can import naoqi).
if sys.maxsize < 2**32:
    import naoqi

    class NaoqiRequestHandler(SocketServer.StreamRequestHandler):
        #def __init__(self, *args, **kwargs):
        given_tokens = [0]
        random = random.Random(0)
        proxy = {} # a dict of ((client_id, proxy_id), proxy) pairs
        proxy_counter = collections.defaultdict(lambda: [])

        def get_token(self):
            token = self.random.getrandbits(32)
            while token in self.given_tokens:
                token = self.random.getrandbits(32)
            self.given_tokens.append(token)
            return token

        def handle(self):
            lines = self.rfile.readline()
            request = unicode2str(json.loads(lines, encoding='ASCII'))
            try:
                if not request.has_key('token') or request['token'] is None:
                    raise UnboundLocalError("Request a token first!")
                elif request['object_id'] == 0:
                    if request['method'] == 'get_token':
                        token = self.get_token()
                        self.reply(self.get_token())
                    elif request['method'] == 'ALProxy':
                        token = request['token']
                        proxy_id = self.get_token()
                        self.proxy_counter[token].append(proxy_id)
                        self.proxy[token, proxy_id] = ALProxyWrapper(*request['args'])
                        self.reply(proxy_id)
                    elif request['method'] == 'disconnect':
                        token = request['token']
                        if token in self.given_tokens:
                            for proxy_id in self.proxy_counter[token]:
                                self.proxy[token, proxy_id].exit()
                                del self.proxy[token, proxy_id]
                            self.reply(True)
                        else:
                            raise ValueError("Not a registered token.")
                    else:
                        raise AttributeError("No such attribute: %s" \
                                % request['method'])
                else:
                    proxy = self.proxy[request['token'], request['object_id']]
                    method = getattr(proxy, request['method'])
                    self.reply(method(*request['args'], **request['kwargs']))
            except Exception, e:
                self.reply(e)

        def reply(self, value):
            if isinstance(value, Exception):
                self.wfile.write(json.dumps({'result': str(value), 'error':
                    value.__class__.__name__}) + '\n')
            else:
                self.wfile.write(json.dumps({'result': value, 'error': None}) + '\n')


    class ALProxyWrapper(object):
        def __init__(self, proxy, r_host="localhost", r_port=9559):
            self.proxy_type = proxy
            self.host = r_host
            self.port = r_port
            self.proxy = naoqi.ALProxy(proxy, self.host, self.port)

        def __getattr__(self, value):
            def callme(*args, **kwargs):
                return getattr(self.proxy, value)(*args, **kwargs)
            return callme


    def Server(host_and_port):
        server = SocketServer.ThreadingTCPServer(host_and_port, NaoqiRequestHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.setDaemon(True)
        return server_thread


def unicode2str(u_obj):
    if isinstance(u_obj, basestring):
        return str(u_obj)
    elif isinstance(u_obj, dict):
        s_obj = type(u_obj)()
        for u_key, u_value in u_obj.iteritems():
            s_obj[unicode2str(u_key)] = unicode2str(u_value)
        return s_obj
    elif isinstance(u_obj, (list, tuple)):
        return type(u_obj)(map(unicode2str, u_obj))
    else: # not a collection or unicode string
        return u_obj
