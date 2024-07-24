# Brightsign LogDownloader using Local Diagnostic Web Server API

This is a simple Python script that downloads the logs from a Brightsign player using the Local Diagnostic Web Server API. The script will download the logs from the player and save them to a file on the local machine.

Only works without authentication enabled on the player.

## Requirements
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