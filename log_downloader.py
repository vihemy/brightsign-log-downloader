import os
import argparse
import concurrent.futures
import threading
import time
import logging
import requests
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

directory_lock = threading.Lock()


class Player:
    def __init__(self, name: str, ip: str):
        self.name = name
        self.ip = ip


class DownloadReport:
    def __init__(self):
        self.success = True
        self.downloaded_logs = 0
        self.attempts = 1
        self.errors = []
        self.failed_logs = 0


def create_directory(path):
    """Create a directory if it does not exist, with thread safety."""
    with directory_lock:
        os.makedirs(path, exist_ok=True)


def load_yaml_config(config_path):
    """Load YAML configuration file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def check_player_connection(player):
    """Check if the player is reachable."""
    url = f"http://{player.ip}/api/v1/files/sd/logs/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return True, None
    except requests.RequestException as e:
        return False, e


def download_log(player, log_name, log_parent_folder, attempts=3):
    """Download a log file from a player with retries."""
    file_path = os.path.join(log_parent_folder, player.name, log_name)
    if os.path.isfile(file_path):
        return True, 1, None

    create_directory(os.path.dirname(file_path))
    url = f"http://{player.ip}/api/v1/files/sd/logs/{log_name}?contents&stream"
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, allow_redirects=True, timeout=10)
            response.raise_for_status()
            with open(file_path, "wb") as f:
                f.write(response.content)
            return True, attempt, None
        except requests.RequestException as e:
            if attempt == attempts:
                return False, attempts, e
    return False, attempts, None


def download_logs(player, log_parent_folder):
    """Download all logs from a player."""
    report = DownloadReport()
    success, e = check_player_connection(player)
    if not success:
        report.success = False
        report.errors.append(e)
        return report

    url = f"http://{player.ip}/api/v1/files/sd/logs/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        log_names = [log["name"] for log in response.json()["data"]["result"]["files"]]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(
                    download_log, player, log_name, log_parent_folder
                ): log_name
                for log_name in log_names
            }
            for future in concurrent.futures.as_completed(futures):
                success, attempts, e = future.result()
                if success:
                    report.downloaded_logs += 1
                else:
                    report.success = False
                    report.errors.append(e)
                    report.failed_logs += 1
                report.attempts = max(report.attempts, attempts)

        report.errors = [err for err in report.errors if err is not None]

        return report
    except requests.RequestException as e:
        report.success = False
        report.errors.append(e)
        return report


def log_report(player_name, report):
    """Log the download report for a player."""
    if report.success:
        logging.info(
            f"{player_name}: Successfully downloaded all {report.downloaded_logs} logs."
        )
    else:
        errors = ", ".join(str(error) for error in report.errors)
        logging.error(
            f"{player_name}: Failed to download some logs. Downloaded logs: {report.downloaded_logs}, Failed logs: {report.failed_logs}, Attempts: {report.attempts}, Errors: {errors}"
        )


def main():
    """Main function to load config and start downloading logs."""
    parser = argparse.ArgumentParser(
        description="Download logs from BrightSign players"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to the configuration file",
        default="config.yaml",
    )
    args = parser.parse_args()

    config = load_yaml_config(args.config)
    log_parent_folder = config["log_paths"]["log_parent_folder"]
    players = [Player(player["name"], player["ip"]) for player in config["players"]]

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(download_logs, player, log_parent_folder): player
            for player in players
        }
        for future in concurrent.futures.as_completed(futures):
            player = futures[future]
            report = future.result()
            log_report(player.name, report)


if __name__ == "__main__":
    start_time = time.time()
    main()
    elapsed_time = time.time() - start_time
    logging.info(f"Execution time: {elapsed_time:.2f} seconds")
