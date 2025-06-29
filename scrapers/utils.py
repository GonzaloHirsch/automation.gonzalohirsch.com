import time
import os
from typing import List, Optional


def wait_for_download_to_finish(
    download_dir: str,
    ignore_pattern: List[str],
    timeout: int = 60,
    interval: float = 0.5,
) -> Optional[str]:
    """
    Waits for a file to appear in the download_dir and for its .crdownload to finish.
    Returns the path to the completed file, or None on timeout.
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        files = os.listdir(download_dir)
        if not files:
            time.sleep(interval)
            continue

        for file in files:
            if file.endswith(".crdownload"):
                continue  # still downloading
            file_path = os.path.join(download_dir, file)
            # Check if the file does not match any ignore patterns.
            if os.path.isfile(file_path) and not any(
                [pattern in file for pattern in ignore_pattern]
            ):
                return file_path

        time.sleep(interval)

    return None  # Timeout
