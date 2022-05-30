import os, subprocess
from SLURM.exceptions import CommandExecutionException


class App:
    """
    Enum for App to run.
    """
    ISSM_MINIAPP_THERMAL = "ISSM_MINIAPP_THERMAL"
    ISSM_MINIAPP_STRESSBALANCE = "ISSM_MINIAPP_STRESSBALANCE"
    ISSM_4_18 = "ISSM_4_18"


class Resolution:
    """
    Resolution for the greenland setup. Ties a name to the setups directory.
    """
    G4000 = "G4000"
    G16000 = "G1600"
    G64000 = "G64000"


class Compiler:
    GCC = "GCC"
    LLVM = "LLVM"


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
        self.source_path = source_path # Relative to home dir, without leading "/"
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

    def prepare_build(self):
        old_dir = os.getcwd()
        os.chdir(self.home_dir+"/issm-build-scripts/install/etc")
        # move env-build.sh file to a backup to keep the "original"
        subprocess.run(["mv", "env-build.sh", "env-build-BACKUP.sh"])
        # make a copy to edit
        subprocess.run(["cp", "env-build-BACKUP.sh", "env-build.sh"])
        lines = open("env-build.sh", "r").readlines()
        print("Compiler: ", lines[12])
        print("GCC Version: ", lines[13])
        print("LLVM Version: ", lines[14])
        print("C Flags: ", lines[16])
        print("C++ Flags: ", lines[20])
        print("F Flags: ", lines[21])
        print("PETSc version: ", lines[31])
        print("ScoreP Instrumentation: ", lines[34])
        print("ScoreP Flags: ", lines[35])
        raise RuntimeError()

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
        pass

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
