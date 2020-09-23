import requests
from pathlib import Path
from .base import Task


class URLDownloaderTask(Task):
    """
    This task periodically downloads a url and saves the HTML data in a file.
    """
    def execute(self, url: str, output_path: str, create_dir: bool = False):
        """
        :param url: URL to download.
        :param output_path: Location in which to save the HTML data.
        :param create_dir: Whether to write the response even if the directory of output_file doesn't exist (will create it).
        """
        output = Path(output_path)
        if create_dir:
            output.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Downloading url \"{url}\"")
        response = requests.get(url)
        response.raise_for_status()
        output.write_text(response.text)
        self.logger.info(f"Download complete for url \"{url}\"")
