from msq.ProblemLibrary import ProblemLibrary
from shared.azure_blob_manager import AzureBlobManager
from shared.azure_manager import AzureManager
import azure_config
import logging.config
import pytest
import os
import json
import requests


logger = logging.getLogger(__name__)

def pytest_configure():

    # 1. Load in extra env vars

    AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
    AZURE_STORAGE_ACCOUNT_NAME = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")
    AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")

    # 2. Create shared azure_manager here

    try:
        # Create azure manager to manage the infrastructure resource group
        pytest.azure_manager = AzureManager(
            AZURE_CLIENT_ID,
            AZURE_CLIENT_SECRET,
            AZURE_TENANT_ID,
            azure_config.AZURE_SUBSCRIPTION_ID,
            azure_config.AZURE_RESOURCE_GROUP,
            AZURE_STORAGE_ACCOUNT_NAME,
        )

    except Exception as e:
        err_msg = f"Failed to create azure manager to manage infrastructure resource group: {e}."
        logger.error(err_msg)
        raise Exception(err_msg)

    # 3. Create shared blob manager

    try:
        # Create azure blob manager
        pytest.azure_blob_manager = AzureBlobManager(
            account_name=AZURE_STORAGE_ACCOUNT_NAME
        )
    except Exception as e:
        err_msg = f"Failed to create azure blob manager: {e}"
        logger.error(err_msg)
        pass

    # default QUBO size
    pytest.qubo_size = os.environ.get("DEFAULT_TEST_QUBO_SIZE", "1028")

    # create a problem and add it to problem list
    blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(
        size=int(pytest.qubo_size)
    )

    # create shared problem list here
    pytest.problem_list = [
        ProblemLibrary.get_problem_by_blob_name(blob_name),
    ]



def post_reports_to_slack():

        url= "https://hooks.slack.com/services/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"  

        #To generate report file add "> pytest_report.log" at end of py.test command for e.g. py.test -v > pytest_report.log
        test_report_file = '/usr/src/app/pytest_report.txt' #Add report file name and address here
 
        # Open report file and read data
        with open(test_report_file, "r") as in_file:
                testdata = ""
                for line in in_file:
                        testdata = testdata + '\n' + line
 
        # Set Slack Pass Fail bar indicator color according to test results   
        if 'FAILED' in testdata:
            bar_color = "#ff0000"
        else:
            bar_color = "#36a64f"
 
        # Arrange your data in pre-defined format. Test your data format here: https://api.slack.com/docs/messages/builder?  
        data = {"attachments":[
                            {"color": bar_color,
                            "title": "Test Report",
                            "text": testdata}
                            ]}
        json_params_encoded = json.dumps(data)
        slack_response = requests.post(url=url,data=json_params_encoded,headers={"Content-type":"application/json"})
        if slack_response.text == 'ok':
                print("Successfully posted pytest report on Slack channel")
        else:
                print("Something went wrong. Unable to post pytest report on Slack channel")



class TestSolver:

    """The base class providing azure client and problem to tests"""

    pytest_configure()

    @pytest.fixture(scope="session")
    def problem_list(self):

        # collect container Id's to clear it up later
        pytest.container_ids = []
        self.connection_str = pytest.azure_manager.get_storage_connection_string()

        # hold off on cleaning until the test is finished.
        yield pytest.problem_list
        # clean job containers from msq

        if len(pytest.container_ids) > 0:
            for container in pytest.container_ids:
                pytest.azure_blob_manager.delete_container_if_exist(
                    self.connection_str, container
                )
