import urllib.request

urls = [
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_01.jpg', 'display84a_01.jpg'),
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_03.jpg', 'display84a_03.jpg'),
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_05.jpg', 'display84a_05.jpg'),
]

for url, fn in urls:
    try:
        urllib.request.urlretrieve(url, fn)
        print(f"Downloaded {fn}")
    except Exception as e:
        print(f"Error {fn}: {e}")
