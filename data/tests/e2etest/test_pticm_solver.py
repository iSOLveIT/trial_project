from msq.Experiment import Experiment
from tests.e2etest.test_solver import TestSolver
from msq.SolverFactory import SolverFactory
import pytest
from enum import Enum


class pticm_goal(str, Enum):
    OPTIMIZE = "OPTIMIZE"
    SAMPLE = "SAMPLE"

    def __str__(self):
        return self.name


class pticm_scaling_type(str, Enum):
    MEDIAN = "MEDIAN"
    NO_SCALING = "NO_SCALING"

    def __str__(self):
        return self.name


class pticm_var_fixing_type(str, Enum):
    NO_FIXING = "NO_FIXING"
    PERSISTENCY = "PERSISTENCY"
    SPVAR = "SPVAR"

    def __str__(self):
        return self.name


class pticm_solver_error(str, Enum):
    ERROR_PTICM_ELITE_THRESHOLD = "Invalid value passed for elite_threshold: Elite threshold must be in the range [0-1]"
    ERROR_PTICM_FRAC_ICM_THERMAL_LAYERS = "Invalid value passed for frac_icm_thermal_layers: Frac icm thermal layers must be in the range [0-1]"
    ERROR_PTICM_FRAC_SWEEPS_IDLE = "Invalid value passed for frac_sweeps_idle: Frac sweeps idle must be in the range [0-1]]"
    ERROR_PTICM_FRAC_SWEEPS_STAGNATION = "Invalid value passed for frac_sweeps_stagnation: Frac sweeps stagnation must be in the range [0-1]]"
    ERROR_PTICM_HIGH_TEMP = "Invalid value passed for high_temp: high_temp must be >= 0"
    ERROR_PTICM_HIGH_TEMP_WITH_AUTO_SET_TEMPERATURES_TRUE = (
        "auto_set_temperatures should be set to false to use high temp"
    )
    ERROR_PTICM_LOW_TEMP = "Invalid value passed for low_temp: low_temp must be >= 0"
    ERROR_PTICM_MAX_TOTAL_SWEEPS = (
        "Invalid value passed for max_total_sweeps: max_total_sweeps must be >= 0"
    )
    ERROR_PTICM_NUM_ELITE_TEMPS = "Invalid value passed for num_elite_temps: Number of elite temps cannot be less than 1"
    ERROR_PTICM_NUM_REPLICAS = "Invalid value passed for num_replicas: Number of replicas must be in the range [2, 10000]"
    ERROR_PTICM_NUM_SWEEPS_PER_RUN = "Invalid value passed for num_sweeps_per_run: Number of sweeps per run must be in the range [2, 10000000]"
    ERROR_PTICM_NUM_TEMPS_WITH_AUTO_SET_TEMPERATURES_TRUE = (
        "auto_set_temperatures should be set to false to use the number of temperatures"
    )
    ERROR_PTICM_SEED = "Invalid value passed for seed: seed must be >= 0"

    def __str__(self):
        return self.name


