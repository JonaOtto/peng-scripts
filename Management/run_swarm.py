from typing import List

from Runs.run import BaseRun
from Analyzer.analyzer import ResultAnalyzer


class RunSwarm:
    """
    This is sort of a container for Runs. You can put a variable amount of runs in it and an analyzer.
    This will run all the jobs, and after this run the analyzer on the results.
    Put jobs in a Swarm you want to compare with each other.
    This class opens the same interface as a Run, so call "do_run()" to start it.
    """
    def __init__(self, runs: List[BaseRun]):
        """
        Constructor.
        """
        self.runs = runs
        self.__run_res_tuples = []

    def do_run(self):
        """
        Start the run swarm.
        """
        for run in self.runs:
            out_dir, builder_config, job_config = run.do_run()
            self.__run_res_tuples.append((out_dir, builder_config, job_config))
        analyzer = ResultAnalyzer(self.__run_res_tuples)
        analyzer.analyze()
