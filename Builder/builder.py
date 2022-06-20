import os
import subprocess

from SLURM.exceptions import CommandExecutionException


class App:
    """
    Enum for App to run.
    """
    ISSM_CUSTOM_MINIAPP_STRESSBALANCE = "ISSM-CUSTOM-STRESSBALANCE"
    ISSM_CUSTOM_MINIAPP_THERMAL = "ISSM-CUSTOM-THERMAL"
    ISSM_MINIAPP_THERMAL = "ISSM-MINIAPP-THERMAL"
    ISSM_MINIAPP_STRESSBALANCE = "ISSM-MINIAPP-STRESSBALANCE"
    ISSM_4_18 = "ISSM-4-18"

    @classmethod
    def get(cls, app_name):
        if app_name == App.ISSM_MINIAPP_THERMAL:
            return App.ISSM_MINIAPP_THERMAL
        elif app_name == App.ISSM_MINIAPP_STRESSBALANCE:
            return App.ISSM_MINIAPP_STRESSBALANCE
        elif app_name == App.ISSM_4_18:
            return App.ISSM_4_18
        else:
            raise KeyError("App name not found.")


class Resolution:
    """
    Resolution for the greenland setup. Ties a name to the setups directory.
    """
    G4000 = "G4000"
    G16000 = "G1600"
    G64000 = "G64000"

    @classmethod
    def get(cls, res_name):
        if res_name == Resolution.G4000:
            return Resolution.G4000
        elif res_name == Resolution.G16000:
            return Resolution.G16000
        elif res_name == Resolution.G64000:
            return Resolution.G64000
        else:
            raise KeyError("Resolution not found.")


class Compiler:
    GCC = "GCC"
    LLVM = "LLVM"

    @classmethod
    def get(cls, compiler_name):
        if compiler_name == Compiler.GCC:
            return Compiler.GCC
        elif compiler_name == Compiler.LLVM:
            return Compiler.LLVM
        else:
            raise KeyError("Compiler not found.")


build_defaults = {
    "compiler": Compiler.GCC,
    "gcc_version": "10.2",
    "llvm_version": "10.0.0",
    "c_compiler_flags": "-O2",
    "fortran_compiler_flags": "-O2",
    "cxx_compiler_flags": "-O2",
    "petsc_version": "3.13",  # 3.13 and 3.14 are supported
    "scorep_instrumentation": False,
    "scorep_flags": "",
}


