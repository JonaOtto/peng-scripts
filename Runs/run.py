import os
import subprocess

from Builder.builder import BaseBuilder, App, Resolution, Compiler, GProfBuilder, CompilerVectorizationReportBuilder
from SLURM.default_slurm import DefaultPEngSlurmConfig

# source and executable paths by app:
from SLURM.exceptions import CommandExecutionException

source_path = {
    App.ISSM_MINIAPP_THERMAL: "issm-miniapp/",
    App.ISSM_MINIAPP_STRESSBALANCE: "issm-miniapp/",
    App.ISSM_4_18: "issm-4.18/"
}
executable_path = {
    App.ISSM_MINIAPP_THERMAL: "issm-miniapp/bin/miniappthermal.exe",
    App.ISSM_MINIAPP_STRESSBALANCE: "issm-miniapp/bin/miniappstressbalance.exe",
    App.ISSM_4_18: "issm-4.18/bin/issm.exe"
}
model_setup_path = {
    Resolution.G4000: "greenland-setup/G4000",
    Resolution.G16000: "greenland-setup/G16000",
    Resolution.G64000: "greenland-setup/G64000"
}
is_active = {
    "build": True,
    "load_modules": False,
    "run": False,
}  # analyze and cleanup are after this: there are "active" bey default.
# mpirun -n 96 $ISSM_DIR/bin/issm.exe TransientSolution $PWD PAtransient_std_$FOLDER
default_runner = "mpirun"
default_executable = "$ISSM_DIR/bin/issm.exe"
default_run_command = "TransientSolution $PWD PAtransient_std_$FOLDER"


class BaseRun:
    """
    A Run for ISSM. Derive this for specific tooling. If you run this run, it will just run the app without any
    performance measurement tools.
    """

    def __init__(self,
                 app: App,
                 resolution: Resolution,
                 builder: BaseBuilder = None,
                 compiler: Compiler = Compiler.GCC,
                 num_mpi_ranks: int = 96,
                 own_build: bool = True,
                 runner: str = default_runner,
                 run_command: str = default_run_command,
                 cleanup_build: bool = False,
                 ):
        self.app = app
        self.resolution = resolution
        self.compiler = compiler
        self.num_mpi_ranks = num_mpi_ranks
        self.own_build = own_build
        self.runner = runner
        self.home_dir = os.path.expanduser('~')
        self.run_command = f"{self.runner} -n {self.num_mpi_ranks} {self.home_dir}/{executable_path[self.app]} {run_command}"
        self.cleanup_build = cleanup_build
        self.execution_command = []
        self.jobfile = None
        self.builder = builder
        if self.builder is None:
            self.builder = BaseBuilder(app, source_path[app])
        # Job name konvention: APP_RESOLUTION_COMPILER_MPI<NUM>[_TOOL[...]][OUT.ID/ERR.ID/JOB][.fileextension]
        self.jobname_skeleton = f"{self.app}_{self.resolution}_{self.compiler}_MPI{self.num_mpi_ranks}"
        # this will reflect in the filenames for out, err, and jobscript, and in the actual slurm job name
        # Slurm config
        self.slurm_configuration = DefaultPEngSlurmConfig(
            job_name=self.jobname_skeleton,
            job_file_directory=self.home_dir + "/" + model_setup_path[self.resolution],
            num_mpi_ranks=self.num_mpi_ranks
        )

    def add_tool(self, name: str):
        """
        Adds a tool to the naming scheme.
        """
        self.jobname_skeleton = f"{self.jobname_skeleton}_{name}"

    def prepend_run_command(self, prefix: str):
        """
        Puts something in front of the run commands.
        """
        self.run_command = f"{prefix} {self.run_command}"

    def pipe_run_command(self, to_file_path: str, triangle_pipe=True):
        """
        Pipes output of the runcommand to the to-file.
        """
        pipe_sign = ">" if triangle_pipe else "|"
        self.run_command = f"{self.run_command} {pipe_sign} {to_file_path}"

    def __add_execution_command(self, commands):
        """
        Adds a commands to add to execution. Helper: Everything must be in ONE subprocess call, otherwise it messes up env vars.
        """
        self.execution_command.extend(commands)

    def prepare(self):
        """
        Builds the ISSM build.
        """
        # Slurm config
        self.slurm_configuration = DefaultPEngSlurmConfig(
            job_name=self.jobname_skeleton,
            job_file_directory=self.home_dir + "/" + model_setup_path[self.resolution],
            num_mpi_ranks=self.num_mpi_ranks
        )
        if self.own_build:
            if is_active["build"]:
                self.builder.prepare_build()
                # TODO maybe do additional ENV loading here
                try:
                    self.builder.build(active=True)
                except CommandExecutionException as e:
                    raise RuntimeError(e)
                # If we build actively, we can clean up now,
                # otherwise the build command not run yet, do it in the cleanup method.
                self.builder.cleanup_build()
            else:
                self.__add_execution_command(self.builder.build(active=False))
        if is_active["load_modules"]:
            # TODO maybe do additional Module loading here
            try:
                self.builder.load_modules(active=True)
            except CommandExecutionException as e:
                raise RuntimeError(e)
        else:
            self.__add_execution_command(self.builder.load_modules(active=False))
        # generate job_script:
        self.slurm_configuration.add_command(self.run_command)
        self.slurm_configuration.write_slurm_script()

    def __run_passive_commands(self):
        """
        Runs the summarized commands, in ONE subprocess call.
        """
        # put step numbers in output:
        run_cmd = []
        n = 1
        for cmd in self.execution_command:
            run_cmd.append(f"echo '####################### Step {n} #######################'")
            run_cmd.append(cmd)
            n = n + 1
        self.execution_command = ";".join(run_cmd)

        res = subprocess.run(["bash", "-c", self.execution_command],
                             executable="/bin/bash",
                             #shell=True,
                             env=os.environ.copy(),
                             stdout=subprocess.PIPE)
        if res.returncode != 0:
            raise CommandExecutionException(self.execution_command)
        return res

    def run(self):
        """
        Runs the build.
        """
        if is_active["run"]:
            job_id = self.slurm_configuration.sbatch(active=True)
        else:
            sbatch_command = self.slurm_configuration.sbatch(active=False)
            print("Sbatch command: ", sbatch_command)
            self.__add_execution_command([f"cd {self.home_dir}/{model_setup_path[self.resolution]}", sbatch_command])
            # execute the whole thing:
            res = self.__run_passive_commands()
            # get job id from res:
            res = res.stdout.decode("utf-8")
            print("Result: ", res)
            res = res.split("Submitted batch job")[1]
            job_id = int(res.split(" ")[1].split("\n")[0])
        return self.slurm_configuration.wait(job_id)

    def cleanup(self, remove_build: bool = False):
        # back up job file to the OUT dir
        subprocess.run(["cp", self.slurm_configuration.get_slurm_file_path() + ".sh", self.slurm_configuration.get_out_dir()])
        # Clean up job file (leave model dirs clean)
        os.remove(self.slurm_configuration.get_slurm_file_path()+".sh")
        if remove_build:
            folder = self.home_dir+"/"+"/".join(executable_path[self.app].split("/")[:-1])
            os.remove(f"{self.home_dir}/{executable_path[self.app]}")  # the executable
            os.remove(f"{self.home_dir}/{folder}/issm-load.sh")  # issm-load.sh
            os.remove(f"{self.home_dir}/{folder}/issmModule.lua")  # issmMoudle.lua
        if not is_active["build"]:
            self.builder.cleanup_build()

    def analyze(self):
        """
        Analyze the output.
        """
        print("Analyzing...")

    def do_run(self):
        """
        Runs the whole run.
        """
        self.prepare()
        out_path, error_path = self.run()
        self.cleanup(remove_build=self.cleanup_build)
        print(f"\nOut file: {out_path}")
        print(f"Err file: {error_path}\n")
        self.analyze()


