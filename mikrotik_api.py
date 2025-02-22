from flask import Flask, jsonify
from flask_cors import CORS
import routeros_api
import logging
import socket

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# MikroTik API credentials
username = "username_api"
password = "password_api"
TIMEOUT = 3

# List of MikroTik devices with different ports
mikrotik_devices = {
    "Nama Device": {"host": "xxx.xx.xxx.xxx", "port": xxxx}, 
    "Nama Device": {"host": "xxx.xx.xxx.xxx", "port": xxxx},
    "Nama Device": {"host": "xxx.xx.xxx.xxx", "port": xxxx},
    "Nama Device": {"host": "xxx.xx.xxx.xxx", "port": xxxx},  
    "Nama Device": {"host": "xxx.xx.xxx.xxx", "port": xxxx},
}

def fetch_data(ip, port, device_name):
    """ Fetch PPPoE or Hotspot data based on the device with improved speed and logging """
    logging.info(f"Fetching data from {device_name} ({ip}:{port})...")

    try:
        # Check if the host is reachable before connecting
        logging.info(f"Checking connection to {ip}:{port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result != 0:
            raise TimeoutError(f"Connection timed out for {device_name} ({ip}:{port})")

        # Connect to MikroTik API
        logging.info(f"Connecting to {device_name} API...")
        api = routeros_api.RouterOsApiPool(
            host=ip, username=username, password=password, port=port, plaintext_login=True
        )
        connection = api.get_api()

        if device_name in ["Nama Device", "Nama Device", "Nama Device"]: # Isi nama devie yang ingin ambil data dari IP > Hotspot > Active
            logging.info(f"Fetching Hotspot data for {device_name}...")
            hotspot_active = connection.get_resource('/ip/hotspot/active')
            active_users = len(hotspot_active.get())
            total_users = "Active"
        else:
            logging.info(f"Fetching PPPoE data for {device_name}...") # Blok kode untuk ambil data dari PPP > Secrets dan PPP > Active Connections
            secrets = connection.get_resource('/ppp/secret')
            total_users = len(secrets.get(disabled="false"))

            active = connection.get_resource('/ppp/active')
            active_users = len(active.get())

        logging.info(f"Data fetched successfully for {device_name}: {active_users}/{total_users}")

        api.disconnect()
        return {"active": active_users, "total": total_users}

    except TimeoutError as e:
        logging.warning(f"Timeout error for {device_name}: {e}")
        return {"error": "Timeout"}
    except Exception as e:
        logging.error(f"Error fetching data for {device_name}: {e}")
        return {"error": str(e)}

@app.route('/api/pppoe', methods=['GET'])
def get_data():
    """ API Endpoint to return PPPoE or Hotspot data """
    results = {}
    for name, device in mikrotik_devices.items():
        results[name] = fetch_data(device["host"], device["port"], name)
    return jsonify(results)


@app.route("/api/proxy/pppoe")
def proxy_pppoe():
    response = requests.get("http://127.0.0.1:5000/api/pppoe")
    return jsonify(response.json())



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
