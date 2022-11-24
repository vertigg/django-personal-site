from typing import Sequence

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def requests_retry_session(
    retries: int = 5,
    backoff_factor: float = 1.2,
    status_forcelist: Sequence[int] = (429, 500, 502, 504, 522),
    session: requests.Session = None
):
    """Create a requests Session object pre-configured for retries

    Args:
        retries (int): number of times to retry request
        backoff_factor (float): amount of time to wait between retries
        status_forcelist (Sequence[int]): http status codes to ignore during retries
        session (Session): optional Session object to apply retry config to

    Returns:
        Session: requests Session object configured for retries

    """
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )

    session = session or requests.Session()
    adapter = HTTPAdapter(max_retries=retry)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
        )
    })

    return session
