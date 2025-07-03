import calendar
import time
import os
from typing import List, Optional, Tuple
from datetime import date
from dateutil.relativedelta import relativedelta


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


def prep_download_folder(folder_name: str) -> str:
    project_root = os.path.dirname(
        os.path.abspath(__file__)
    )  # current script directory
    download_folder = os.path.join(project_root, folder_name)
    os.makedirs(download_folder, exist_ok=True)
    return download_folder


def compute_last_month_range() -> Tuple[date, date]:
    today = date.today()
    previous_month = today - relativedelta(months=1)
    _, previous_month_max_day = calendar.monthrange(
        previous_month.year, previous_month.month
    )
    from_date = today.replace(
        month=previous_month.month, day=1, year=previous_month.year
    )
    to_date = today.replace(
        month=previous_month.month, day=previous_month_max_day, year=previous_month.year
    )
    return from_date, to_date