class BaseBuilder:
    """
    Builds and app of ISSM.
    """
    def __init__(self, app: App, source_path: str,
                 compiler: Compiler = build_defaults["compiler"],
                 gcc_version: str = build_defaults["gcc_version"],
                 llvm_version: str = build_defaults["llvm_version"],
                 c_compiler_flags: str = build_defaults["c_compiler_flags"],
                 fortran_compiler_flags: str = build_defaults["fortran_compiler_flags"],
                 cxx_compiler_flags: str = build_defaults["cxx_compiler_flags"],
                 petsc_version: str = build_defaults["petsc_version"],  # 3.13 and 3.14 are supported
                 scorep_instrumentation: bool = build_defaults["scorep_instrumentation"],
                 scorep_flags: str = build_defaults["scorep_flags"],
                 ):
        self.app = app
        self.source_path = source_path  # Relative to home dir, without leading "/"
        self.compiler = compiler
        self.gcc_version = gcc_version
        self.llvm_version = llvm_version
        self.c_compiler_flags = c_compiler_flags
        self.fortran_compiler_flags = fortran_compiler_flags
        self.cxx_compiler_flags = cxx_compiler_flags
        self.petsc_version = petsc_version
        self.scorep_instrumentation = scorep_instrumentation
        self.scorep_flags = scorep_flags
        self.home_dir = os.path.expanduser('~')

    def get_config(self):
        return {
            "app": self.app,
            "source_path": self.source_path,
            "compiler": self.compiler,
            "gcc_version": self.gcc_version,
            "llvm_version": self.llvm_version,
            "c_compiler_flags": self.c_compiler_flags,
            "fortran_compiler_flags": self.fortran_compiler_flags,
            "cxx_compiler_flags": self.cxx_compiler_flags,
            "petsc_version": self.petsc_version,  # 3.13 and 3.14 are supported
            "scorep_instrumentation": self.scorep_instrumentation,
            "scorep_flags": self.scorep_flags
        }

    def prepare_build(self):
        old_dir = os.getcwd()
        os.chdir(self.home_dir+"/issm-build-scripts/install/etc")
        # move env-build.sh file to a backup to keep the "original"
        subprocess.run(["mv", "env-build.sh", "env-build-BACKUP.sh"])
        # make a copy to edit
        subprocess.run(["cp", "env-build-BACKUP.sh", "env-build.sh"])
        lines = open("env-build.sh", "r").readlines()
        if self.compiler != build_defaults["compiler"]:
            cmd, arg = lines[12].split("=", 1)
            if self.compiler == Compiler.GCC:
                arg = "gcc"
            elif self.compiler == Compiler.LLVM:
                arg = "llvm"
            else:
                arg = build_defaults["compiler"]
            lines[12] = "=".join([cmd, arg])+"\n"
        if self.gcc_version != build_defaults["gcc_version"]:
            cmd, arg = lines[13].split("=", 1)
            lines[13] = "=".join([cmd, self.gcc_version])+"\n"
        if self.llvm_version != build_defaults["llvm_version"]:
            cmd, arg = lines[14].split("=", 1)
            lines[14] = "=".join([cmd, self.llvm_version])+"\n"
        if self.c_compiler_flags != build_defaults["c_compiler_flags"]:
            cmd, arg = lines[16].split("=", 1)
            lines[16] = "=".join([cmd, self.c_compiler_flags])+"\n"
        if self.cxx_compiler_flags != build_defaults["cxx_compiler_flags"]:
            cmd, arg = lines[20].split("=", 1)
            lines[20] = "=".join([cmd, self.cxx_compiler_flags])+"\n"
        if self.fortran_compiler_flags != build_defaults["fortran_compiler_flags"]:
            cmd, arg = lines[21].split("=", 1)
            lines[21] = "=".join([cmd, self.fortran_compiler_flags])+"\n"
        if self.petsc_version != build_defaults["petsc_version"]:
            cmd, arg = lines[31].split("=", 1)
            lines[31] = "=".join([cmd, self.petsc_version])+"\n"
        if self.scorep_instrumentation != build_defaults["scorep_instrumentation"]:
            cmd, arg = lines[34].split("=", 1)
            arg = "1" if self.scorep_instrumentation else "0"
            lines[34] = "=".join([cmd, arg])+"\n"
        if self.scorep_flags != build_defaults["scorep_flags"]:
            cmd, arg = lines[35].split("=", 1)
            lines[35] = "=".join([cmd, self.scorep_flags])+"\n"
        with open("env-build.sh", "w") as env_build_sh:
            for line in lines:
                env_build_sh.write(line)
        os.chdir(old_dir)

    def build(self, active: bool = True):
        if active:
            # Step 1: cd into the issm-build/install/ dir
            old_dir = os.getcwd()
            os.chdir(self.home_dir+"/issm-build-scripts/install/")
            # Step 2: run "./issm-build.sh PATH_TO_SOURCE"
            res = subprocess.run([f"./issm-build.sh {self.home_dir}/{self.source_path}"], shell=True, executable="/bin/bash", env=os.environ.copy())
            if res.returncode != 0:
                raise CommandExecutionException(f"./issm-build.sh {self.home_dir}/{self.source_path}")
            # cd back to old dir
            os.chdir(old_dir)
            return [""]
        else:
            return [f"cd {self.home_dir}/issm-build-scripts/install/", f"./issm-build.sh {self.home_dir}/{self.source_path}"]

    def cleanup_build(self):
        old_dir = os.getcwd()
        os.chdir(self.home_dir + "/issm-build-scripts/install/etc")
        # move env-build.sh file to a backup to keep the "original"
        subprocess.run(["mv", "env-build-BACKUP.sh", "env-build.sh"])
        # make a copy to edit
        subprocess.run(["rm", "env-build-BACKUP.sh"])
        os.chdir(old_dir)

    def load_modules(self, active: bool = True):
        if active:
            # Step 1: cd into the source_dir, there will now be a "issm-load.sh"
            old_dir = os.getcwd()
            os.chdir(self.home_dir+"/"+self.source_path)
            print(os.getcwd())
            # Step 2: source issm-load.sh
            # "source" is a bash build-in commands, you need a bash shell to run it,
            # not just a subprocess. Therefore, shell=True and executable="/bin/bash"
            res = subprocess.run(["source issm-load.sh"], shell=True, executable="/bin/bash", env=os.environ.copy())
            if res.returncode != 0:
                raise CommandExecutionException(f"source issm-load.sh")
            # cd back to old dir
            os.chdir(old_dir)
            return [""]
        else:
            return [f"cd {self.home_dir}/{self.source_path}", "source issm-load.sh"]


