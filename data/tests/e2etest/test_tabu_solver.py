from msq.Experiment import Experiment
from msq.SolverFactory import SolverFactory
from msq.ProblemLibrary import ProblemLibrary
from tests.e2etest.test_solver import TestSolver
import pytest
from enum import Enum


class tabu_solver_error(str, Enum):
    ERROR_TABU_IMPROVEMENT_CUTOFF = (
        "Invalid value passed for improvement_cutoff: improvement_cutoff must be >= 0"
    )
    ERROR_TABU_IMPROVEMENT_TOLERANCE = "Invalid value passed for improvement_tolerance: improvement_tolerance must be >= 0"
    ERROR_TABU_SEED = "Invalid value passed for seed: seed must be >= 0"
    ERROR_TABU_TABU_TENURE = (
        "Invalid value passed for tabu_tenure: tabu_tenure must be >= 0"
    )
    ERROR_TABU_TABU_TENURE_RAND_MAX = "Invalid value passed for tabu_tenure_rand_max: tabu_tenure_rand_max must be in the range [1, 200000]"
    ERROR_TABU_TIMEOUT = "Invalid value passed for timeout: timeout must be >= 0"

    def __str__(self):
        return self.name

@pytest.mark.usefixtures("problem_list")
class TestTabuSolver(TestSolver):
    def test_input_params_tabu_success(self, problem_list):

        """Pass positive solver parameter to create solver and validate the success of experiment
        This function creates a Tabu solver with valid solver parameters and uses this solver to 
        submit an experiment for problem created by test fixture. Later it validates the Success 
        of experiment by getting experiment details and checking status and parameters
        """

        solver_params = {
            "improvement_cutoff": "4",
            "improvement_tolerance": "1e-09",
            "seed": "3",
            "tabu_tenure": "3",
            "tabu_tenure_rand_max": "4",
            "timeout": "10",
        }
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
            result[0]["parameters"]["improvement_cutoff"]
            == solver_params["improvement_cutoff"]
        )
        assert (
            result[0]["parameters"]["improvement_tolerance"]
            == solver_params["improvement_tolerance"]
        )
        assert result[0]["parameters"]["seed"] == solver_params["seed"]
        assert result[0]["parameters"]["tabu_tenure"] == solver_params["tabu_tenure"]
        assert (
            result[0]["parameters"]["tabu_tenure_rand_max"]
            == solver_params["tabu_tenure_rand_max"]
        )
        assert (
            result[0]["parameters"]["improvement_cutoff"]
            == solver_params["improvement_cutoff"]
        )
        # verify the solver
        assert result[0]["parameters"]["solver_name"] == "Tabu"
        # verify the number of iteration
        assert result[0]["experiment"]["num_iterations"] == 1
        # add all the job containers for the cleanup
        for result in result:
            container_name = "job-" + result["id"]
            pytest.container_ids.append(container_name)

    def test_input_params_for_multiple_problems_tabu_success(self, problem_list):

        """Pass positive solver parameter to create Tabu solver and  validate the success of experiment
        This function creates a Tabu solver with valid solver parameters and uses this solver to submit 
        an experiment for problem created by test fixture.We add another problem into the problem set to 
        test how are Experiment is performing when multiple solvers are passed Later  it validates.
        The Success of experiment by getting experiment details and checking status and parameters
        """

        solver_params = {
            "improvement_cutoff": "4",
            "improvement_tolerance": "1e-09",
            "seed": "3",
            "tabu_tenure": "3",
            "tabu_tenure_rand_max": "4",
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
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
                job["parameters"]["improvement_cutoff"]
                == solver_params["improvement_cutoff"]
            )
            assert (
                job["parameters"]["improvement_tolerance"]
                == solver_params["improvement_tolerance"]
            )
            assert job["parameters"]["seed"] == solver_params["seed"]
            assert job["parameters"]["tabu_tenure"] == solver_params["tabu_tenure"]
            assert (
                job["parameters"]["tabu_tenure_rand_max"]
                == solver_params["tabu_tenure_rand_max"]
            )
            assert (
                job["parameters"]["improvement_cutoff"]
                == solver_params["improvement_cutoff"]
            )
            # verify the solver
            assert job["parameters"]["solver_name"] == "Tabu"
            # verify the number of iteration
            assert job["experiment"]["num_iterations"] == number_of_iterations
            # add all the job containers for the cleanup
            container_name = "job-" + job["id"]
            pytest.container_ids.append(container_name)

        # remove the extra problem created
        problem_list.pop()

    def test_tabu_success_improvement_tolerance_int(self, problem_list):

        """Pass positive solver parameter to create solver and validate the success of experiment
        This function creates a Tabu solver with valid imporvement_tolerance parameter and
        uses this solver to submit an experiment for problem created by test fixture. Later it validates
        the Success of experiment by getting experiment details and checking status and parameters
        """

        solver_params = {"improvement_tolerance": "2"}
        # solve
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
            result[0]["parameters"]["improvement_tolerance"]
            == solver_params["improvement_tolerance"]
        )
        # verify the solver
        assert result[0]["parameters"]["solver_name"] == "Tabu"
        # verify the number of iteration
        assert result[0]["experiment"]["num_iterations"] == 1
        for result in result:
            container_name = "job-" + result["id"]
            pytest.container_ids.append(container_name)

    def test_tabu_success_tabu_tenure_rand_max_upperbound(self, problem_list):

        """Pass positive solver parameter to create solver and validate the success of experiment
        This function creates a Tabu solver with valid upperbound tabu_tenure_rand_max parameter value 
        and uses this solver to submit an experiment for problem created by test fixture. Later it validates
        the Success of experiment by getting experiment details and checking status and parameters
        """

        solver_params = {"tabu_tenure_rand_max": "200000"}
        # solve
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
            result[0]["parameters"]["tabu_tenure_rand_max"]
            == solver_params["tabu_tenure_rand_max"]
        )
        # verify the solver
        assert result[0]["parameters"]["solver_name"] == "Tabu"
        # verify the number of iteration
        assert result[0]["experiment"]["num_iterations"] == 1
        for result in result:
            container_name = "job-" + result["id"]
            pytest.container_ids.append(container_name)

    def test_tabu_error_negative_timeout(self, problem_list):

        """Pass negative timeout parameter to create Tabu solver and  
        validate the failure of experiment along with the correct error 
        message
        """

        solver_params = {"timeout": -1}
        # solve
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
            tabu_solver_error.ERROR_TABU_TIMEOUT
            in result[0]["error_data"]["message"]
        )

    def test_tabu_error_tabu_tenure_rand_max_upperbound_plus1(self, problem_list):

        """Pass out of bound tabu_tenure_rand_max value to create Tabu solver and  
        validate the failure of experiment along with the correct error message
        """

        solver_params = {"tabu_tenure_rand_max": 200001}
        # solve
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
            tabu_solver_error.ERROR_TABU_TABU_TENURE_RAND_MAX
            in result[0]["error_data"]["message"]
        )

    def test_tabu_error_negative_seed(self, problem_list):

        """Pass negative seed value as parameter to create Tabu solver and  
        validate the failure of experiment along with the correct error message
        """

        solver_params = {"seed": -1}
        # solve
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
            tabu_solver_error.ERROR_TABU_SEED
            in result[0]["error_data"]["message"]
        )

    def test_tabu_error_negative_improvement_tolerance(self, problem_list):

        """Pass negative improvement_tolerance as parameter to create Tabu solver 
        and  validate the failure of experiment along with the correct error message
        """

        solver_params = {"improvement_tolerance": -1}
        # solve
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
            tabu_solver_error.ERROR_TABU_IMPROVEMENT_TOLERANCE
            in result[0]["error_data"]["message"]
        )

    def test_tabu_error_negative_tabu_tenure(self, problem_list):

        """Pass negative tabu_tenure as parameter to create Tabu solver and  
        validate the failure of experiment along with the correct error message
        """

        solver_params = {"tabu_tenure": -1}
        # solve
        solver = SolverFactory.generate_tabu_search_solvers([solver_params])
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
            tabu_solver_error.ERROR_TABU_TABU_TENURE
            in result[0]["error_data"]["message"]
        )
