import json
import os

from Analyzer.analyzer import ExperimentConfig


default_out_dir = "RESULTS"


class Exporter:
    """
    Exports the results to .json
    """
    def __init__(self, results, experiment_name):
        """
        Constructor.
        """
        self.results = results
        self.experiment_name = experiment_name
        self.out_file = f"{os.path.expanduser('~')}/{default_out_dir}/{self.experiment_name}.json"

    def export(self):
        """
        Run the exporter.
        """
        with open(self.out_file, "w") as f:
            f.write(json.dumps(self.results, indent=4))
