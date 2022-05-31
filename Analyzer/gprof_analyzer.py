

class _FlatProfileEntry:
    """
    Entry for flat profile.
    """
    def __init__(self):
        pass


class _CallGraphNode:
    """
    Node for the call graph.
    """
    def __init__(self):
        pass


class GProfAnalyzer:
    """
    Analyzer for GProf results.
    """
    def __init__(self, profile: str):
        """
        Constructor.
        """
        self.profile = profile
        self.flat_profile = []
        self.call_graph = []

    def read_file(self):
        """
        Reads the profile file into variables.
        """

    def analyze(self):
        """
        Analyze the results.
        """


# temporary for testing
if __name__ == "__main__":
    g = GProfAnalyzer("ISSM-MINIAPP-THERMAL_G64000_GCC_MPI96_GPROF.profile")
    g.analyze()