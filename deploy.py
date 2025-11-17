import time
import requests
from dotenv import dotenv_values

config = dotenv_values('.env')

PUBLIC_SSH_KEY_PATH = config["SSH_KEY_PATH"]
DO_API_TOKEN = config["DO_API_TOKEN"]
HEADERS = {"Authorization": f"Bearer {DO_API_TOKEN}"}

REGION = config["REGION"]
SIZE = config["SIZE"]
IMAGE = config["IMAGE"]

DROPLET_COUNT = int(config["DROPLET_COUNT"])
DROPLET_PREFIX = config["DROPLET_PREFIX"]
INVENTORY_FILE = config["INVENTORY_FILE"]


# ---------------------------
# Upload your SSH public key
# ---------------------------
def upload_ssh_key(name, public_key_path):
    with open(public_key_path, "r") as f:
        public_key = f.read().strip()

    payload = {"name": name, "public_key": public_key}

    response = requests.post(
        "https://api.digitalocean.com/v2/account/keys",
        headers=HEADERS,
        json=payload
    )

    if response.status_code == 201:
        print("SSH key uploaded.")
        return response.json()["ssh_key"]["id"]

    # Fallback: check existing keys
    keys = requests.get("https://api.digitalocean.com/v2/account/keys", headers=HEADERS).json()
    for key in keys["ssh_keys"]:
        if key["public_key"] == public_key:
            print("Existing SSH key found.")
            return key["id"]

    raise Exception("SSH key not found or upload failed.")


# ---------------------------
# Create Droplet
# ---------------------------
def create_droplet(name, region, size, image, ssh_key_id):
    payload = {
        "name": name,
        "region": region,
        "size": size,
        "image": image,
        "ssh_keys": [ssh_key_id],
        "backups": False,
        "ipv6": False,
        "tags": ["auto-created"]
    }

    response = requests.post(
        "https://api.digitalocean.com/v2/droplets",
        headers=HEADERS,
        json=payload
    )

    if response.status_code != 202:
        print("Response:", response.text)
        raise Exception("Droplet creation failed")

    droplet_id = response.json()["droplet"]["id"]
    print(f"{name} created with ID: {droplet_id}")
    return droplet_id


# ---------------------------
# Get Droplet IP
# ---------------------------
def wait_for_ip(droplet_id):
    print(f"Waiting for droplet {droplet_id} IP...")
    while True:
        response = requests.get(
            f"https://api.digitalocean.com/v2/droplets/{droplet_id}",
            headers=HEADERS
        ).json()

        networks = response["droplet"]["networks"]["v4"]
        for net in networks:
            if net["type"] == "public":
                return net["ip_address"]

        time.sleep(5)


# ---------------------------
# Write inventory.ini
# ---------------------------
def write_inventory(droplets):
    """
    droplets = [{"name": "Frankfort", "ip": "123.45.67.89"}, ...]
    """
    with open(INVENTORY_FILE, "w") as f:
        f.write("[webservers]\n")
        for d in droplets:
            f.write(
                f"{d['name']} ansible_host={d['ip']} ansible_user=root "
                f"ansible_python_interpreter=/usr/bin/python3\n"
            )

    print(f"\nInventory written to {INVENTORY_FILE}")


# ---------------------------
# MAIN SCRIPT
# ---------------------------
if __name__ == "__main__":
    ssh_key_id = upload_ssh_key("my_key", PUBLIC_SSH_KEY_PATH)

    droplets = []

    for i in range(1, DROPLET_COUNT + 1):
        droplet_name = f"{DROPLET_PREFIX}-{i}"
        droplet_id = create_droplet(
            name=droplet_name,
            region=REGION,
            size=SIZE,
            image=IMAGE,
            ssh_key_id=ssh_key_id
        )
        ip = wait_for_ip(droplet_id)

        print(f"Droplet {droplet_name} is ready! IP: {ip}\n")
        droplets.append({"name": droplet_name, "ip": ip})

    write_inventory(droplets)

    print("\nAll droplets created successfully!")
