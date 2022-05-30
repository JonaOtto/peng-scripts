import os, subprocess


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


class BasicBuilder:
    """
    Builds and app of ISSM.
    """

    def __init__(self, app: App, source_path: str):
        self.app = app
        self.source_path = source_path # Relative to home dir, without leading "/"
        self.home_dir = os.path.expanduser('~')

    def build(self):
        # Step 1: cd into the issm-build/install/ dir
        old_dir = os.getcwd()
        os.chdir(self.home_dir+"/issm-build-scripts/install/")
        # Step 2: run "./issm-build.sh PATH_TO_SOURCE"
        subprocess.run(["./issm-build.sh", self.home_dir+"/"+self.source_path], shell=True, executable="/bin/bash")
        # cd back to old dir
        os.chdir(old_dir)

    def load_modules(self):
        # Step 1: cd into the source_dir, there will now be a "issm-load.sh"
        old_dir = os.getcwd()
        os.chdir(self.home_dir+"/"+self.source_path)
        print(os.getcwd())
        # Step 2: source issm-load.sh
        # "source" is a bash build-in command, you need a bash shell to run it,
        # not just a subprocess. Therefore, shell=True and executable="/bin/bash"
        subprocess.run(["source issm-load.sh"], shell=True, executable="/bin/bash")
        # cd back to old dir
        os.chdir(old_dir)