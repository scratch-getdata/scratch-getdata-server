import requests
import json
from flask import Flask, jsonify
from flask_caching import Cache

app = Flask(__name__)

# Configure caching settings with a simple in-memory dictionary
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 2 * 24 * 3600  # 2 days in seconds
cache = Cache(app)

# Your existing get_scratch_data function with caching
# Your existing get_scratch_data function with caching
def get_scratch_data(url):
    cached_data = cache.get(url)
    if cached_data:
        print('data from cache')
        return cached_data

    proxy_urls = [
        'https://jungle-strengthened-aardvark.glitch.me/get/',
        'https://vnmppd-5000.csb.app/scratch_proxy/',
        'https://thingproxy.freeboard.io/fetch/'
    ]
    
    for proxy_url in proxy_urls:
        proxied_url = proxy_url + url
        try:
            response = requests.get(proxied_url)
            response.raise_for_status()
            data = response.text
            if data.strip():  # Check if the data is not empty
                cache.set(url, data)
                return data
            else:
                print(f"Empty response from proxy: {proxy_url}")
        except requests.exceptions.HTTPError as err:
            if response.status_code == 429:
                print("Too Many Requests")
            else:
                print(f"Error with proxy: {proxy_url}. Retrying with next proxy.")
                continue  # Skip to the next proxy
    
    # If all proxies fail, try using SOCKS4 proxy
    try:
        response = ServerFiles.proxy.send(url)  # Replace with your actual code for SOCKS4 proxy
        response.raise_for_status()
        data = response.text
        if data.strip():  # Check if the data is not empty
            cache.set(url, data)
            return data
        else:
            print("Empty response from SOCKS4 proxy")
    except requests.exceptions.HTTPError as err:
        print("All proxies failed, including SOCKS4 proxy")
        # Handle the error as needed
    
    return "All proxy options failed"


print(jsonify(get_scratch_data('https://google.com')))

if __name__ == '__main__':
    app.run()