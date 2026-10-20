import urllib.request
import os

urls = [
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_01.jpg', 'display84a_01.jpg'),
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_03.jpg', 'display84a_03.jpg'),
    ('https://www.prugio.com/hb/2025/dongtan/assets/images/sub/display84a_05.jpg', 'display84a_05.jpg'),
]

out_dir = "references/modelhouse/original"
os.makedirs(out_dir, exist_ok=True)
for url, fn in urls:
    try:
        urllib.request.urlretrieve(url, os.path.join(out_dir, fn))
        print(f"Downloaded {fn}")
    except Exception as e:
        print(f"Error {fn}: {e}")
