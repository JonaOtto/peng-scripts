import json
import os
import subprocess

from SLURM.exceptions import CommandExecutionException

default_out_dir = "issm-output/RESULTS"
git_dir = "issm-output"


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
        self.suffix = 0
        self.home_dir = os.path.expanduser('~')
        self.out_file = f"{self.home_dir}/{default_out_dir}/{self.experiment_name}.json"

    def prepare(self):
        while os.path.isdir(f"{self.home_dir}/{default_out_dir}/{self.experiment_name}-{self.suffix}"):
            print(f"{self.home_dir}/{default_out_dir}/{self.experiment_name}-{self.suffix} is present")
            self.suffix = self.suffix + 1
        print(f"Using: {self.home_dir}/{default_out_dir}/{self.experiment_name}-{self.suffix}")
        res = subprocess.run(["mkdir", "-p", f"{self.home_dir}/{default_out_dir}/{self.experiment_name}-{self.suffix}"])
        if not res.returncode == 0:
            raise CommandExecutionException(f"mkdir -p {self.home_dir}/{default_out_dir}/{self.experiment_name}-{self.suffix}")
        self.out_file = f"{self.home_dir}/{default_out_dir}/{self.experiment_name}-{self.suffix}/{self.experiment_name}.json"

    def export(self):
        """
        Run the exporter.
        """
        with open(self.out_file, "w") as f:
            f.write(json.dumps(self.results, indent=4))

    def commit_and_push(self):
        """
        commits and pushes the results in the issm-output git.
        """
        print("Git status:")
        subprocess.run(["git" "status"])
        print(f"Committing: Updated results for experiment {self.experiment_name}")
        os.chdir(f"{self.home_dir}/{git_dir}")
        subprocess.run(["git" "add", "-A"])
        subprocess.run(["git" "commit", "-m", f"\"Updated results for experiment {self.experiment_name}\""])
        print("Pushing")
        subprocess.run(["git", "push"])
        print("Finished! Updated the output git.")
        print("Git status:")
        subprocess.run(["git" "status"])
