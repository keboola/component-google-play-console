"""
Template Component main class.

"""

import os
import logging

from keboola.component.base import ComponentBase
from keboola.component.exceptions import UserException

from configuration import Configuration
from client.cloud_storage_client import CloudStorageClient


class Component(ComponentBase):
    """
    Extends base class for general Python components. Initializes the CommonInterface
    and performs configuration validation.

    For easier debugging the data folder is picked up by default from `../data` path,
    relative to working directory.

    If `debug` parameter is present in the `config.json`, the default logger is set to verbose DEBUG mode.
    """

    def __init__(self):
        super().__init__()

    def run(self):
        """
        Main execution code
        """

        params = Configuration(**self.configuration.parameters)

        logging.info(f"Config initialized.")

        client = CloudStorageClient(params.gcp_service_account_key)

        logging.info(f"Client initialized.")


        path = os.path.join(self.data_folder_path, "artifacts", "out", "current")

        logging.info(f"Path set to {path}")

        client.download_files_from_bucket(params.bucket_id, path)

        logging.info(f"Downloading files from bucket.")


"""
        Main entrypoint
"""
if __name__ == "__main__":
    try:
        comp = Component()
        # this triggers the run method by default and is controlled by the configuration.action parameter
        comp.execute_action()
    except UserException as exc:
        logging.exception(exc)
        exit(1)
    except Exception as exc:
        logging.exception(exc)
        exit(2)
