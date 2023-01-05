from msq.Experiment import Experiment
from msq.SolverFactory import SolverFactory
from msq.ProblemLibrary import ProblemLibrary
from tests.e2etest.test_solver import TestSolver
import azure_config
import pytest
from enum import Enum
import logging.config
from logger.logger_config import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class prl_solver_error(str, Enum):
    ERROR_PRL_DISTANCE_SCALE = "Invalid value passed for distance_scale: distance_scale must be in the range (0.0, 0.5)"
    ERROR_PRL_GREEDY_PATH_RELINKING = "value could not be parsed to a boolean"
    ERROR_PRL_REF_SET_COUNT = "Invalid value passed for ref_set_count: Ref set count must be in the range [2, 500]"
    ERROR_PRL_SEED = "Invalid value passed for seed: seed must be >= 0"
    ERROR_PRL_TIMEOUT = "Invalid value passed for timeout: timeout must be >= 0"

    def __str__(self):
        return self.name


@pytest.mark.usefixtures("problem_list")
class TestPrlSolver(TestSolver):
    """
    Build E2E test suit for PRL Solvers by covering positive , negative and edge test cases
    """
    def test_input_params_prl_success(self, problem_list):

        """Pass positive solver parameter to create solver and validate the success of experiment
        This function creates a path relinking solver with valid solver parameters and uses this 
        solver to submit an experiment for problem created by test fixture.Later it validates
        the Success of experiment by getting experiment details and checking status and parameters
        """

        logger.info("E2E test running")

        solver_params = {
            "distance_scale": "0.2",
            "greedy_path_relinking": "true",
            "seed": "2",
            "ref_set_count": "2",
            "timeout": "10",
        }
        solver = SolverFactory.generate_path_relinking_solvers([solver_params])
        # solve
        experiment = Experiment(solver, problem_list)
        experiment.submit()
        experiment.wait_until_completed()
        result = experiment.get_experiment_details()
        # length of results
        assert len(result) == 1
        # validate status of experiment
        assert result[0]["status"] == "Succeeded"
        # verify all parameters correctly set in output
        assert (
            result[0]["parameters"]["distance_scale"] == solver_params["distance_scale"]
        )
        assert (
            result[0]["parameters"]["greedy_path_relinking"]
            == solver_params["greedy_path_relinking"]
        )
        assert result[0]["parameters"]["seed"] == solver_params["seed"]
        assert (
            result[0]["parameters"]["ref_set_count"] == solver_params["ref_set_count"]
        )
        assert result[0]["parameters"]["timeout"] == solver_params["timeout"]
        # verify the solver
        assert result[0]["parameters"]["solver_name"] == "PathRelinking"
        # verify the number of iteration
        assert result[0]["experiment"]["num_iterations"] == 1
        # add all the job containers for the cleanup
        for result in result:
            container_name = "job-" + result["id"]
            pytest.container_ids.append(container_name)

    def test_multiple_problems_prl_success(self, problem_list):

        """Pass positive solver parameter to create solver and  validate the success of experiment
        This function creates a path relinking solver with valid solver parameters and uses this solver 
        to submit an experiment for problem created by test fixture.We add another problem into the problem 
        set to test how are Experiment is performing when multiple solvers are passed Later it validates the
        Success of experiment by getting experiment details and checking status and parameters
        """

        solver_params = {
            "distance_scale": "0.2",
            "greedy_path_relinking": "true",
            "seed": "2",
            "ref_set_count": "2",
            "timeout": "10",
        }
        # create new problem and add to existing problem set
        blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(
            size=int(pytest.qubo_size)
        )
        problem = ProblemLibrary.get_problem_by_blob_name(blob_name)
        problem_list.append(problem)
        # define number of iterations
        number_of_iterations = 2
        solver = SolverFactory.generate_path_relinking_solvers([solver_params])
        # solve
        experiment = Experiment(solver, problem_list, number_of_iterations)
        experiment.submit()
        experiment.wait_until_completed()
        result = experiment.get_experiment_details()
        # length of results
        assert len(result) == number_of_iterations * len(problem_list)
        for job in result:
            # validate status of experiment
            assert job["status"] == "Succeeded"
            # verify all parameters correctly set in output
            assert (
                job["parameters"]["distance_scale"] == solver_params["distance_scale"]
            )
            assert (
                job["parameters"]["greedy_path_relinking"]
                == solver_params["greedy_path_relinking"]
            )
            assert job["parameters"]["seed"] == solver_params["seed"]
            assert job["parameters"]["ref_set_count"] == solver_params["ref_set_count"]
            assert job["parameters"]["timeout"] == solver_params["timeout"]
            # verify the solver
            assert job["parameters"]["solver_name"] == "PathRelinking"
            # verify the number of iteration
            assert job["experiment"]["num_iterations"] == number_of_iterations
            # add all the job containers for the cleanup
            container_name = "job-" + job["id"]
            pytest.container_ids.append(container_name)

        # remove the extra problem created
        problem_list.pop()

    def test_prl_error_negative_timeout(self, problem_list):

        """Pass negative timeout parameter to create solver and  validate the failure of experiment
        along with the correct error message
        """

        solver_params = {"timeout": -1}
        # solve
        solver = SolverFactory.generate_path_relinking_solvers([solver_params])
        experiment = Experiment(solver, problem_list)
        experiment.submit()
        experiment.wait_until_completed()
        result = experiment.get_experiment_details()
        # status failed
        assert result[0]["status"] == "Failed"
        # status code validation
        assert result[0]["error_data"]["code"] == "InvalidProperty"
        # validate the error message
        assert (
            prl_solver_error.ERROR_PRL_TIMEOUT
            in result[0]["error_data"]["message"]
        )

    def test_prl_error_negative_seed(self, problem_list):

        """Pass negative seed parameter to create solver and  validate the failure of experiment
        along with the correct error message
        """

        solver_params = {"seed": -1}
        # solve
        solver = SolverFactory.generate_path_relinking_solvers([solver_params])
        experiment = Experiment(solver, problem_list)
        experiment.submit()
        experiment.wait_until_completed()
        result = experiment.get_experiment_details()
        # status failed
        assert result[0]["status"] == "Failed"
        # status code validation
        assert result[0]["error_data"]["code"] == "InvalidProperty"
        # validate the error message
        assert (
            prl_solver_error.ERROR_PRL_SEED in result[0]["error_data"]["message"]
        )

    def test_prl_error_distance_scale_exclusive_upper_bound(self, problem_list):

        """Pass upper bound distance scale parameter to create solver and  validate the failure 
        of experiment along with the correct error message
        """

        solver_params = {"distance_scale": 0.5}
        # solve
        solver = SolverFactory.generate_path_relinking_solvers([solver_params])
        experiment = Experiment(solver, problem_list)
        experiment.submit()
        experiment.wait_until_completed()
        result = experiment.get_experiment_details()
        # status failed
        assert result[0]["status"] == "Failed"
        # status code validation
        assert result[0]["error_data"]["code"] == "InvalidProperty"
        # validate the error message
        assert (
            prl_solver_error.ERROR_PRL_DISTANCE_SCALE
            in result[0]["error_data"]["message"]
        )

    def test_prl_error_invalid_greedy_path_relinking(self, problem_list):

        """Pass invalid greedy_path_relinking parameter to create solver and  
        validate the failure of experiment along with the correct error message
        """

        solver_params = {"greedy_path_relinking": "test_string"}
        # solve
        solver = SolverFactory.generate_path_relinking_solvers([solver_params])
        experiment = Experiment(solver, problem_list)
        experiment.submit()
        experiment.wait_until_completed()
        result = experiment.get_experiment_details()

        # status failed
        assert result[0]["status"] == "Failed"
        # status code validation
        assert result[0]["error_data"]["code"] == "InvalidProperty"
        # validate the error message
        assert (
            prl_solver_error.ERROR_PRL_GREEDY_PATH_RELINKING
            in result[0]["error_data"]["message"]
        )
