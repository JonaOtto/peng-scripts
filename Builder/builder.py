import os, subprocess

from Runs.run import App


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
        subprocess.run(["issm-build.sh", self.home_dir+"/"+self.source_path])
        # cd back to old dir
        os.chdir(old_dir)

    def load_modules(self):
        # Step 1: cd into the source_dir, there will now be a "issm-load.sh"
        old_dir = os.getcwd()
        os.chdir(self.home_dir+"/"+self.source_path)
        # Step 2: source issm-load.sh
        subprocess.run(["source", "issm-load.sh"])
        # cd back to old dir
        os.chdir(old_dir)
