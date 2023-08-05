#'http': 'socks4://194.226.164.214:1080',

import requests

def get_data(proxy_host, proxy_port, url_to_send):
    proxies = {
        'http': f'socks4://{proxy_host}:{proxy_port}',
        'https': f'socks4://{proxy_host}:{proxy_port}'
    }

    response = requests.get(url_to_send, proxies=proxies)
    return response.content

response = get_data('51.222.29.254', 47103, 'https://www.example.com')
print(response)
