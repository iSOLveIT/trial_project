import json
import os
import shutil
from unittest import TestCase
from msq.VisualizationGenerator import VisualizationGenerator

from unittest.mock import patch


class VisualizationGeneratorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.visualization_generator = VisualizationGenerator()
        cls.fig = "mock_fig"
        cls.default_file_name = "viz_num_solves"
        cls.data = [
            {"target": "1qbit.tabu", "solver_list_index": 0, "solve_time": 2.141324},
            {"target": "1qbit.tabu", "solver_list_index": 0, "solve_time": 2.717909},
            {"target": "1qbit.tabu", "solver_list_index": 0, "solve_time": 3.263594},
            {"target": "1qbit.pticm", "solver_list_index": 1, "solve_time": 3.96576},
            {"target": "1qbit.pticm", "solver_list_index": 1, "solve_time": 4.467632},
            {"target": "1qbit.pticm", "solver_list_index": 1, "solve_time": 4.819963},
            {
                "target": "1qbit.pathrelinking",
                "solver_list_index": 2,
                "solve_time": 5.051341,
            },
            {
                "target": "1qbit.pathrelinking",
                "solver_list_index": 2,
                "solve_time": 5.616555,
            },
            {
                "target": "1qbit.pathrelinking",
                "solver_list_index": 2,
                "solve_time": 5.800055,
            },
            {"target": "1qbit.tabu", "solver_list_index": 3, "solve_time": 6.967958},
            {"target": "1qbit.tabu", "solver_list_index": 3, "solve_time": 7.434249},
            {"target": "1qbit.tabu", "solver_list_index": 3, "solve_time": 7.953032},
        ]

    def test_generate_time_to_solution_bar_graph_success(self):
        try:
            fig = self.visualization_generator.generate_time_to_solution_bar_graph(
                self.data
            )
        except Exception as e:
            self.fail(
                f"generate_time_to_solution_bar_graph raised exception unexpectedly: {e}"
            )

    def test_generate_time_to_solution_bar_graph_invaid_data_type(self):
        with self.assertRaises(Exception) as context:
            self.visualization_generator.generate_time_to_solution_bar_graph([])
        self.assertTrue(
            "None of [Index(['target', 'solver_list_index', 'solve_time'], dtype='object')] are in the [columns]"
            in str(context.exception)
        )

    def test_generate_time_to_solution_bar_graph_invaid_data(self):

        invalid_data = [
            {
                "invalid_field": "1qbit.tabu",
                "solver_list_index": 0,
                "solve_time": 2.141324,
            },
            {
                "invalid_field": "1qbit.pticm",
                "solver_list_index": 1,
                "solve_time": 4.819963,
            },
        ]
        with self.assertRaises(Exception) as context:
            self.visualization_generator.generate_time_to_solution_bar_graph(
                invalid_data
            )

        self.assertTrue("['target'] not in index" in str(context.exception))

    @patch("msq.VisualizationGenerator.plotly")
    def test_save_graph_by_format_set_output_format_success(
        self, mock_plotly_offline_plot
    ):
        try:
            self.visualization_generator.save_graph_by_format(
                self.fig, self.default_file_name, "html"
            )
        except Exception as e:
            self.fail(f"save_graph_by_format raised exception unexpectedly: {e}")

    def test_save_graph_by_format_set_output_format_error(self):
        with self.assertRaises(Exception) as context:
            self.visualization_generator.save_graph_by_format(
                self.fig, self.default_file_name, "csv"
            )

        self.assertEqual(
            "output format must be either png or html", str(context.exception)
        )
