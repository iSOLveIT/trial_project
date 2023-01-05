from logging import raiseExceptions
import os
import subprocess
import time


class AzureManager:
    """An Azure Manager handles all the actions with Azure account"""

    def __init__(
        self,
        client_id,
        client_secret,
        tenant_id,
        subscription,
        resource_group_name,
        storage_account,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.resource_group_name = resource_group_name
        self.subscription = subscription
        self.cosmosdb_account_name = None
        self.storage_account_name = storage_account
        self.login()
        # The default subscription is not correct. Therefore, we need to set the
        # subscription.
        self.set_subscription()

    def login(self):
        """Log in with credentials"""
        login_command = (
            "az login --service-principal -u "
            + self.client_id
            + " -p "
            + self.client_secret
            + " --tenant "
            + self.tenant_id
        )

        login_output = subprocess.run(
            login_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # reading error
        err = login_output.stderr.decode("utf-8")
        # MC will return a python mismatch error so we should ignore it
        if err and "Python 3.6" not in err:
            err_msg = f"login failed: {err}"
            print(err_msg)
            raise Exception(err_msg)
        else:
            print("login success")

    def set_subscription(self):
        """Set a subscription to be the current active subscription."""
        set_subscription_command = "az account set -s " + self.subscription

        set_subscription_output = subprocess.run(
            set_subscription_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # reading error
        err = set_subscription_output.stderr.decode("utf-8")
        if err:
            err_msg = f"set subscription failed: {err}"
            print(err_msg)
            raise Exception(err_msg)
        else:
            print("set subscription success")

    def create_cosmosdb(self, cosmosdb_account_name):
        """Create cosmosdb account"""
        self.cosmosdb_account_name = cosmosdb_account_name
        cosmosdb_command = (
            "az cosmosdb create --name "
            + self.cosmosdb_account_name
            + " --resource-group "
            + self.resource_group_name
        )

        create_cosmosdb_output = subprocess.run(
            cosmosdb_command, shell=True, stderr=subprocess.PIPE
        )

        # reading error
        err = create_cosmosdb_output.stderr.decode("utf-8")

        if err:
            err_msg = f"Create cosmosdb failed: {err}"
            print(err_msg)
            raise Exception(err_msg)
        else:
            print("Create cosmosdb success")

    def get_cosmosdb_url(self):
        return "https://" + self.cosmosdb_account_name + ".documents.azure.com:443/"

    def get_cosmosdb_key(self):
        get_key_command = (
            "az cosmosdb keys list --name "
            + self.cosmosdb_account_name
            + " --resource-group "
            + self.resource_group_name
            + " --output json "
            + "--query [primaryMasterKey]"
        )

        retries = 5
        has_key = False
        while retries > 0 and not has_key:
            get_key_output = subprocess.run(
                get_key_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # reading output and error
            output = get_key_output.stdout.decode("utf-8")
            err = get_key_output.stderr.decode("utf-8")

            if err:
                err_msg = f"Get comosdb key failed: {err}"
                print(err_msg)
                time.sleep(5)
                retries -= 1
            else:
                print("Get cosmosdb key success")
                has_key = True
                break

        if not has_key:
            err_msg = f"AzureManager timed out trying to get comosdb key."
            print(err_msg)
            raise Exception(err_msg)

        return output

    def get_storage_account_key(self):
        get_key_command = (
            "az storage account keys list --account-name "
            + self.storage_account_name
            + " --resource-group "
            + self.resource_group_name
            + " --output json "
            + "--query [0].value"
        )
        get_key_output = subprocess.run(
            get_key_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # reading output and error
        output = get_key_output.stdout.decode("utf-8")
        err = get_key_output.stderr.decode("utf-8")

        # MC will return a python mismatch error so we should ignore it
        if err and "Python 3.6" not in err:
            err_msg = f"Get storage account key failed: {err}"
            print(err_msg)
            raise Exception(err_msg)
        else:
            print("Get storage account key success")
        return output

    def get_storage_connection_string(self):

        get_key_command = (
            "az storage account show-connection-string --name "
            + self.storage_account_name
            + " --resource-group "
            + self.resource_group_name
            + " --output json "
            + "--query connectionString"
        )

        get_key_output = subprocess.run(
            get_key_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # reading output and error
        output = get_key_output.stdout.decode("utf-8")
        err = get_key_output.stderr.decode("utf-8")

        # MC will return a python mismatch error so we should ignore it
        if err and "Python 3.6" not in err:
            err_msg = f"Get storage connection string failed: {err}"
            print(err_msg)
            raise Exception(err_msg)
        else:
            print("Get storage account connection string success")
        return output
