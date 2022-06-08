from typing import List

from Runs.run import BaseRun
from Analyzer.analyzer import ResultAnalyzer
from Management.exporter import Exporter


class RunSwarm:
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
        Start the run swarm.
        """
        print(f"Starting experiment: {self.name}")
        for run in self.runs:
            print(f"Starting run {run.jobname_skeleton} from run swarm {self.name}")
            out_dir, builder_config, job_config = run.do_run()
            # out_dir, builder_config, job_config = "/home/kurse/kurs00054/jo83xafu/OUT/ISSM-MINIAPP-THERMAL_G1600_GCC_MPI96_GPROF.28918782", {'app': 'ISSM-MINIAPP-THERMAL', 'source_path': 'issm-miniapp', 'compiler': 'GCC', 'gcc_version': '10.2', 'llvm_version': '10.0.0', 'c_compiler_flags': "'-O2 -pg'", 'fortran_compiler_flags': '-O2', 'cxx_compiler_flags': "'-O2 -pg'", 'petsc_version': '3.13', 'scorep_instrumentation': False, 'scorep_flags': ''}, {'std_out_path': '/home/kurse/kurs00054/jo83xafu/OUT/ISSM-MINIAPP-THERMAL_G1600_GCC_MPI96_GPROF/ISSM-MINIAPP-THERMAL_G1600_GCC_MPI96_GPROF.out', 'std_err_path': '/home/kurse/kurs00054/jo83xafu/OUT/ISSM-MINIAPP-THERMAL_G1600_GCC_MPI96_GPROF/ISSM-MINIAPP-THERMAL_G1600_GCC_MPI96_GPROF.err', 'job_time_limit': '00:30:00', 'mem_per_cpu': 3800, 'mpi_num_ranks': 96, 'number_of_tasks': 1, 'number_of_cores_per_task': 96, 'cpu_frequency_setting': 'Medium-Medium'}
            self.__run_res_tuples.append((out_dir, builder_config, job_config))
            # TEMP!
            #break
        print(f"Starting analyzing on experiment: {self.name}")
        analyzer = ResultAnalyzer(self.__run_res_tuples)
        results = analyzer.analyze()
        print(f"Starting exporting on experiment: {self.name}")
        exporter = Exporter(results, self.name)
        exporter.prepare()
        exporter.export()
        print(f"Finished run swarm: {self.name}")
