import uuid
import json
import io
import gzip
import numpy as np
import azure_config
import logging.config
from azure.storage.blob import ContainerClient
from azure.quantum.job.job import Job
from azure.quantum.optimization import OnlineProblem
from logger.logger_config import LOGGING_CONFIG

# Set up logger
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class ProblemLibrary:
    """A collection of methods used to manage previously uploaded problems"""

    @classmethod
    def get_problem_by_blob_name(cls, blob_name) -> OnlineProblem:
        """Return an OnlineProblem, for a previously uploaded problem, given its blob name"""
        logger.debug("()")
        container_uri = azure_config.WORKSPACE.get_container_uri(
            container_name="qio-problems"
        )
        container_uri = container_uri.split("?")[0]
        blob_uri = container_uri + "/" + blob_name
        online_problem_name = "o_prob_" + blob_name
        online_problem = OnlineProblem(name=online_problem_name, blob_uri=blob_uri)
        logger.debug("- Return")
        return online_problem

    @classmethod
    def _pos_or_neg(cls):
        if np.random.rand() < 0.5:
            return 1
        else:
            return -1

    @classmethod
    def _random_qubo_json(cls, n):
        """Generate a random QUBO"""
        logger.debug("()")
        INPUT_DATA_METADATA_NAME = "metadata_name"
        SOLVER_FORMAT_VERSION = "1.1"

        # create qubo request
        terms_list = []

        if n > 0:
            # create random n x n matrix of negative float coefficient values
            result_array = np.random.uniform(-1000, 0, (n, n))

            # add random non-zero float constant value
            c = np.random.uniform(-1000, 0) * cls._pos_or_neg()
            term = {"c": c, "ids": []}
            terms_list.append(term)

            # add upper triangular of matrix
            for i in range(n):
                for j in range(i, n):
                    # add random non-zero float coefficient value
                    if i == j:
                        c = result_array[i][j] * cls._pos_or_neg()
                        term = {"c": c, "ids": [i]}
                        terms_list.append(term)
                    else:
                        c = result_array[i][j] * cls._pos_or_neg()
                        term = {"c": c, "ids": [i, j]}
                        terms_list.append(term)

        qubo_json = {
            "metadata": {"name": INPUT_DATA_METADATA_NAME},
            "cost_function": {
                "type": "ising",
                "version": SOLVER_FORMAT_VERSION,
                "terms": terms_list,
            },
        }

        logger.debug("- Return")
        return qubo_json

    @classmethod
    def generate_random_qubo(cls, size, blob_name=""):
        """Generate and upload a random QUBO"""
        # create QUBO
        logger.debug("()")
        qubo = cls._random_qubo_json(n=size)
        if blob_name == "":
            blob_name = str(uuid.uuid4()) + "_random_qubo_" + str(size)
        # upload QUBO to Azure Blob Storage
        blob_uri = cls.upload_problem(qubo=qubo, blob_name=blob_name)

        logger.debug("- Return")
        return blob_name, blob_uri

    @classmethod
    def generate_random_qubo_if_not_exists(cls, size, blob_name=""):
        """Generate and upload a random QUBO of the given size (if it doesn't exist)."""
        logger.debug("()")
        if blob_name == "":
            blob_name = "random_qubo_" + str(size)

        container_client = ContainerClient.from_container_url(
            azure_config.WORKSPACE.get_container_uri(container_name="qio-problems")
        )
        blob_client = container_client.get_blob_client(blob_name)
        # Check if a blob with that name already exists
        if not blob_client.exists():
            # Generate and upload a random QUBO
            blob_name, blob_uri = cls.generate_random_qubo(
                size=size, blob_name=blob_name
            )
        else:
            online_problem = cls.get_problem_by_blob_name(blob_name)
            blob_uri = online_problem.uploaded_blob_uri

        logger.debug("- Return")
        return blob_name, blob_uri

    @classmethod
    def upload_problem(cls, qubo, blob_name):
        """Upload a QUBO"""
        # create blob from qubo; gzip before upload
        logger.debug("()")
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="w") as fo:
            fo.write(json.dumps(qubo).encode())
        blob = out.getvalue()

        container_uri = azure_config.WORKSPACE.get_container_uri(
            container_name="qio-problems"
        )
        blob_uri = Job.upload_input_data(
            input_data=blob,
            blob_name=blob_name,
            container_uri=container_uri,
            encoding="gzip",
            content_type="application/json",
        )
        logger.debug("- Return")
        return blob_uri
