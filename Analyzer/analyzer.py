import os
from typing import List, Union, Tuple

from Builder.builder import App, Resolution, Compiler
from Analyzer.exceptions import *

default_out_dir = "/home/kurse/kurs00054/jo83xafu/OUT"
lichtenberg_defaults = {
    "cpu": "Intel AVX-512",
    "cpu_cores": 48,
    "cpu_count": 2,
    "mem": 38400,  # In MB
    "mem_type": "DDR4",
    "mem_frequency": 2933,
    "vector_type": "AVX",
    "vector_bits": 512,
    "network": "Infiniband HDR100",
    "network_speed": 100,  # GBit/s
}


### Helper classes ###


class ExperimentConfig:
    """
    All Data of a run, to analyze and compare.
    This should hold every aspect that can have performance influence on the experiment.
    This should be used to compare experiments, to make sure the environment is equal, to make good comparisons.
    """

    def __init__(self, result_file: Union[str, None],
                 job_id: int,
                 source_path: str,
                 job_time_limit: str,
                 mem_per_cpu: int,
                 number_of_tasks: int,
                 cpu_frequency_setting: str,
                 gcc_version: str,
                 llvm_version: str,
                 c_compiler_flags: str,
                 fortran_compiler_flags: str,
                 cxx_compiler_flags: str,
                 petsc_version: str,  # 3.13 and 3.14 are supported
                 scorep_instrumentation: bool,
                 scorep_flags: str,
                 app: App = None,
                 resolution: Resolution = None,
                 compiler: Compiler = None,
                 mpi_num_ranks: int = None,
                 cpu: str = lichtenberg_defaults["cpu"],
                 cpu_cores: int = lichtenberg_defaults["cpu_cores"],
                 cpu_count: int = lichtenberg_defaults["cpu_count"],
                 node_mem: int = lichtenberg_defaults["mem"],  # In MB
                 mem_type: str = lichtenberg_defaults["mem_type"],
                 mem_frequency: int = lichtenberg_defaults["mem_frequency"],
                 vector_type: str = lichtenberg_defaults["vector_type"],
                 vector_bits: int = lichtenberg_defaults["vector_bits"],
                 network: str = lichtenberg_defaults["network"],
                 network_speed: int = lichtenberg_defaults["network_speed"],  # GBit/s
                 *args,  # just pipe more given stuff, to not get an error
                 **kwargs  # we do not have to use them
                 ):
        self.result_file = result_file
        self.job_id = job_id
        self.source_path = source_path
        self.app = app
        self.resolution = resolution
        self.compiler = compiler
        self.mpi_num_ranks = mpi_num_ranks
        self.job_time_limit = job_time_limit
        self.mem_per_cpu = mem_per_cpu
        self.number_of_tasks = number_of_tasks
        self.cpu_frequency_setting = cpu_frequency_setting
        self.gcc_version = gcc_version
        self.llvm_version = llvm_version
        self.c_compiler_flags = c_compiler_flags
        self.fortran_compiler_flags = fortran_compiler_flags
        self.cxx_compiler_flags = cxx_compiler_flags
        self.petsc_version = petsc_version
        self.scorep_instrumentation = scorep_instrumentation
        self.scorep_flags = scorep_flags
        self.cpu = cpu
        self.cpu_cores = cpu_cores
        self.cpu_count = cpu_count
        self.node_mem = node_mem
        self.mem_type = mem_type
        self.mem_frequency = mem_frequency
        self.vector_type = vector_type
        self.vector_bits = vector_bits
        self.network = network
        self.network_speed = network_speed

    def is_comparable(self, other):
        """
        Check if a ExperimentConfig is comparable with another. This means everything should be equal but the
        result_file and the job_id.
        There may be cases where it is useful to have other "equal" definitions. They must be implemented on their own.
        """
        return \
            self.source_path == other.source_path and \
            self.app == other.app and \
            self.resolution == other.resolution and \
            self.compiler == other.compiler and \
            self.mpi_num_ranks == other.mpi_num_ranks and \
            self.job_time_limit == other.job_time_limit and \
            self.mem_per_cpu == other.mem_per_cpu and \
            self.number_of_tasks == other.number_of_tasks and \
            self.cpu_frequency_setting == other.cpu_frequency_setting and \
            self.gcc_version == other.gcc_version and \
            self.llvm_version == other.llvm_version and \
            self.c_compiler_flags == other.c_compiler_flags and \
            self.fortran_compiler_flags == other.fortran_compiler_flags and \
            self.cxx_compiler_flags == other.cxx_compiler_flags and \
            self.petsc_version == other.petsc_version and \
            self.scorep_instrumentation == other.scorep_instrumentation and \
            self.scorep_flags == other.scorep_flags and \
            self.cpu == other.cpu and \
            self.cpu_cores == other.cpu_cores and \
            self.cpu_count == other.cpu_count and \
            self.node_mem == other.node_mem and \
            self.mem_type == other.mem_type and \
            self.mem_frequency == other.mem_frequency and \
            self.vector_type == other.vector_type and \
            self.vector_bits == other.vector_bits and \
            self.network == other.network and \
            self.network_speed == other.network_speed

    def __eq__(self, other):
        """
        Override equality with is_comparable.
        """
        return self.is_comparable(other)


