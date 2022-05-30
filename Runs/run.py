import os
import subprocess

from Builder.builder import BasicBuilder, App, Resolution, Compiler
from SLURM.default_slurm import DefaultPEngSlurmConfig

# source and executable paths by app:
from SLURM.exceptions import CommandExecutionException

source_path = {
    App.ISSM_MINIAPP_THERMAL: "issm-miniapp/",
    App.ISSM_MINIAPP_STRESSBALANCE: "issm-miniapp/",
    App.ISSM_4_18: "issm-4.18/"
}
executable_path = {
    App.ISSM_MINIAPP_THERMAL: "issm-miniapps/bin/miniappthermal.exe",
    App.ISSM_MINIAPP_STRESSBALANCE: "issm-miniapps/bin/miniappstressbalance.exe",
    App.ISSM_4_18: "issm-4.18/bin/issm.exe"
}
model_setup_path = {
    Resolution.G4000: "greenland-setup/G4000",
    Resolution.G16000: "greenland-setup/G16000",
    Resolution.G64000: "greenland-setup/G64000"

}
# mpirun -n 96 $ISSM_DIR/bin/issm.exe TransientSolution $PWD PAtransient_std_$FOLDER
default_runner = "mpirun"
default_run_command = "$ISSM_DIR/bin/issm.exe TransientSolution $PWD PAtransient_std_$FOLDER"


class BaseRun:
    """
    A Run for ISSM. Derive this for specific tooling. If you run this run, it will just run the app without any
    performance measurement tools.
    """

    def __init__(self,
                 app: App,
                 resolution: Resolution,
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
        self.run_command = f"{self.runner} -n {self.num_mpi_ranks} {run_command}"
        self.cleanup_build = cleanup_build
        self.execution_command = []
        self.jobfile = None
        self.home_dir = os.path.expanduser('~')
        self.builder = BasicBuilder(app, source_path[app])
        # Job name konvention: APP_RESOLUTION_COMPILER_MPI<NUM>[_TOOL[...]][OUT_ID/ERR_ID/JOB]
        self.jobname_skeleton = f"{self.app}_{self.resolution}_{self.compiler}_MPI{self.num_mpi_ranks}"
        # this will reflect in the filenames for out, err, and jobscript, and in the actual slurm job name
        self.slurm_configuration = DefaultPEngSlurmConfig(
            job_name=self.jobname_skeleton,
            job_file_directory=self.home_dir+"/"+model_setup_path[self.resolution],
            num_mpi_ranks=num_mpi_ranks
        )

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
        if self.own_build:
            # TODO maybe do additional ENV loading here
            # try:
            #     self.builder.build()
            # except CommandExecutionException as e:
            #     raise RuntimeError(e)
            self.__add_execution_command(self.builder.build())
            # TODO maybe do additional Module loading here
            # try:
            #     self.builder.load_modules()
            # except CommandExecutionException as e:
            #     raise RuntimeError(e)
            self.__add_execution_command(self.builder.load_modules())
        # generate job_script:
        self.slurm_configuration.add_command(self.run_command)
        self.slurm_configuration.write_slurm_script()

    def __run_execution_command(self):
        """
        Runs the summarized commands, in ONE subprocess call.
        """
        # put step numbers in output:
        run_cmd = []
        n = 1
        for cmd in self.execution_command:
            run_cmd.append(cmd)
            run_cmd.append(f"echo '####################### Step {n} #######################'")
            n = n + 1
        self.execution_command = ";".join(run_cmd)[1:]

        res = subprocess.run(["bash", "-c", self.execution_command],
                             #executable="/bin/bash",
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
        sbatch_command = self.slurm_configuration.sbatch(return_command=True)
        self.__add_execution_command(sbatch_command)
        # execute the whole thing:
        res = self.__run_execution_command()
        # get job id from res:
        res = res.stdout.decode("utf-8")
        print(res)
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

    def do_run(self):
        """
        Runs the whole run.
        """
        self.prepare()
        out_path, error_path = self.run()
        self.cleanup(remove_build=self.cleanup_build)
        return out_path, error_path


class GProfRun(BaseRun):
    """
    A run with the tool GProf.
    """

    def __init__(self, app: App, resolution: Resolution, gprof_out_filename: str = None):
        """
        Constructor.
        :param app: The app to use.
        :param resolution: The resolution to use.
        :param gprof_out_filename: You can give a alternative file name for the gprof output.
        Otherwise, it will be based on the jobname, to adhere to the naming scheme of everything else.
        """
        super().__init__(app, resolution)
        """
        From tools.py:
        
        ### GProf ###
        Hotspot detection with timings and everything. Also call graph inspections. 
        Uses a mixture of instrumentation and sampling.
        Usage: gprof BIN_NAME > gprof.profile, will pipe a GProf profile into specified file. 
        This file can be read, or viewed with the gprof GUI (https://www.ulfdittmer.com/profileviewer/).
        """
        super().prepend_run_command(prefix="gprof")
        file_name = f"{self.jobname_skeleton}_GPROF.profile" if not gprof_out_filename else f"{gprof_out_filename}.profile"
        super().pipe_run_command(to_file_path=self.slurm_configuration.get_out_dir()+file_name)
