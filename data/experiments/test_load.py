import unittest
from datetime import datetime
import warnings
from azure.quantum.target.oneqbit import TabuSearch, PticmSolver, PathRelinkingSolver
from msq.Experiment import Experiment
from msq.ProblemLibrary import ProblemLibrary
import azure_config


class LoadTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        warnings.simplefilter("ignore", ResourceWarning)

        # Create a list of solvers
        self.solver_list = [
            TabuSearch(azure_config.WORKSPACE),
            PticmSolver(azure_config.WORKSPACE),
            PathRelinkingSolver(azure_config.WORKSPACE),
        ]

    def setUp(self):
        print("\n[%s] Test %s Started" % (str(datetime.now()), self._testMethodName))

    def tearDown(self):
        print("\n[%s] Test %s Finished" % (str(datetime.now()), self._testMethodName))

    def solve(self, problem_list, num_iterations):
        """Solve the list of problems, with each solver, multiple times (depending on num_iterations)."""
        num_solvers = len(LoadTestCase.solver_list)
        num_problems = len(problem_list)
        num_jobs = num_solvers * num_problems * num_iterations

        # Create and run an experiment
        print("[%s] Submit %s job(s)" % (str(datetime.now()), str(num_jobs)))
        experiment = Experiment(
            self.solver_list, problem_list, num_iterations=num_iterations
        )
        experiment.submit()
        print("[%s] Wait until completed" % (str(datetime.now())))
        experiment.wait_until_completed()

    def test_load_solve_0064_x0960(self):
        """Concurrently solve the same random QUBO of size=64, 320 times with each solver (960 jobs)."""
        blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(size=64)
        problem_list = [
            ProblemLibrary.get_problem_by_blob_name(blob_name),
        ]
        self.solve(problem_list, num_iterations=320)

    def test_load_solve_0128_x0480(self):
        """Concurrently solve the same random QUBO of size=128, 160 times with each solver (480 jobs)."""
        blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(
            size=128
        )
        problem_list = [
            ProblemLibrary.get_problem_by_blob_name(blob_name),
        ]
        self.solve(problem_list, num_iterations=160)

    def test_load_solve_0256_x0240(self):
        """Concurrently solve the same random QUBO of size=256, 80 times with each solver (240 jobs)."""
        blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(
            size=256
        )
        problem_list = [
            ProblemLibrary.get_problem_by_blob_name(blob_name),
        ]
        self.solve(problem_list, num_iterations=80)

    def test_load_solve_0512_x0120(self):
        """Concurrently solve the same random QUBO of size=512, 40 times with each solver (120 jobs)."""
        blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(
            size=512
        )
        problem_list = [
            ProblemLibrary.get_problem_by_blob_name(blob_name),
        ]
        self.solve(problem_list, num_iterations=40)

    def test_load_solve_1024_x0060(self):
        """Concurrently solve the same random QUBO of size=1024, 20 times with each solver (60 jobs)."""
        blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(
            size=1024
        )
        problem_list = [
            ProblemLibrary.get_problem_by_blob_name(blob_name),
        ]
        self.solve(problem_list, num_iterations=20)

    def test_load_solve_2048_x0030(self):
        """Concurrently solve the same random QUBO of size=2048, 10 times with each solver (30 jobs)."""
        blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(
            size=2048
        )
        problem_list = [
            ProblemLibrary.get_problem_by_blob_name(blob_name),
        ]
        self.solve(problem_list, num_iterations=10)

    '''
    def test_load_solve_4096_x0015(self):
        """Concurrently solve the same random QUBO of size=4096, 5 times with each solver (15 jobs)."""
        blob_name, blob_uri = ProblemLibrary.generate_random_qubo_if_not_exists(size=4096)
        problem_list = [
            ProblemLibrary.get_problem_by_blob_name(blob_name),
        ]
        self.solve(problem_list, num_iterations=5)
    '''


if __name__ == "__main__":
    unittest.main()
