

class _FlatProfileEntry:
    """
    Entry for flat profile.
    """
    def __init__(self, percentage_total, cumulated_secs, self_secs, calls_to_this, self_ms_calls, cumulated_ms_calls, name):
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


class GProfAnalyzer:
    """
    Analyzer for GProf results.
    """
    def __init__(self, profile: str, threshold_percentage: float = 5.0):
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
        pass

    def analyze(self):
        """
        Analyze the results.
        """
        self.read_file()


# temporary for testing
if __name__ == "__main__":
    g = GProfAnalyzer("ISSM-MINIAPP-THERMAL_G64000_GCC_MPI96_GPROF.profile")
    g.analyze()