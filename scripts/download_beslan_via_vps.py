import os
import paramiko

SERVER_IP = "185.244.40.240"
SERVER_USER = "root"
REEL_URL = "https://www.instagram.com/reel/DcQU8MDAMpV/"

LOCAL_DEST = r"c:\Users\evgen\Desktop\Antigravity\NEWprodject\17_Бесроллинг\public\assets\beslan.mp4"
REMOTE_PATH = "/tmp/beslan_reel.mp4"

keys = [
    r"C:\Users\evgen\.ssh\id_rsa_germany",
    r"C:\Users\evgen\.ssh\id_ed25519"
]

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

connected = False
for k in keys:
    if os.path.exists(k):
        try:
            print(f"Trying key {k}...")
            ssh.connect(SERVER_IP, username=SERVER_USER, key_filename=k, timeout=15)
            connected = True
            print("Connected successfully with key:", k)
            break
        except Exception as e:
            print(f"Failed with key {k}: {e}")

if not connected:
    # Try ubuntu@158.160.114.94 (Yandex Cloud)
    print("Trying Yandex Transit server (158.160.114.94)...")
    for k in keys:
        try:
            ssh.connect("158.160.114.94", username="ubuntu", key_filename=k, timeout=15)
            connected = True
            print("Connected to Yandex Cloud with key:", k)
            break
        except Exception as e:
            print(f"Yandex failed with {k}: {e}")

if not connected:
    raise Exception("Could not connect to any VPS server via SSH.")

print("Installing / verifying yt-dlp on remote server...")
stdin, stdout, stderr = ssh.exec_command("pip install -U yt-dlp || pip3 install -U yt-dlp || apt-get install -y yt-dlp")
print("yt-dlp install output:", stdout.read().decode('utf-8')[:200])

print(f"Executing yt-dlp on remote server for {REEL_URL}...")
cmd = f"rm -f {REMOTE_PATH} && yt-dlp -o '{REMOTE_PATH}' '{REEL_URL}'"
stdin, stdout, stderr = ssh.exec_command(cmd)
print("STDOUT:", stdout.read().decode('utf-8'))
print("STDERR:", stderr.read().decode('utf-8'))

stdin, stdout, stderr = ssh.exec_command(f"ls -lh {REMOTE_PATH}")
ls_out = stdout.read().decode('utf-8')
print("Remote file:", ls_out)

if REMOTE_PATH in ls_out:
    print(f"Downloading to local: {LOCAL_DEST}...")
    os.makedirs(os.path.dirname(LOCAL_DEST), exist_ok=True)
    sftp = ssh.open_sftp()
    sftp.get(REMOTE_PATH, LOCAL_DEST)
    sftp.close()
    print("FINISHED! Local video file size:", os.path.getsize(LOCAL_DEST), "bytes")
else:
    print("Error: Remote file not found.")

ssh.close()
