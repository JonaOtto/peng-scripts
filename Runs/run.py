import os
import subprocess

from Builder.builder import BasicBuilder, App, Resolution, Compiler
from SLURM.default_slurm import DefaultPEngSlurmConfig

# source and executable paths by app:
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
# job file archive: will hold copies of all job files
job_file_archive = "/home/kurse/kurs00054/jo83xafu/jobscript_archive"


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
        self.own_build = True
        self.runner = runner
        self.run_command = f"{self.runner} -n {self.num_mpi_ranks} {run_command}"
        self.cleanup_build = cleanup_build
        self.jobfile = None
        self.home_dir = os.path.expanduser('~')
        self.builder = BasicBuilder(app, source_path[app])
        # Job name konvention: APP_RESOLUTION_COMPILER_MPI<NUM>[_TOOL[...]]
        # this will reflect in the filenames for out, err, and jobscript, and in the actual slurm job name
        self.slurm_configuration = DefaultPEngSlurmConfig(
            job_name=f"{self.app}_{self.resolution}_{self.compiler}_MPI{self.num_mpi_ranks}",
            job_file_directory=self.home_dir+"/"+model_setup_path[self.resolution],
            num_mpi_ranks=num_mpi_ranks
        )

    def prepend_run_command(self, prefix):
        """
        Puts something in front of the run command.
        """
        self.run_command = f"{prefix} {self.run_command}"

    def pipe_run_command(self, to_file_path: str, triangle_pipe=True):
        """
        Pipes output of the runcommand to the to-file.
        """
        pipe_sign = ">" if triangle_pipe else "|"
        self.run_command = f"{self.run_command} {pipe_sign} {to_file_path}"

    def prepare(self):
        """
        Builds the ISSM build.
        """
        if self.own_build:
            # TODO maybe do additional ENV loading here
            self.builder.build()
            # TODO maybe do additional Module loading here
            self.builder.load_modules()
        # generate job_script:
        self.slurm_configuration.add_command(self.run_command)
        self.slurm_configuration.write_slurm_script()

    def run(self):
        """
        Runs the build.
        """
        job_id = self.slurm_configuration.sbatch()
        return self.slurm_configuration.wait(job_id)

    def cleanup(self, remove_build=False):
        # back up job file to archive
        subprocess.run(["cp", self.slurm_configuration.get_slurm_file_path() + ".sh", job_file_archive + "/"])
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
        self.cleanup(self.cleanup_build)
        return out_path, error_path
