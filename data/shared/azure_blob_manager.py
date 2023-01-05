import logging.config
from uuid import uuid4
from datetime import datetime, timedelta
from pathlib import Path
from azure.storage.blob import (
    ContainerClient,
)
from logger.logger_config import LOGGING_CONFIG


# Set up logger
logger = logging.getLogger(__name__)


class AzureBlobManager:
    def __init__(self, account_name=None, data_path="data"):
        """
        Initialize the AzureBlobManager.

        Args:
                data_path (str): Path to data folder.
        """
        self.account_name = account_name
        self.data_path = data_path

        if not self.account_name:
            raise Exception("Please provide a valid storage account name")

    def delete_container_if_exist(self, connection_str, container_name):
        """
        Delete a storage container in Azure if it exists.

        Args:
            container_name (str): The name of the container to be deleted.
            connection_str (str): The connection string of an Azure storage account,
                where the new container will be searched and deleted.

        Returns:
            container(ContainerClient): A container client created from the connection string.
        """
        logger.debug(
            f"container_name={container_name}, connection_str={connection_str}"
        )

        container = ContainerClient.from_connection_string(
            connection_str, container_name
        )

        if container.exists():
            container.delete_container()

        return container