@pytest.mark.usefixtures("problem_list")
class TestPticmSolver(TestSolver):
    """
    Build E2E test suit for Pticm Solvers by covering positive , negative and edge test cases
    """
    def test_input_params_pticm_success_set1_automatic_temperatures(self, problem_list):
        
        """Pass positive solver parameter to create solver and validate the success of experiment
        This function creates a pticm solver with valid solver parameters and uses this solver to 
        submit an experiment for problem created by test fixture. Later it validates the Success of 
        experiment by getting experiment details and checking status and parameters
        """

        solver_params = {
            "auto_set_temperatures": "true",
            "elite_threshold": "0.3",
            "frac_icm_thermal_layers": "0.5",
            "frac_sweeps_fixing": "0.15",
            "frac_sweeps_idle": "0.4",
            "frac_sweeps_stagnation": "0.4",
            "goal": pticm_goal.OPTIMIZE,
            "max_samples_per_layer": "10",
            "max_total_sweeps": "100",
            "num_elite_temps": "4",
            "num_replicas": "2",
            "num_sweeps_per_run": "10",
            "scaling_type": pticm_scaling_type.NO_SCALING,
            "seed": "2",
            "var_fixing_type": pticm_var_fixing_type.NO_FIXING,
        }
        solver = SolverFactory.generate_pticm_solvers([solver_params])
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
            result[0]["parameters"]["auto_set_temperatures"]
            == solver_params["auto_set_temperatures"]
        )
        assert (
            result[0]["parameters"]["elite_threshold"]
            == solver_params["elite_threshold"]
        )
        assert (
            result[0]["parameters"]["frac_icm_thermal_layers"]
            == solver_params["frac_icm_thermal_layers"]
        )
        assert (
            result[0]["parameters"]["frac_sweeps_fixing"]
            == solver_params["frac_sweeps_fixing"]
        )
        assert (
            result[0]["parameters"]["frac_sweeps_idle"]
            == solver_params["frac_sweeps_idle"]
        )
        assert (
            result[0]["parameters"]["frac_sweeps_stagnation"]
            == solver_params["frac_sweeps_stagnation"]
        )
        assert result[0]["parameters"]["goal"] == solver_params["goal"]
        assert (
            result[0]["parameters"]["max_samples_per_layer"]
            == solver_params["max_samples_per_layer"]
        )
        assert (
            result[0]["parameters"]["max_total_sweeps"]
            == solver_params["max_total_sweeps"]
        )
        assert (
            result[0]["parameters"]["num_elite_temps"]
            == solver_params["num_elite_temps"]
        )
        assert result[0]["parameters"]["num_replicas"] == solver_params["num_replicas"]
        assert (
            result[0]["parameters"]["num_sweeps_per_run"]
            == solver_params["num_sweeps_per_run"]
        )
        assert result[0]["parameters"]["scaling_type"] == solver_params["scaling_type"]
        assert result[0]["parameters"]["seed"] == solver_params["seed"]
        assert (
            result[0]["parameters"]["var_fixing_type"]
            == solver_params["var_fixing_type"]
        )
        # verify the solver
        assert result[0]["parameters"]["solver_name"] == "PTICM"
        # verify the number of iteration
        assert result[0]["experiment"]["num_iterations"] == 1
        for result in result:
            container_name = "job-" + result["id"]
            pytest.container_ids.append(container_name)

    def test_input_params_pticm_success_set2_temperatures_by_num_temps(
        self, problem_list
    ):
        solver_params = {
            "auto_set_temperatures": "false",
            "high_temp": "2",
            "low_temp": "0.2",
            "num_temps": "30",
        }
        solver = SolverFactory.generate_pticm_solvers([solver_params])
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
            result[0]["parameters"]["auto_set_temperatures"]
            == solver_params["auto_set_temperatures"]
        )
        assert result[0]["parameters"]["high_temp"] == solver_params["high_temp"]
        assert result[0]["parameters"]["low_temp"] == solver_params["low_temp"]
        assert result[0]["parameters"]["num_temps"] == solver_params["num_temps"]
        # verify the solver
        assert result[0]["parameters"]["solver_name"] == "PTICM"
        # verify the number of iteration
        assert result[0]["experiment"]["num_iterations"] == 1
        for result in result:
            container_name = "job-" + result["id"]
            pytest.container_ids.append(container_name)

    def test_pticm_error_negative_high_temp(self, problem_list):

        """Pass negative high_temperature value and incorrect auto_set_temp 
        parameter to create solver and  validate the failure of experiment
        along with the correct error message
        """

        solver_params = {"auto_set_temperatures": "false", "high_temp": "-1"}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_HIGH_TEMP
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_negative_low_temp(self, problem_list):

        """Pass negative low_temperature value and incorrect auto_set_temp parameter
        to create solver and  validate the failure of experiment along with the correct
        error message
        """

        solver_params = {"auto_set_temperatures": "false", "low_temp": "-1"}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_LOW_TEMP
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_num_replicas_lowerbound_minus1(self, problem_list):

        """Pass out of bound num_replica value to create solver and  validate
        the failure of experiment along with the correct error message
        """

        solver_params = {"num_replicas": 1}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_NUM_REPLICAS
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_num_replicas_upperbound_plus1(self, problem_list):

        """Pass out of bound num_replica value to create solver and
        validate the failure of experiment along with the correct error
        message
        """

        solver_params = {"num_replicas": 10001}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_NUM_REPLICAS
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_num_sweeps_per_run_upperbound_plus1(self, problem_list):

        """Pass out of bound num_sweeps_per_run value to create solver and
        validate the failure of experiment along with the correct error message
        """

        solver_params = {"num_sweeps_per_run": 10000001}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_NUM_SWEEPS_PER_RUN
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_elite_threshold_upperbound_plus(self, problem_list):

        """Pass out of bound elite_threshold value to create solver and 
        validate the failure of experiment along with the correct error 
        message
        """

        solver_params = {"elite_threshold": 1.01}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_ELITE_THRESHOLD
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_negative_frac_icm_thermal_layers(self, problem_list):

        """Pass negative frac_icm_thermal_layers value to create solver and
        validate the failure of experiment along with the correct error message
        """

        solver_params = {"frac_icm_thermal_layers": "-1"}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_FRAC_ICM_THERMAL_LAYERS
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_invalid_combination_temperature_bounds_with_auto_temps(
        self, problem_list
    ):

        """Pass invalid combination of solver params and  validate the failure of 
        experiment along with the correct error message
        """

        solver_params = {
            "auto_set_temperatures": "true",
            "high_temp": 2,
            "low_temp": 0.2,
        }
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_HIGH_TEMP_WITH_AUTO_SET_TEMPERATURES_TRUE
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_negative_seed(self, problem_list):

        """Pass negative seed value to create solver and  validate the failure 
        of experiment along with the correct error message
        """

        solver_params = {"seed": -1}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_SEED
            in result[0]["error_data"]["message"]
        )

    def test_pticm_error_num_elite_temps_lowerbound_minus1(self, problem_list):

        """Pass out of bound num_elite_temps value to create solver and validate 
        the failure of experiment along with the correct error message
        """

        solver_params = {"num_elite_temps": 0}
        solver = SolverFactory.generate_pticm_solvers([solver_params])
        # solve
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
            pticm_solver_error.ERROR_PTICM_NUM_ELITE_TEMPS
            in result[0]["error_data"]["message"]
        )
