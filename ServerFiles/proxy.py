#'http': 'socks4://194.226.164.214:1080',

import requests

def send(url):
  try:
    proxies = {
    'http': 'socks4://184.170.248.5:4145',
    'https': 'socks4://184.170.248.5:4145'
    }
    response = requests.get(url, proxies=proxies, verify=False)
    return response.content
  except:
    try:
      proxies = {
          'http': 'socks4://194.226.164.214:1080',
          'https': 'socks4://184.170.248.5:4145'
      }
      response = requests.get(url, proxies=proxies, verify=False)
      return response.content
    except:
      try:
        proxies = {
          'http': 'socks4://18.133.117.147:3128',
          'https': 'socks4://18.133.117.147:3128'
      }
        response = requests.get(url, proxies=proxies, verify=False)
        return response.content
      except:
        raise ConnectionError
