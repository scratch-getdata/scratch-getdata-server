#'http': 'socks4://194.226.164.214:1080',

import socks
import socket
import urllib.request

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket(socket.AF_INET)  # Force IPv4
    sock.settimeout(timeout)
    if source_address:
        sock.bind(source_address)
    sock.connect(address)
    return sock

def get_data(proxy_host, proxy_port, url_to_send):
    socks.setdefaultproxy(socks.SOCKS4, proxy_host, proxy_port)
    socket.socket = socks.socksocket
    socket.create_connection = create_connection  # Override default create_connection function
    response = urllib.request.urlopen(url_to_send)
    return response.read()

response = get_data('185.179.196.19', 1090, 'https://www.example.com')
print(response)