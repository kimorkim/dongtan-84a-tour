import socket
import json
import sys

def send_blender_command(cmd_type, params=None, port=9876, host="localhost", timeout=30.0):
    payload = {"type": cmd_type}
    if params:
        payload["params"] = params
    
    data_str = json.dumps(payload)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect((host, port))
        s.sendall(data_str.encode('utf-8'))
        
        buffer = b''
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            buffer += chunk
            try:
                res = json.loads(buffer.decode('utf-8'))
                return res
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
        return json.loads(buffer.decode('utf-8'))

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    res = send_blender_command("get_scene_info")
    print(json.dumps(res, indent=2, ensure_ascii=False))