class _FlatProfileEntry:
    """
    Entry for flat profile.
    """

    def __init__(self, percentage_total, cumulated_secs, self_secs, calls_to_this, self_ms_calls, cumulated_ms_calls,
                 name):
        self.percentage_total = percentage_total
        self.cumulated_secs = cumulated_secs
        self.self_secs = self_secs
        self.calls_to_this = calls_to_this
        self.self_ms_calls = self_ms_calls
        self.cumulated_ms_calls = cumulated_ms_calls
        self.name = name


class _CallGraphNode:
    """
    Node for the call graph.
    """

    def __init__(self, index, total_time_percentage, self_time, child_time, called, name, parent_index):
        """
        Constructor.
        """
        self.index = index
        self.total_time_percentage = total_time_percentage
        self.self_time = self_time
        self.child_time = child_time
        self.called = called
        self.name = name
        self.parent_index = parent_index


### Result Analyzer ###


class ResultAnalyzer:
    """
    Looks at all output files and calls the matching analyzers.
    """

    def __init__(self, experiments: List[Tuple[str, dict, dict]], out_dir: str = default_out_dir):
        self.out_dir = out_dir
        # tuple of: the out path, the build config, the job config
        self.experiments = experiments
        # possible result files: dict of identifier, ExperimentConfig
        self.std_files = {
            # out
            # err
        }
        self.gprof_files = {
            # profile
        }
        self.cvr_files = {
            # opt
            # miss
            # all
        }

    def analyze(self):
        """
        Analyze all results for the given experiments.
        """
        # evaluate the files for configs
        for experiment, build_config, slurm_config in self.experiments:
            print(experiment)
            print(build_config)
            print(slurm_config)
            exp_dir = f"{experiment}"
            try:
                experiment, job_id = experiment.split(".", 1)
            except ValueError as e:
                # in case a run has no job ID in folder name,
                # this run has not done its cleanup yet, so is still running, or broken.
                # therefore ignore this folder.
                break
            exp_config = ExperimentConfig(result_file=None, job_id=job_id, **build_config, **slurm_config)
            files = os.listdir(exp_dir)
            for file in files:
                print(file)
                file_path = f"{exp_dir}/{file}"
                this_file_exp_config = exp_config
                this_file_exp_config.result_file = file_path
                # split naming scheme
                # Job name konvention: APP_RESOLUTION_COMPILER_MPI<NUM>[_TOOL/VANILLA][.fileextension][.job_id]
                name, extension = file.split(".", 1)
                file_job_id = None
                try:
                    extension, file_job_id = extension.split(".", 1)
                except ValueError as e:
                    pass
                opts = name.split("_")
                app_name, resolution, compiler, mpi, tool = opts[0], opts[1], opts[2], opts[3], opts[4]
                # update this info to the config:
                this_file_exp_config.app = App.get(app_name)
                this_file_exp_config.resolution = Resolution.get(resolution)
                this_file_exp_config.compiler = Compiler.get(compiler)
                this_file_exp_config.mpi_num_ranks = int(mpi[3:])
                print(this_file_exp_config)
                if len(opts) > 5:
                    raise NamingSchemeException(f"Too many items in file name: {file}")
                if file_job_id:
                    # job std files
                    if job_id not in self.std_files:
                        self.std_files[job_id] = {}
                    if extension == "out":
                        self.std_files[job_id]["out"] = this_file_exp_config
                    elif extension == "err":
                        self.std_files[job_id]["err"] = this_file_exp_config
                    elif extension == "job":
                        # This is the jobfile. Not of interest here
                        continue
                elif tool == "COMPILER-VEC-REPORT":
                    # CVR
                    if job_id not in self.cvr_files:
                        self.cvr_files[job_id] = {}
                    if extension == "all":
                        self.cvr_files[job_id]["all"] = this_file_exp_config
                    elif extension == "opt":
                        self.cvr_files[job_id]["opt"] = this_file_exp_config
                    elif extension == "miss":
                        self.cvr_files[job_id]["miss"] = this_file_exp_config
                elif tool == "GPROF" and extension == "profile":
                    # gprof
                    if job_id not in self.gprof_files:
                        self.gprof_files[job_id] = {}
                    self.gprof_files[job_id]["profile"] = this_file_exp_config
                elif tool == "VANILLA":
                    # TODO: What to do if vanilla? -> Baseline?
                    pass
                else:
                    continue
        # start the specific analyzers
        if self.std_files is not {}:
            for job_id in self.std_files.keys():
                std_analyzer = StdFileAnalyzer(job_id, **self.std_files[job_id])
                std_analyzer.analyze()
        if self.gprof_files is not {}:
            for job_id in self.gprof_files.keys():
                gprof_analyzer = GProfAnalyzer(job_id, **self.gprof_files)
                gprof_analyzer.analyze()
        if self.cvr_files is not {}:
            for job_id in self.cvr_files.keys():
                cvr_analyzer = CompilerVectorizationReportAnalyzer(job_id, **self.cvr_files)
                cvr_analyzer.analyze()


