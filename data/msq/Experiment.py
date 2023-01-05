from datetime import datetime, timezone
import uuid
import json
# import azure_config
import logging.config

from ..logger.logger_config import LOGGING_CONFIG

# Set up logger
# logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


class Experiment:
    """An experiment is a set of solver-problem combinations to be solved as a batch"""

    def __init__(self, solver_list, problem_list, num_iterations=1, experiment_id=None):
        if experiment_id is None:
            experiment_id = str(uuid.uuid4())
        self.date = datetime.now().replace(tzinfo=timezone.utc)
        self.experiment_id = experiment_id
        self.num_iterations = num_iterations
        self.solver_list = solver_list
        self.problem_list = problem_list
        self.job_id_list = []
        self.experiment = []
        self.workspace = azure_config.WORKSPACE

    def __submit_one_problem_num_iterations_times(
        self, solver, problem, submit_problem_object_list
    ):
        """Submit one problem to a solver num_iterations times

        Returns:
            submit_problem_object_list: contains an updated list of submit_problem_object
        """
        logger.debug("()")
        submit_iteration_list = []
        # Iterate over num_iterations
        for i in range(self.num_iterations):
            # Submit job
            try:
                job = solver.submit(problem)
                self.job_id_list.append(job.id)
                submit_iteration_list.append(job.id)
            except Exception as e:
                err_msg = f"Failed to submit {problem} to {type(solver)} at iteration {i}, error: {e}"
                logger.error(err_msg)
        submit_problem_object = {
            "input_data_uri": problem.uploaded_blob_uri,
            "num_iterations": self.num_iterations,
            "iterations": submit_iteration_list,
        }
        submit_problem_object_list.append(submit_problem_object)
        logger.debug("- Return")
        return submit_problem_object_list, job

    def __submit_problems_in_problem_list(self, solver, submit_solver_object_list):
        """Submit problems in the problem list to a solver

        Returns:
            submit_solver_object_list: contains an updated list of submit_solver_object
        """
        logger.debug("()")
        submit_problem_object_list = []
        # Iterate over list of problems
        for problem in self.problem_list:
            try:
                (
                    submit_problem_object_list,
                    job,
                ) = self.__submit_one_problem_num_iterations_times(
                    solver, problem, submit_problem_object_list
                )
            except Exception as e:
                err_msg = f"Failed to submit problem {problem}, error: {e}"
                logger.error(err_msg)

        solver_type = type(solver)
        solver_name = solver_type.__module__ + "." + solver_type.__name__
        submit_solver_object = {
            "solver": solver_name,
            "input_params": job.details.input_params,
            "problems": submit_problem_object_list,
        }
        submit_solver_object_list.append(submit_solver_object)
        logger.debug("- Return")

        return submit_solver_object_list

    def submit(self):
        """Submit all problems to be solved on all solvers"""
        # Construct a list for storing submit_solver_object
        logger.debug("()")
        submit_solver_object_list = []

        # Iterate over list of solvers
        for solver in self.solver_list:
            try:
                submit_solver_object_list = self.__submit_problems_in_problem_list(
                    solver, submit_solver_object_list
                )
            except Exception as e:
                err_msg = f"Failed to submit problems to {type(solver)} , error: {e}"
                logger.error(err_msg)
        self.experiment = submit_solver_object_list
        logger.debug("- Return")

    def has_completed(self) -> bool:
        """Return a boolean value indicating whether the experiment has finished"""
        logger.debug("()")
        for job_id in self.job_id_list:
            try:
                job = self.workspace.get_job(job_id)
                if not job.has_completed():
                    return False
            except Exception as e:
                err_msg = f"Failed to get the job details, job_id: {job_id}, error: {e}"
                logger.error(err_msg)
        logger.debug("- Return")
        return True

    def wait_until_completed(self):
        """Wait until the experiment has finished"""
        logger.debug("()")
        for job_id in self.job_id_list:
            try:
                job = self.workspace.get_job(job_id)
                job.wait_until_completed()
            except Exception as e:
                err_msg = f"Failed to get the job details, job_id: {job_id}, error: {e}"
                logger.error(err_msg)
        logger.debug("- Return")

    def get_experiment_details_as_string(self) -> str:
        """Get the details for the experiment as a string (CSV)"""
        logger.debug("()")
        results = "\ncreation_time, id, target, status, total_time, queue_time, execution_time, cost, error_message"
        for job_id in self.job_id_list:
            try:
                job = self.workspace.get_job(job_id)
                results += self.get_job_details_as_string(job)
            except Exception as e:
                err_msg = f"Failed to get the job details, job_id: {job_id}, error: {e}"
                logger.error(err_msg)
        logger.debug("- Return")
        return results

    def get_job_details_as_string(self, job) -> str:
        """Get the details for a job as a string (CSV)"""
        logger.debug("()")
        id = job.id
        target = job.details.target
        status = job.details.status
        creation_time = job.details.creation_time
        begin_execution_time = job.details.begin_execution_time
        end_execution_time = job.details.end_execution_time
        cancellation_time = job.details.cancellation_time

        execution_time = "null"
        queue_time = "null"
        total_time = "null"
        cost = "null"
        error_message = "null"

        if status == "Succeeded":
            execution_time = end_execution_time - begin_execution_time
            execution_time = execution_time.total_seconds()
            queue_time = begin_execution_time - creation_time
            queue_time = queue_time.total_seconds()
            total_time = end_execution_time - creation_time
            total_time = total_time.total_seconds()
            results = job.get_results()
            cost = results["solutions"][0]["cost"]
        elif status == "Failed":
            if begin_execution_time is not None and end_execution_time is not None:
                execution_time = end_execution_time - begin_execution_time
                execution_time = execution_time.total_seconds()
                queue_time = begin_execution_time - creation_time
                queue_time = queue_time.total_seconds()
                total_time = end_execution_time - creation_time
                total_time = total_time.total_seconds()

            error_data = str(job.details.error_data).replace("'", '"')
            error_data = json.loads(error_data)
            error_message = error_data["message"]

            error_message = error_message.replace("\n", "")
            error_message = error_message.strip()
            error_message = f'"{error_message}"'

        elif status == "Cancelled":
            if begin_execution_time is not None:
                execution_time = cancellation_time - begin_execution_time
                execution_time = execution_time.total_seconds()
                queue_time = begin_execution_time - creation_time
                queue_time = queue_time.total_seconds()

            total_time = cancellation_time - creation_time
            total_time = total_time.total_seconds()
        elif status == "Executing":
            queue_time = begin_execution_time - creation_time
            queue_time = queue_time.total_seconds()
        elif status == "Waiting":
            pass
        logger.debug("- Return")

        return f"\n{creation_time}, {id}, {target}, {status}, {total_time}, {queue_time}, {execution_time}, {cost}, {error_message}"

    def __get_job_details_in_submit_iteration_list(
        self,
        experiment_details_list,
        submit_iteration_list,
        solver,
        problem,
        experiment,
        iteration_index,
    ):
        """Get the details for jobs inside submit_iteration_list (a list of job_ids)"""
        logger.debug("()")
        for job_id in submit_iteration_list:
            try:
                job = self.workspace.get_job(job_id)
                experiment_details_list.append(
                    self.get_job_details(job, solver, problem, experiment)
                )
                iteration_index += 1
                experiment = experiment.copy()
                experiment["iteration"] = iteration_index
            except Exception as e:
                err_msg = (
                    f"Failed getting the job details, job_id: {job_id}, error: {e}"
                )
                logger.error(err_msg)
        logger.debug("- Return")

    def __get_problem_objects_details(
        self,
        problems,
        solver,
        solver_list_length,
        solver_list_index,
        problem_list_length,
        problem_list_index,
        experiment_details_list,
    ):
        """Get the details from problem objects"""
        logger.debug("()")
        for problem_object in problems:
            try:
                iteration_index = 0
                problem = {
                    "qubo_size": "qubo_size",
                    "qubo_density": "qubo_density",
                }
                experiment = {
                    "experiment_id": self.experiment_id,
                    "date": str(self.date),
                    "num_iterations": problem_object["num_iterations"],
                    "iteration": iteration_index,
                    "solver_list_length": solver_list_length,
                    "solver_list_index": solver_list_index,
                    "problem_list_length": problem_list_length,
                    "problem_list_index": problem_list_index,
                }
                self.__get_job_details_in_submit_iteration_list(
                    experiment_details_list,
                    problem_object["iterations"],
                    solver,
                    problem,
                    experiment,
                    iteration_index,
                )
                problem_list_index += 1
            except Exception as e:
                err_msg = f"Failed iterating the problem list, error: {e}"
                logger.error(err_msg)
        logger.debug("- Return")

    def __get_solver_objects_details(
        self,
        solver_list_length,
        solver_list_index,
        experiment_details_list,
    ):
        """Get the details from solver objects"""
        logger.debug("()")
        for solver_object in self.experiment:
            problem_list_index = 0
            problems = solver_object["problems"]
            problem_list_length = len(problems)
            if problem_list_length != 0:
                try:
                    solver = {
                        "class_name": solver_object["solver"],
                        "input_params": solver_object["input_params"],
                    }
                    self.__get_problem_objects_details(
                        problems,
                        solver,
                        solver_list_length,
                        solver_list_index,
                        problem_list_length,
                        problem_list_index,
                        experiment_details_list,
                    )
                    solver_list_index += 1
                except Exception as e:
                    err_msg = f"Failed iterating the solver list, error: {e}"
                    logger.error(err_msg)
            else:
                err_msg = "Empty problem list"
                logger.error(err_msg)
                raise Exception(err_msg)
        logger.debug("- Return")

    def get_experiment_details(self):
        """
        Get the details for the experiment

        Returns:
            experiment_details_list: contains details object created by __get_solver_objects_details()
        """
        logger.debug("()")
        experiment_details_list = []
        solver_list_index = 0
        solver_list_length = len(self.experiment)
        if solver_list_length != 0:
            self.__get_solver_objects_details(
                solver_list_length,
                solver_list_index,
                experiment_details_list,
            )
            return experiment_details_list
        else:
            err_msg = "Empty problem list"
            logger.error(err_msg)
            raise Exception(err_msg)
        logger.debug("- Return")

    def get_job_details(self, job, solver, problem, experiment):
        """
        Get the details for a job

        Returns:
            JSON Schema of returned dictionary, when converted to JSON:
            {
                "type" : "object",
                "properties" : {
                    "id" : {"type" : "string"},
                    "target" : {"type" : "string"},
                    "status" : {"type" : "string", "enum": ["Waiting", "Executing", "Succeeded", "Failed", "Cancelled"]},
                    "creation_time" : {"type" : "string"},
                    "execution_time" : {"type" : "string"},
                    "queue_time" : {"type" : "string"},
                    "total_time" : {"type" : "string"},
                    "cost" : {"type" : "string"},
                    "parameters" : {"type" : "object"},
                    "input_data_uri" : {"type" : "string"},
                    "output_data_uri" : {"type" : "string"},
                    "problem" : {"$ref": "#/definitions/problem_object"},
                    "solver" : {"$ref": "#/definitions/solver_object"},
                    "experiment" : {"$ref": "#/definitions/experiment_object"}
                },
                "required" : ["id", "target", "status", "creation_time", "input_data_uri", "output_data_uri", "problem", "solver", "experiment"],
                "additionalProperties": False
                "definitions": {
                    "problem_object": {
                        "type" : "object",
                        "properties" : {
                            "qubo_size": {"type" : "string"},
                            "qubo_density": {"type" : "string"}
                        },
                        "required" : ["qubo_size", "qubo_density"],
                        "additionalProperties": False
                    },
                    "solver_object": {
                        "type" : "object",
                        "properties" : {
                            "class_name": {"type" : "string"},
                            "input_params": {"type" : "object"}
                        },
                        "required" : ["class_name", "input_params"],
                        "additionalProperties": False
                    }
                    "experiment_object": {
                        "type" : "object",
                        "properties" : {
                            "experiment_id" : {"type" : "string"},
                            "date" : {"type" : "string"},
                            "num_iterations" : {"type" : "number"},
                            "iteration" : {"type" : "number"},
                            "solver_list_length" : {"type" : "number"},
                            "solver_list_index" : {"type" : "number"},
                            "problem_list_length" : {"type" : "number"},
                            "problem_list_index" : {"type" : "number"}
                        },
                        "required" : ["experiment_id", "date", "num_iterations", "iteration", "solver_list_length", "solver_list_index", "problem_list_length", "problem_list_index"],
                        "additionalProperties": False
                    }
                }
            }
        """
        logger.debug("()")
        creation_time = job.details.creation_time
        begin_execution_time = job.details.begin_execution_time
        end_execution_time = job.details.end_execution_time
        cancellation_time = job.details.cancellation_time

        try:
            input_data_uri = job.details.input_data_uri.split("?")[0]
            output_data_uri = job.details.output_data_uri
        except Exception as e:
            err_msg = (
                f"Failed getting the input/output uri from a job: {job.id}, error : {e}"
            )
            logger.error(err_msg)
            input_data_uri = None
            output_data_uri = None

        result_object = {
            "id": job.id,
            "target": job.details.target,
            "status": job.details.status,
            "creation_time": str(creation_time),
            "input_data_uri": input_data_uri,
            "output_data_uri": output_data_uri,
            "problem": problem,
            "solver": solver,
            "experiment": experiment,
        }

        if job.details.status == "Succeeded":
            execution_time = end_execution_time - begin_execution_time
            execution_time = execution_time.total_seconds()
            queue_time = begin_execution_time - creation_time
            queue_time = queue_time.total_seconds()
            total_time = end_execution_time - creation_time
            total_time = total_time.total_seconds()

            try:
                output_data = job.get_results()

                if "input_params" in output_data:
                    # obtain parameters from 1qbit solvers
                    parameters = output_data["input_params"]
                elif "parameters" in output_data:
                    # obtain parameters from microsoft solvers
                    parameters = output_data["parameters"]
                else:
                    parameters = None

                cost = output_data["solutions"][0]["cost"]
            except RuntimeError as e:
                err_msg = "Failed getting the results from a job: {job.id}, error : {e}"
                logger.error(err_msg)
                parameters = None
                cost = None
            except KeyError as e:
                err_msg = "Failed getting the cost from a job: {job.id}, error : {e}"
                logger.error(err_msg)
                cost = None

            result_object.update(
                {
                    "execution_time": str(execution_time),
                    "queue_time": str(queue_time),
                    "total_time": str(total_time),
                    "cost": cost,
                    "parameters": parameters,
                }
            )

        elif job.details.status == "Failed":
            if begin_execution_time is not None and end_execution_time is not None:
                execution_time = end_execution_time - begin_execution_time
                execution_time = execution_time.total_seconds()
                queue_time = begin_execution_time - creation_time
                queue_time = queue_time.total_seconds()
                total_time = end_execution_time - creation_time
                total_time = total_time.total_seconds()

                result_object.update(
                    {
                        "execution_time": str(execution_time),
                        "queue_time": str(queue_time),
                        "total_time": str(total_time),
                    }
                )

            error_data = str(job.details.error_data).replace("'", '"')
            error_data = json.loads(error_data)

            result_object.update(
                {
                    "error_data": error_data,
                }
            )

        elif job.details.status == "Cancelled":
            if begin_execution_time is not None:
                execution_time = cancellation_time - begin_execution_time
                execution_time = execution_time.total_seconds()
                queue_time = begin_execution_time - creation_time
                queue_time = queue_time.total_seconds()

                result_object.update(
                    {
                        "execution_time": str(execution_time),
                        "queue_time": str(queue_time),
                    }
                )
            total_time = cancellation_time - creation_time
            total_time = total_time.total_seconds()

            result_object.update(
                {
                    "total_time": str(total_time),
                }
            )

        elif job.details.status == "Executing":
            queue_time = begin_execution_time - creation_time

            result_object.update(
                {
                    "queue_time": str(queue_time),
                }
            )

        elif job.details.status == "Waiting":
            pass

        logger.debug("- Return")
        return result_object
