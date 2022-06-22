from typing import List

from Runs.run import BaseRun
from Analyzer.analyzer import ResultAnalyzer
from Management.exporter import Exporter


class Experiment:
    """
    This is sort of a container for Runs. You can put a variable amount of runs in it and an analyzer.
    This will run all the jobs, and after this run the analyzer on the results.
    Put jobs in a Swarm you want to compare with each other.
    This class opens the same interface as a Run, so call "do_run()" to start it.
    """
    def __init__(self, name, runs=None):
        """
        Constructor.
        """
        if runs is None:
            runs = []
        self.name = name
        self.runs = runs
        self.__run_res_tuples = []

    def add_run(self, run: BaseRun):
        self.runs.append(run)

    def do_run(self):
        """
        Start the experiment.
        """
        print(f"Starting experiment: {self.name}")
        for run in self.runs:
            print(f"Starting run {run.jobname_skeleton} from experiment {self.name}")
            try:
                out_dir, builder_config, job_config = run.do_run()
                self.__run_res_tuples.append((out_dir, builder_config, job_config))
            except Exception:
                print("AAAAAAAAAAAAAAAHHHHHHHHHHHHHHHHHHHHHHRRRRRRRRRRRRRRGGGGGGGGGGGGGGG")
        print(f"Starting analyzing on experiment: {self.name}")

        """ 
        Configs are compared on equality of their options while analyzing. 
        You may need to have your own definition of what "equal" is in the context of your experiment.
        You may inject a function that returns true or false and takes two ExperimentConfigs as arguments here,
        with the config_equal_f parameter. This way you can overwrite the default comparison method used otherwise,
        which can be found in Analyzer/analyzer.py:ExperimentConfig::is_comparable(self, other)
        """
        analyzer = ResultAnalyzer(self.__run_res_tuples, config_equal_f=None)
        results = analyzer.analyze()

        print(f"Starting exporting on experiment: {self.name}")
        exporter = Exporter(results, self.name)
        exporter.prepare()
        exporter.export()
        exporter.commit_and_push()
        print(f"Finished experiment: {self.name}")