### Base ###


class BaseAnalyzer:
    """
    Analyzer base class.
    If you want to enable some functionality for all specific Analyzers, put it here.
    """

    def __init__(self, job_id: int):
        self.job_id = job_id

    def analyze(self):
        pass


### Specific Analyzers ###


class StdFileAnalyzer(BaseAnalyzer):
    """
    Analyzer for out and err file.
    """

    def __init__(self, job_id: int, out: ExperimentConfig = None, err: ExperimentConfig = None):
        """
        Constructor.
        """
        super().__init__(job_id)
        self.out_cnf = out
        self.err_cnf = err
        # results
        self.model_elements_avg = None
        self.model_loops_avg = None
        self.calculation_time = None
        self.setup_time = None

    def read_out_file(self, path):
        """
        Reads the std_out file.
        """
        with open(path, "r") as f:
            lines = f.readlines()
            print(lines)
            print(lines[-3])
            self.calculation_time = float(lines[-3].split(":", 1)[1][1:-1])
            model_elm_sum = 0.0
            model_elm_cnt = 0.0
            model_loop_sum = 0.0
            model_loop_cnt = 0.0
            for line in lines:
                if line.startswith("FemModel"):
                    model_elm_sum += float(line.split(",", 1)[0][18:-9])
                    model_elm_cnt += 1
                elif line.startswith(" -->"):
                    model_loop_sum += float(line[12:-6])
                    model_loop_cnt += 1
                elif line.startswith("   FemModel initialization elapsed time"):
                    self.setup_time = float(line.split(":")[1][3:-1])
            self.setup_time = self.setup_time * 100
            self.model_elements_avg = model_elm_sum / model_elm_cnt
            self.model_loops_avg = model_loop_sum / model_loop_cnt

    def analyze(self):
        print(f"\n\nANALYZING STD OUT for job: {self.job_id}")
        if self.out_cnf:
            self.read_out_file(self.out_cnf.result_file)
        print(f"Calculation Time: {self.calculation_time}")
        print(f"Setup Time: {self.setup_time}")
        print(f"Model element count average: {self.model_elements_avg}")
        print(f"Model loop count average: {self.model_loops_avg}")
        return self.calculation_time, self.model_elements_avg, self.model_loops_avg


class GProfAnalyzer(BaseAnalyzer):
    """
    Analyzer for GProf results.
    """

    def __init__(self, job_id: int, profile: ExperimentConfig, threshold_percentage: float = 5.0):
        """
        Constructor.
        """
        super().__init__(job_id)
        self.profile = profile
        self.threshold = threshold_percentage
        self.flat_profile = []
        self.call_graph = []

    def read_file(self):
        """
        Reads the profile file into variables.
        """
        pass

    def analyze(self):
        """
        Analyze the results.
        """
        self.read_file()

        print("\n\nANALYZING GPROF!!")
        print(self.profile)


class CompilerVectorizationReportAnalyzer(BaseAnalyzer):
    """
    Analyzer for CVR.
    """

    def __init__(self, job_id: int, all: ExperimentConfig = None, opt: ExperimentConfig = None,
                 miss: ExperimentConfig = None):
        """
        Constructor.
        """
        super().__init__(job_id)
        self.all_cnf = all
        self.opt_cnf = opt
        self.miss_cnf = miss

    def analyze(self):
        print("\n\nANALYZING CVR!!")
        print(self.all_cnf)
        print(self.opt_cnf)
        print(self.miss_cnf)