class GProfBuilder(BaseBuilder):
    """
    Builder for GProf.
    """
    def __init__(self, app: App, source_path: str):
        super().__init__(app, source_path,
                         c_compiler_flags=f"'{build_defaults['c_compiler_flags']} -pg'",
                         cxx_compiler_flags=f"'{build_defaults['cxx_compiler_flags']} -pg'",
                         )


class CompilerVectorizationReportBuilder(BaseBuilder):
    """
    Builder for Runs with Compiler Vectorization Report enabled.
    """
    def __init__(self, app: App, source_path: str, path_successful: str, path_unsuccessful: str, path_all: str = None, do_not_export_single_files: bool = False, gcc_flags: bool = True):
        self.path_successful = path_successful
        self.path_unsuccessful = path_unsuccessful
        self.path_all = path_all
        self.do_not_export_single_files = do_not_export_single_files
        additional_compiler_flags = ""
        # add out file paths
        if gcc_flags:
            # enable vectorization
            additional_compiler_flags = "-ftree-vectorize "
            if not self.do_not_export_single_files:
                additional_compiler_flags += f"-fopt-info-vec-optimized={self.path_successful} -fopt-info-vec-missed={self.path_unsuccessful}"
            if self.path_all:
                additional_compiler_flags += f"-fopt-info-vec-all={self.path_all}"
            additional_gf_flags = "-O3 -march=native"
        else:
            # TODO: put correct intel compiler flags
            if not self.do_not_export_single_files:
                additional_compiler_flags += f"-fopt-info-vec-optimized={self.path_successful} -fopt-info-vec-missed={self.path_unsuccessful}"
            if self.path_all:
                additional_compiler_flags += f"-fopt-info-vec-all={self.path_all}"
            additional_gf_flags = "-O3 -march=native"
        super().__init__(app, source_path,
                         c_compiler_flags=f"'{build_defaults['c_compiler_flags']} {additional_compiler_flags}'",
                         cxx_compiler_flags=f"'{build_defaults['cxx_compiler_flags']} {additional_compiler_flags}'",
                         fortran_compiler_flags=f"'{additional_gf_flags}'"
                         )


class CallgrindBuilder(BaseBuilder):
    """
    Builder for the valgrind callgrind tool.
    """
    def __init__(self, app: App, source_path: str):
        """
        Constructor.
        """
        # https://valgrind.org/docs/manual/cl-manual.html#cl-manual.basics
        # compile with -g and optimization (standard)
        super().__init__(app, source_path,
                         c_compiler_flags=f"'{build_defaults['c_compiler_flags']} -g'",
                         cxx_compiler_flags=f"'{build_defaults['cxx_compiler_flags']} -g'",
                         )


class ScorePBuilder(BaseBuilder):

    def __init__(self, app: App, source_path: str):
        """
        Constructor.
        """
        # https://valgrind.org/docs/manual/cl-manual.html#cl-manual.basics
        # compile with -g and optimization (standard)
        super().__init__(app, source_path,
                         scorep_instrumentation=True,
                         scorep_flags="",
                         )
