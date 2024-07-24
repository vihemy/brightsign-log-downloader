# Brightsign LogDownloader using Local Diagnostic Web Server API

This is a simple Python script that downloads player logs* (located sd/logs on the player) from a Brightsign player using the Local Diagnostic Web Server API. The script will download the logs from the player and save them to a file on the local machine.

*Note: This script download player logs from the sd/logs folder on the player, not the diagnostic log.

## Requirements
**Brightsign Configuration**
- Local Diagnostic Web Server API enabled on the player
- Authentication disabled on the player

**Libraries**:
- requests
- yaml

## Usage

1. Download the contents of the repository to your local machine.
2. Open the `config.yaml` file and update parent_log_folder and player names and ip's the IP address of the Brightsign player.
3. Run the script using the following command:

'''
python log_downloader.py --config config.yaml
'''