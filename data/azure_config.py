import os
from azure.quantum import Workspace
import logging.config


logger = logging.getLogger(__name__)

# Azure configuration
AZURE_SUBSCRIPTION_ID    = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
AZURE_RESOURCE_GROUP     = os.environ.get("AZURE_RESOURCE_GROUP", "")
AZURE_WORKSPACE_NAME     = os.environ.get("AZURE_WORKSPACE_NAME", "")
AZURE_WORKSPACE_LOCATION = os.environ.get("AZURE_WORKSPACE_LOCATION", "")


# Workspace information
try:
    WORKSPACE = Workspace(
        subscription_id=AZURE_SUBSCRIPTION_ID,  # add your subscription_id
        resource_group=AZURE_RESOURCE_GROUP,  # add your resource_group
        name=AZURE_WORKSPACE_NAME,  # add your workspace name
        location=AZURE_WORKSPACE_LOCATION,  # add your workspace location
    )
except Exception:
    pass