class GProfRun(BaseRun):
    """
    A run with the tool GProf.
    """

    def __init__(self, app: App, resolution: Resolution, gprof_out_filename: str = None, *args, **kwargs):
        """
        Constructor.
        :param app: The app to use.
        :param resolution: The resolution to use.
        :param gprof_out_filename: You can give a alternative file name for the gprof output.
        Otherwise, it will be based on the jobname, to adhere to the naming scheme of everything else.
        """
        builder = GProfBuilder(app, source_path[app])
        super().__init__(app, resolution, builder=builder, *args, **kwargs)
        """
        From tools.py:
        
        ### GProf ###
        Hotspot detection with timings and everything. Also call graph inspections. 
        Uses a mixture of instrumentation and sampling.
        Usage: gprof BIN_NAME > gprof.profile, will pipe a GProf profile into specified file. 
        This file can be read, or viewed with the gprof GUI (https://www.ulfdittmer.com/profileviewer/).
        """
        # update the job name
        self.add_tool("GPROF")
        # add gprof
        # super().prepend_run_command(prefix="gprof")
        file_name = f"{self.jobname_skeleton}.profile" if not gprof_out_filename else f"{gprof_out_filename}.profile"
        gprof_file = self.slurm_configuration.get_out_dir()+file_name
        self.slurm_configuration.add_command(f"gprof {self.home_dir}/{executable_path[self.app]} > {gprof_file}")


class CompilerVectorizationReportRun(BaseRun):
    """
    Run class for the Compiler Vectorization Report tool.
    """

    def __init__(self, app: App, resolution: Resolution, vec_out_dir: str = None, *args, **kwargs):
        """
        Constructor.
        :param app: The app to run.
        :param resolution: The resolution of the model to run.
        :param vec_out_dir: Alternative dir for the out files. Otherwise, it will be constructed off the job name,
        to adhere to the standard naming scheme. Give with trailing slash!
        """
        tool = "COMPILER_VEC_REPORT"
        # we have to add the tool here bevor, because we can add it to the runner only if the super call took place,
        # for this we need the builder first
        file_name_opt = f"{self.jobname_skeleton}_{tool}.opt"
        file_name_miss = f"{self.jobname_skeleton}_{tool}.miss"
        file_name_all = None
        if vec_out_dir:
            file_name_all = f"{self.jobname_skeleton}_{tool}.all"
        path = self.slurm_configuration.get_out_dir() if not vec_out_dir else vec_out_dir
        if not vec_out_dir:
            builder = CompilerVectorizationReportBuilder(app, source_path[app],
                                                         path_successful=f"{path}{file_name_opt}",
                                                         path_unsuccessful=f"{path}{file_name_miss}"
                                                         )
        else:
            builder = CompilerVectorizationReportBuilder(app, source_path[app],
                                                         path_successful=f"{path}{file_name_opt}",
                                                         path_unsuccessful=f"{path}{file_name_miss}",
                                                         path_all=f"{path}{file_name_all}"
                                                         )
        super().__init__(app, resolution, builder=builder, *args, **kwargs)
        # update the job name
        self.add_tool(tool)
