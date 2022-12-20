import requests
import ipaddress
from os import path
import logging
from os import environ

IP_API_URL = "https://api.ipify.org?format=json"
NAMECHEAP_DDNS_URL = "https://dynamicdns.park-your-domain.com/update"

DDNS_NAMECHEAP_PASSWORD = None
DDNS_DOMAIN = None
DDNS_HOST = None
LAST_IP_FILE = "/var/update/.lastip"
LOG_FILE = "/var/update/out.log"

logging.basicConfig(filename=LOG_FILE, encoding='utf-8', level=logging.DEBUG)


def is_valid_ip_address(ip_str):
    result = True
    try:
        ipaddress.ip_network(ip_str)
    except:
        result = False
    return result


def get_ip_from_file():
    if path.exists(LAST_IP_FILE):
        with open(LAST_IP_FILE, 'r') as ip_file:
            ip_str = ip_file.read()
            if is_valid_ip_address(ip_str):
                return ip_str
    return None


def write_ip_to_file(new_ip):
    with open(LAST_IP_FILE, 'w') as ip_file:
        ip_file.write(new_ip)


def get_ip():
    resp = requests.get(IP_API_URL)
    if resp.status_code < 300:
        new_ip = resp.json()['ip']
        logging.info("Got new ip: %s", new_ip)
        return new_ip
    logging.warning("Error getting ip. Status code: %u", resp.status_code)
    return None


def update_ip(sub_domain, domain, password, new_ip):
    payload = {'host': sub_domain, 'domain': domain,
               'password': password, 'ip': new_ip}
    resp = requests.get(NAMECHEAP_DDNS_URL, params=payload, verify=True)
    if resp.status_code < 300:
        logging.info("Successfully updated ip to %s on remote", new_ip)
        return True
    else:
        print(resp.content)
        print(resp.request.url)
        logging.warning(
            "Failed to update ip on remote. Status code: %u", resp.status_code)
        return False

def load_envvars():
    global DDNS_NAMECHEAP_PASSWORD
    global DDNS_DOMAIN
    global DDNS_HOST

    DDNS_NAMECHEAP_PASSWORD = environ.get("DDNS_NAMECHEAP_PASSWORD")
    DDNS_DOMAIN = environ.get("DDNS_DOMAIN")
    DDNS_HOST = environ.get("DDNS_HOST")

    if DDNS_NAMECHEAP_PASSWORD == None:
        logging.error("DDNS_NAMECHEAP_PASSWORD is not set. Please add it to your .env to continue")
    elif DDNS_DOMAIN == None:
        logging.error("DDNS_DOMAIN is not set. Please add it to your .env to continue")
    elif DDNS_HOST == None:
        logging.error("DDNS_HOST is not set. Please add it to your .env to continue")
    else:
        return True
    return False

def main():
    if not load_envvars():
        return
    last_ip = get_ip_from_file()
    new_ip = get_ip()
    if last_ip != None and last_ip == new_ip:
        logging.info("Current ip matches existing ip. Not updating.")
    else:
        success = update_ip(DDNS_HOST, DDNS_DOMAIN,
                            DDNS_NAMECHEAP_PASSWORD, new_ip)
        if success:
            write_ip_to_file(new_ip)


main()
