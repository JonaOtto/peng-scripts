import copy
import os
from typing import List, Union, Tuple, Callable

from Builder.builder import App, Resolution, Compiler
from Analyzer.exceptions import *
from Analyzer.mpi_comparator import MPIComparator

default_out_dir = "/home/kurse/kurs00054/jo83xafu/issm-output/OUT"
lichtenberg_defaults = {
    "os": "RedHat",
    "os_version": "8.5",
    "cpu": "Intel® Xeon® Platinum 9242",
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
                 os: str = lichtenberg_defaults["os"],
                 os_version: str = lichtenberg_defaults["os_version"],
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
        self.os = os
        self.os_version = os_version
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
        result_file, job_id, source_path and the compiler flags. Also, Apps and Resolution are not included in this:
        USE WITH CARE!!
        There may be cases where it is useful to have other "equal" definitions. They must be implemented on their own.
        """
        return \
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
            self.os == other.os and \
            self.os_version == other.os_version and \
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

    def as_dict(self, env=True):
        """
        env: Output stuff about environment, not job-specific stuff.
        """
        res = {
            "compiler": self.compiler,
            "mpi_num_ranks": self.mpi_num_ranks,
            "job_time_limit": self.job_time_limit,
            "mem_per_cpu": self.mem_per_cpu,
            "number_of_tasks": self.number_of_tasks,
            "cpu_frequency_setting": self.cpu_frequency_setting,
            "gcc_version": self.gcc_version,
            "llvm_version": self.llvm_version,
            "c_compiler_flags": self.c_compiler_flags,
            "fortran_compiler_flags": self.fortran_compiler_flags,
            "cxx_compiler_flags": self.cxx_compiler_flags,
            "petsc_version": self.petsc_version,
            "scorep_instrumentation": self.scorep_instrumentation,
            "scorep_flags": self.scorep_flags,
            "os": self.os,
            "os_version": self.os_version,
            "cpu": self.cpu,
            "cpu_cores": self.cpu_cores,
            "cpu_count": self.cpu_count,
            "node_mem": self.node_mem,
            "mem_type": self.mem_type,
            "mem_frequency": self.mem_frequency,
            "vector_type": self.vector_type,
            "vector_bits": self.vector_bits,
            "network": self.network,
            "network_speed": self.network_speed
        }
        if env:
            return res
        else:
            res.update({
                "result_file": self.result_file,
                "job_id": self.job_id,
                "source_path": self.source_path,
                "app": self.app,
                "model": self.resolution,
            })
            return res

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

    def as_dict(self):
        return {
            "percentage_total": self.percentage_total,
            "cumulated_seconds": self.cumulated_secs,
            "individual_seconds": self.self_secs,
            "number_of_calls_to_this": self.calls_to_this,
            "cumulated_milliseconds_per_call": self.cumulated_ms_calls,
            "individual_milliseconds_per_call": self.self_ms_calls,
            "name": self.name,
        }


class _CallGraphNode:
    """
    Node for the call graph.
    """

    def __init__(self, index, total_time_percentage, self_time, child_time, called, name, parent_indexes):
        """
        Constructor.
        """
        self.index = index
        self.total_time_percentage = total_time_percentage
        self.self_time = self_time
        self.child_time = child_time
        self.called = called
        self.name = name
        self.parent_indexes = parent_indexes

    def as_dict(self):
        return {
            "identifier": self.index,
            "total_percentage_of_time": self.total_time_percentage,
            "individual_time": self.self_time,
            "in_children_time": self.child_time,
            "number_of_calls_to_this": self.called,
            "name": self.name,
            "parent_indexes": self.parent_indexes
        }


### Result Analyzer ###


class ResultAnalyzer:
    """
    Looks at all output files and calls the matching analyzers.
    """

    def __init__(self, experiments: List[Tuple[str, dict, dict]], out_dir: str = default_out_dir, config_equal_f:
                 Callable[[ExperimentConfig, ExperimentConfig], bool] = None):
        self.out_dir = out_dir
        # tuple of: the out path, the build config, the job config
        self.experiments = experiments
        # callable for config comparison
        self.config_equal_f = config_equal_f
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
        self.callgrind_files = {
            # callgrind_out
        }
        self.mpi_compare = {
            # dict of MPI-NUM: results of std-out
        }

        self.results = {}

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
                this_file_exp_config = copy.deepcopy(exp_config)
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
                print(this_file_exp_config.result_file)
                if len(opts) > 5:
                    raise NamingSchemeException(f"Too many items in file name: {file}")
                if file_job_id:
                    print(extension)
                    # job std files
                    if job_id not in self.std_files:
                        self.std_files[job_id] = {}
                    if extension == "out":
                        if "VALGRIND" in tool:  # valgrind has different out files
                            continue
                        print(this_file_exp_config.result_file)
                        self.std_files[job_id]["out"] = this_file_exp_config
                        # add file to mpi compare for later mpi compare
                        # todo split for the apps
                        if tool == "MPI-COMPARE":
                            self.mpi_compare.update({this_file_exp_config.mpi_num_ranks: None})
                    elif extension == "err":
                        if "VALGRIND" in tool:  # valgrind has different out files
                            continue
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
                elif tool == "VALGRIND-CALLGRIND":
                    if job_id not in self.callgrind_files:
                        self.callgrind_files[job_id] = {}
                    if extension == "callgrind-out":
                        self.callgrind_files[job_id]["callgrind_out"] = this_file_exp_config
                    elif extension == "callgrind-vgcore":
                        self.callgrind_files[job_id]["callgrind_vgcore"] = this_file_exp_config
                elif tool == "VANILLA":
                    # TODO: What to do if vanilla? -> Baseline?
                    pass
                else:
                    continue
                del this_file_exp_config
        # start the specific analyzers
        all_configs = []
        all_equal = True
        if self.std_files is not {}:
            for job_id in self.std_files.keys():
                for config in self.std_files[job_id].values():
                    all_configs.append(config)
        if self.gprof_files is not {}:
            for job_id in self.gprof_files.keys():
                for config in self.gprof_files[job_id].values():
                    all_configs.append(config)
        if self.cvr_files is not {}:
            for job_id in self.cvr_files.keys():
                for config in self.cvr_files[job_id].values():
                    all_configs.append(config)
        if self.callgrind_files is not {}:
            for job_id in self.callgrind_files.keys():
                for config in self.callgrind_files[job_id].values():
                    all_configs.append(config)
        for i in range(len(all_configs) - 1):
            if self.config_equal_f:
                if not self.config_equal_f(all_configs[i], all_configs[i + 1]):
                    all_equal = False
            else:
                if not all_configs[i].is_comparable(all_configs[i + 1]):
                    all_equal = False
        self.results["environment"] = {}
        self.results["environment"]["is_static"] = all_equal
        if all_equal:
            # only add environment if its static
            try:
                self.results["environment"]["static_environment"] = all_configs[0].as_dict()
            except IndexError:
                self.results["environment"]["static_environment"] = None
        self.results["jobs"] = {}
        self.results["results"] = {}
        # TODO compare result data?
        if self.std_files is not {}:
            for job_id in self.std_files.keys():
                std_analyzer = StdFileAnalyzer(int(job_id), **self.std_files[job_id])
                job_id, configs, results = std_analyzer.analyze()
                self.results["jobs"][f"{job_id}"] = {"analyzed": [], "settings": {}}
                for name, cnf in configs.items():
                    self.results["jobs"][f"{job_id}"]["analyzed"].append({f"{name}": cnf.result_file})
                    self.results["jobs"][f"{job_id}"]["settings"].update(cnf.as_dict(env=False))
                    # update results to mpi compare
                    if cnf.mpi_num_ranks in self.mpi_compare:
                        self.mpi_compare[cnf.mpi_num_ranks] = results
                self.results["results"][f"{job_id}"] = {}
                self.results["results"][f"{job_id}"].update(results)
            # run mpi comparator
            if self.mpi_compare != {}:
                comparator = MPIComparator(self.mpi_compare)
                self.results["results"].update(comparator.analyze())
        if self.gprof_files is not {}:
            for job_id in self.gprof_files.keys():
                gprof_analyzer = GProfAnalyzer(int(job_id), **self.gprof_files[job_id])
                job_id, configs, results = gprof_analyzer.analyze()
                self.results["jobs"][f"{job_id}"]["analyzed"].append({f"profile": configs['profile'].result_file})
                self.results["results"][f"{job_id}"].update(results)
        if self.cvr_files is not {}:
            for job_id in self.cvr_files.keys():
                cvr_analyzer = CompilerVectorizationReportAnalyzer(int(job_id), **self.cvr_files[job_id])
                job_id, configs, results = cvr_analyzer.analyze()
                for name, cnf in configs.items():
                    self.results["jobs"][f"{job_id}"]["analyzed"].append({f"{name}": cnf.result_file})
                self.results["results"][f"{job_id}"].update(results)
        if self.callgrind_files is not {}:
            for job_id in self.callgrind_files.keys():
                callgrind_analyzer = CallgrindAnalyzer(int(job_id), **self.callgrind_files[job_id])
                job_id, configs, results = callgrind_analyzer.analyze()
                if type(self.results["jobs"][f"{job_id}"]) != dict:
                    self.results["jobs"][f"{job_id}"] = {"analyzed": [], "settings": {}}
                if type(self.results["results"][f"{job_id}"]) != dict:
                    self.results["results"][f"{job_id}"] = {}
                if self.results["jobs"][f"{job_id}"]["settings"] == {}:
                    self.results["jobs"][f"{job_id}"]["settings"].update(configs["callgrind_out"].as_dict(env=False))
                self.results["jobs"][f"{job_id}"]["analyzed"].append({f"callgrind_out": configs['callgrind_out'].result_file})
                self.results["results"][f"{job_id}"].update(results)
        print(self.results)
        return self.results

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
        self.total_time = None

    def read_out_file(self, path):
        """
        Reads the std_out file.
        """
        with open(path, "r") as f:
            lines = f.readlines()
            # if job broke, there will just be the three std lines from the generator (plus maybe time output)
            if len(lines) <= 4:
                return False
            try:
                self.calculation_time = float(lines[-3].split(":", 1)[1][1:-1])
            except IndexError:
                return False
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
                elif line.startswith("   Total elapsed time"):
                    # : 0 hrs 0 min 47 sec
                    hours = line.split(":")[1].split(" hrs ")
                    hours, rest = int(hours[0]), hours[1]
                    minutes = rest.split(" min ")
                    minutes, rest = int(minutes[0]), minutes[1]
                    seconds = int(rest.split(" sec")[0])
                    if len(str(hours)) == 1:
                        hours = f"0{hours}"
                    if len(str(minutes)) == 1:
                        minutes = f"0{minutes}"
                    if len(str(seconds)) == 1:
                        seconds = f"0{seconds}"
                    self.total_time = f"{hours}:{minutes}:{seconds}"
            self.setup_time = self.setup_time
            self.model_elements_avg = model_elm_sum / model_elm_cnt
            self.model_loops_avg = model_loop_sum / model_loop_cnt
        return True

    def read_out_file_418(self, path):
        """
        Reads the std_out file of real 4.18 issm app.
        """
        with open(path, "r") as f:
            lines = f.readlines()
            if len(lines) <= 4:
                return False
            for line in lines:
                if line.startswith("   FemModel initialization elapsed time"):
                    self.setup_time = float(line.split(":")[1].strip())
                elif line.startswith("   Total Core solution elapsed time"):
                    self.calculation_time = float(line.split(":")[1].strip())
                elif line.startswith("   Total elapsed time"):
                    # : 0 hrs 0 min 47 sec
                    hours = line.split(":")[1].split(" hrs ")
                    hours, rest = int(hours[0]), hours[1]
                    minutes = rest.split(" min ")
                    minutes, rest = int(minutes[0]), minutes[1]
                    seconds = int(rest.split(" sec")[0])
                    if len(str(hours)) == 1:
                        hours = f"0{hours}"
                    if len(str(minutes)) == 1:
                        minutes = f"0{minutes}"
                    if len(str(seconds)) == 1:
                        seconds = f"0{seconds}"
                    self.total_time = f"{hours}:{minutes}:{seconds}"
        return True

    def analyze(self):
        print(f"\n\nANALYZING STD OUT for job: {self.job_id}")
        configs = {}
        if self.out_cnf:
            configs["out"] = self.out_cnf
        if self.err_cnf:
            configs["err"] = self.err_cnf
        if self.out_cnf:
            if self.out_cnf.app != App.ISSM_4_18:
                if not self.read_out_file(self.out_cnf.result_file):
                    # return error in case of error
                    return self.job_id, configs, {"error": True, "message": "ISSM did not run! Check with error file!",
                                                  "error_file": None if not self.err_cnf else self.err_cnf.result_file}
            else:
                if not self.read_out_file_418(self.out_cnf.result_file):
                    # return error in case of error
                    return self.job_id, configs, {"error": True, "message": "ISSM did not run! Check with error file!",
                                                  "error_file": None if not self.err_cnf else self.err_cnf.result_file}
        print(f"Calculation Time: {self.calculation_time}")
        print(f"Setup Time: {self.setup_time}")
        print(f"Total Time: {self.total_time}")
        print(f"Model element count average: {self.model_elements_avg}")
        print(f"Model loop count average: {self.model_loops_avg}")

        results = {
            "setup_time": self.setup_time,
            "calculation_time": self.calculation_time,
            "total_time": self.total_time,
            "model_element_count_average": self.model_elements_avg,
            "model_loops_count_average": self.model_loops_avg
        }
        return self.job_id, configs, results


class GProfAnalyzer(BaseAnalyzer):
    """
    Analyzer for GProf results.
    """

    def __init__(self, job_id: int, profile: ExperimentConfig, threshold_percentage: float = 0.01):
        """
        Constructor.
        """
        super().__init__(job_id)
        self.profile = profile
        self.threshold = threshold_percentage
        self.flat_profile = []
        self.call_graph = []
        self.flat_profile_lines = []
        self.cg_lines = []

    def read_profile_file(self, path):
        """
        Reads the profile file into variables.
        """
        with open(path, "r") as f:
            lines = f.readlines()
            i = 0
            for i in range(5, len(lines)):
                line = lines[i][:-1]
                # print(line)
                if line != "":
                    # 19.81     10.22    10.22    62500     0.00     0.00  EnthalpyAnalysis::CreateKMatrixVolume(Element*)
                    elms = line.split(" ")
                    elms = [elm.strip() for elm in elms if elm.strip() != ""]
                    if float(elms[0]) < self.threshold:
                        continue
                    try:
                        entry = _FlatProfileEntry(
                            percentage_total=float(elms[0]),
                            cumulated_secs=float(elms[1]),
                            self_secs=float(elms[2]),
                            calls_to_this=int(elms[3]),
                            self_ms_calls=float(elms[4]),
                            cumulated_ms_calls=float(elms[5]),
                            name=" ".join(elms[6:])
                        )
                    except (ValueError, IndexError):
                        try:
                            entry = _FlatProfileEntry(
                                percentage_total=float(elms[0]),
                                cumulated_secs=float(elms[1]),
                                self_secs=float(elms[2]),
                                calls_to_this=None,
                                self_ms_calls=None,
                                cumulated_ms_calls=None,
                                name=" ".join(elms[3:])
                            )
                        except (ValueError, IndexError):
                            entry = _FlatProfileEntry(
                                percentage_total=None,
                                cumulated_secs=None,
                                self_secs=None,
                                calls_to_this=None,
                                self_ms_calls=None,
                                cumulated_ms_calls=None,
                                name=None
                            )
                    self.flat_profile.append(entry)
                else:
                    break
            j = i + 40
            while j < len(lines):
                caller_lines = []
                m = 0
                elms = None
                read = False
                while "---------" not in lines[j + m]:
                    if lines[j + m].startswith("["):
                        # print("start [:")
                        # print(lines[j + m][:-1])
                        elms = [elm.strip() for elm in lines[j + m].split(" ") if elm.strip() != ""]
                        read = True
                    elif not read:
                        # print("begginning line")
                        # print(lines[j + m][:-1])
                        caller_lines.append(lines[j + m][:-1].strip())
                    m = m + 1
                j = j + m
                # print(elms)
                # print(caller_lines)
                # print("---------")
                if float(elms[1]) < self.threshold:
                    break
                caller_ids = []
                start = False
                for caller_line in caller_lines:
                    if caller_line == "<spontaneous>" or start:
                        start = True
                        caller_ids.append(None)
                        called = None
                        name = " ".join(elms[4:])
                    else:
                        caller_ids.append(int(caller_line.split("[")[1].split("]")[0]))
                        called = float(elms[4])
                        name = " ".join(elms[5:])
                # [1]     98.1    0.00   50.61                 execute(int, char**, int, int, void (*)(FemModel*)) [1]
                self.call_graph.append(
                    _CallGraphNode(
                        index=int(elms[0][1:-1]),
                        total_time_percentage=float(elms[1]),
                        self_time=float(elms[2]),
                        child_time=float(elms[3]),
                        called=called,
                        name=name,
                        parent_indexes=caller_ids
                    )
                )
                j = j + 1

    def analyze(self):
        """
        Analyze the results.
        """
        print("\n\nANALYZING GPROF!!")
        if self.profile:
            self.read_profile_file(self.profile.result_file)
        for e in self.flat_profile:
            print(e.name, e.percentage_total)
        for e in self.call_graph:
            print(e.index, e.name, e.total_time_percentage)
        print(self.profile)
        results = {
            "used_min_percentage": self.threshold,
            "flat_profile": [fpe.as_dict() for fpe in self.flat_profile],
            "call_graph": [cgn.as_dict() for cgn in self.call_graph]
        }
        return self.job_id, {"profile": self.profile}, results


class CompilerVectorizationReportAnalyzer(BaseAnalyzer):
    """
    Analyzer for CVR.
    """

    def __init__(self, job_id: int, all: ExperimentConfig = None, opt: ExperimentConfig = None,
                 miss: ExperimentConfig = None, limit_to="src/c"):
        """
        Constructor.
        """
        super().__init__(job_id)
        self.all_cnf = all
        self.opt_cnf = opt
        self.miss_cnf = miss
        self.limit_to = limit_to

    def read_file(self, result_file) -> dict:
        with open(result_file, "r") as f:
            results = {}
            """ Dict: Keys are the files,
                which hold lists of dicts like {
                # line: line number of the loop
                # column: column of the loop
                # vectorized: t/f
                # vector_bytes if yes else None
                # reason (if not) else None
            } """
            for line in f.readlines():
                try:
                    try:
                        source, line, column, result, rest = line.split(":", 4)
                    except ValueError:
                        continue
                    if "note" in result:
                        continue
                    elif "missed" in result and "statement clobbers memory" in rest:
                        continue
                    if source not in results:
                        results[source] = []
                    if "missed" in result:
                        try:
                            reason = rest.split(":", 1)[1][:-1]
                        except IndexError:
                            reason = rest[:-1]
                        try:
                            res = {
                                "line": int(line),
                                "column": int(column),
                                "vectorized": False,
                                "vector_bits": None,
                                "reason": reason
                            }
                            if res not in results[source]:
                                if (self.limit_to and self.limit_to in source) or not self.limit_to:
                                    results[source].append(res)
                        except Exception as e:
                            print("Something went wrong reading CVR report: ", e,"::", type(e))
                    elif "optimized" in result:
                        try:
                            res = {
                                "line": int(line),
                                "column": int(column),
                                "vectorized": True,
                                "vector_bits": 8*int(rest.split(" byte")[0].split(" ")[-1]),
                                "reason": None,
                            }
                            if res not in results[source]:
                                if (self.limit_to and self.limit_to in source) or not self.limit_to:
                                    results[source].append(res)
                        except Exception as e:
                            print("Something went wrong reading CVR report: ", e)
                    else:
                        continue
                except IndexError:
                    continue
            return results


    def analyze(self):
        print("\n\nANALYZING CVR!!")
        print(self.all_cnf)
        print(self.opt_cnf)
        print(self.miss_cnf)
        configs = {}
        if self.all_cnf:
            configs["all"] = self.all_cnf
        if self.opt_cnf:
            configs["opt"] = self.opt_cnf
        if self.miss_cnf:
            configs["miss"] = self.miss_cnf
        # TODO: Actually extract the stuff from the files!
        """
        But for the paper in this case it was easier to just use Ctrl+F on the output files.
        """
        results = {}
        if self.all_cnf:
            results = self.read_file(self.all_cnf.result_file)
        elif self.opt_cnf and self.miss_cnf:
            results = self.read_file(self.opt_cnf.result_file)
            results.update(self.read_file(self.miss_cnf.result_file))
        return self.job_id, configs, results


class CallgrindAnalyzer(BaseAnalyzer):
    """
    Callgrind Analyzer.
    """
    def __init__(self, job_id: int, callgrind_out: ExperimentConfig = None, callgrind_vgcore: ExperimentConfig = None):
        super().__init__(job_id)
        self.callgrind_out = callgrind_out
        self.callgrind_vgcore = callgrind_vgcore

    def analyze(self):
        print("\n\nANALYZING CVR!!")
        print(self.callgrind_out)
        configs = {
            "callgrind_out": self.callgrind_out,
        }
        results = {
            "callgrind_out": self.callgrind_out.result_file,
            "callgrind_vgcore": self.callgrind_vgcore.result_file,
            "examine_with_cmd": f"kcachegrind {self.callgrind_out.result_file}"
        }
        return self.job_id, configs, results
