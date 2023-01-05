from unittest import TestCase
from msq.Experiment import Experiment
from unittest.mock import patch, MagicMock

from azure.quantum.optimization import Problem, ProblemType, Term
from azure.quantum.target.oneqbit import TabuSearch, PticmSolver, PathRelinkingSolver
import azure_config


class ExperimentTest(TestCase):
    @classmethod
    def setUpClass(self):
        # Create a list of problems
        self.problem_list = []
        for n in range(1):
            # Construct a problem
            problem = Problem(name=f"Problem-{n}", problem_type=ProblemType.pubo)
            terms = [
                Term(c=-9, indices=[0]),
                Term(c=-3, indices=[1, 0]),
                Term(c=5, indices=[2, 0]),
            ]
            problem.add_terms(terms=terms)
            self.problem_list.append(problem)

        # Create a list of solvers
        self.solver_list = [
            TabuSearch(azure_config.WORKSPACE),
            PticmSolver(azure_config.WORKSPACE),
            PathRelinkingSolver(azure_config.WORKSPACE),
        ]

    def setUp(self):
        self.experiment = Experiment(self.solver_list, self.problem_list)

    @patch.object(Experiment, "_Experiment__submit_problems_in_problem_list")
    def test_submit_called(self, mock_func):

        try:
            self.experiment.submit()
        except Exception as e:
            self.fail(f"submit() raised Exception {e}")
        mock_func.assert_called()

    @patch.object(Experiment, "_Experiment__submit_problems_in_problem_list")
    def test_submit_exception(self, mock_func):

        mock_func.side_effect = Exception()

        try:
            self.experiment.submit()
        except Exception as e:
            self.fail(f"submit() raised Exception {e}")
        mock_func.assert_called()

    @patch.object(Experiment, "_Experiment__submit_problems_in_problem_list")
    def test_submit_return_value(self, mock_func):

        mock_func.return_value = [1]
        self.experiment.submit()
        self.assertEqual(self.experiment.experiment, [1])

    def test_has_completed(self):
        # Mock internal functions
        mock_job = MagicMock()
        mock_workspace = MagicMock()
        self.experiment.job_id_list = [mock_job]
        self.experiment.workspace = mock_workspace

        try:
            self.experiment.has_completed()
        except Exception as e:
            self.fail(f"has_completed() raised Exception {e}")

        # Check function was called
        mock_workspace.get_job.assert_called()

    def test_wait_until_completed(self):
        # Mock internal functions
        mock_job = MagicMock()
        mock_workspace = MagicMock()
        self.experiment.job_id_list = [mock_job]
        self.experiment.workspace = mock_workspace

        try:
            test = self.experiment.wait_until_completed()
        except Exception as e:
            self.fail(f"wait_until_completed() raised Exception {e}")

        # Check function was called
        mock_workspace.get_job.assert_called()

    @patch.object(Experiment, "get_job_details_as_string")
    def test_get_experiment_details_as_string(self, mock_func):
        # Mock internal functions
        mock_func.return_value = " test"
        mock_job = MagicMock()
        mock_workspace = MagicMock()
        self.experiment.job_id_list = [mock_job]
        self.experiment.workspace = mock_workspace

        expected_string = "\ncreation_time, id, target, status, total_time, queue_time, execution_time, cost, error_message test"

        try:
            results = self.experiment.get_experiment_details_as_string()
        except Exception as e:
            self.fail(f"get_experiment_details_as_string() raised Exception {e}")

        self.assertEqual(results, expected_string)

    def test_get_experiment_details_empty_list(self):
        self.experiment.experiment = []
        expected_error_msg = "Empty problem list"

        with self.assertRaises(Exception) as test:
            self.experiment.get_experiment_details()

        self.assertEqual(expected_error_msg, str(test.exception))

    @patch.object(Experiment, "_Experiment__get_solver_objects_details")
    def test_get_experiment_details_mock(self, mock_func):
        self.experiment.experiment = [1, 1]
        # Return an empty list
        details = self.experiment.get_experiment_details()

        self.assertEqual(details, [])

    def test_get_job_details_as_string_mock(self):
        mock_job = MagicMock()

        self.assertTrue(self.experiment.get_job_details_as_string(mock_job))

    def test_get_job_details_as_string_mock_waiting(self):
        mock_job = MagicMock()
        mock_job.status = "Waiting"

        self.assertTrue(self.experiment.get_job_details_as_string(mock_job))

    def test_get_job_details_as_string_mock_succeeded(self):
        mock_job = MagicMock()
        mock_job.details.status = "Succeeded"

        self.assertTrue(self.experiment.get_job_details_as_string(mock_job))

        mock_job.get_results.assert_called()

    def test_get_job_details_as_string_mock_failed(self):
        mock_job = MagicMock()
        mock_job.details.status = "Failed"
        mock_job.details.error_data = MagicMock()

        with self.assertRaises(Exception) as test:
            self.experiment.get_job_details_as_string(mock_job)

    def test_get_job_details_as_string_mock_cancelled(self):
        mock_job = MagicMock()
        mock_job.details.status = "Cancelled"

        self.assertTrue(self.experiment.get_job_details_as_string(mock_job))

    def test_get_job_details_as_string_mock_executing(self):
        mock_job = MagicMock()
        mock_job.details.status = "Executing"

        self.assertTrue(self.experiment.get_job_details_as_string(mock_job))

    def test_get_job_details_mock(self):
        mock_job = MagicMock()
        mock_solver = MagicMock()
        mock_problem = MagicMock()
        mock_experiment = MagicMock()

        self.assertTrue(
            self.experiment.get_job_details(
                mock_job, mock_solver, mock_problem, mock_experiment
            )
        )

    def test_get_job_details_mock_succeeded(self):
        mock_job = MagicMock()
        mock_solver = MagicMock()
        mock_problem = MagicMock()
        mock_experiment = MagicMock()

        mock_job.details.status = "Succeeded"

        self.assertTrue(
            self.experiment.get_job_details(
                mock_job, mock_solver, mock_problem, mock_experiment
            )
        )

        mock_job.get_results.assert_called()

    def test_get_job_details_mock_failed(self):
        mock_job = MagicMock()
        mock_solver = MagicMock()
        mock_problem = MagicMock()
        mock_experiment = MagicMock()

        mock_job.details.status = "Failed"

        with self.assertRaises(Exception) as test:
            self.experiment.get_job_details(
                mock_job, mock_solver, mock_problem, mock_experiment
            )

    def test_get_job_details_mock_cancelled(self):
        mock_job = MagicMock()
        mock_solver = MagicMock()
        mock_problem = MagicMock()
        mock_experiment = MagicMock()

        mock_job.details.status = "Cancelled"

        self.assertTrue(
            self.experiment.get_job_details(
                mock_job, mock_solver, mock_problem, mock_experiment
            )
        )

    def test_get_job_details_mock_executing(self):
        mock_job = MagicMock()
        mock_solver = MagicMock()
        mock_problem = MagicMock()
        mock_experiment = MagicMock()

        mock_job.details.status = "Executing"

        self.assertTrue(
            self.experiment.get_job_details(
                mock_job, mock_solver, mock_problem, mock_experiment
            )
        )

    def test_get_job_details_mock_waiting(self):
        mock_job = MagicMock()
        mock_solver = MagicMock()
        mock_problem = MagicMock()
        mock_experiment = MagicMock()

        mock_job.details.status = "Waiting"

        self.assertTrue(
            self.experiment.get_job_details(
                mock_job, mock_solver, mock_problem, mock_experiment
            )
        )
