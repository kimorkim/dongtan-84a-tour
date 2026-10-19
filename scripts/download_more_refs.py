import urllib.request

urls = [
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_06.jpg', 'display84a_06.jpg'),
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_07.jpg', 'display84a_07.jpg'),
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_08.jpg', 'display84a_08.jpg'),
]

for url, fn in urls:
    try:
        urllib.request.urlretrieve(url, fn)
        print(f"Downloaded {fn}")
    except Exception as e:
        print(f"Error {fn}: {e}")
