from azure.quantum.optimization import Problem, ProblemType, Term
from azure.quantum.target.oneqbit import TabuSearch, PticmSolver, PathRelinkingSolver
from msq.Experiment import Experiment
import azure_config


# Create a list of problems
problem_list = []
for n in range(10):
    # Construct a problem
    problem = Problem(name=f"Problem-{n}", problem_type=ProblemType.ising)

    terms = [
        Term(c=-9, indices=[0]),
        Term(c=-3, indices=[1, 0]),
        Term(c=5, indices=[2, 0]),
    ]
    problem.add_terms(terms=terms)
    problem_list.append(problem)

# Create a list of solvers
solver_list = [
    TabuSearch(azure_config.WORKSPACE),
    PticmSolver(azure_config.WORKSPACE),
    PathRelinkingSolver(azure_config.WORKSPACE),
]

# Create and run an experiment
experiment = Experiment(solver_list, problem_list)
experiment.submit()
experiment.wait_until_completed()
print(experiment.get_experiment_details_as_string())
