# ddns-updater
This tool is to be used as a cronjob to publish a new IP to NameCheap's DDNS service.   

ddns-updater will fetch your public IP using ipify's api service. It will then determine if the IP has change since last posting. If it has, it will reach out to the configured DDNS server with the new information.

## How to run 
1. Create a `.env` file containing the following values:
```
DDNS_NAMECHEAP_PASSWORD={namecheap ddns password here}
DDNS_DOMAIN={your domain name, e.g. example.com}
DDNS_HOST={your host name, e.g. www}
MONITOR_URL={optional http endpoint for heartbeat}
```
2. Run `python update.py`
