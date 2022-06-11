#import matplotlib as mpl


class MPIComparator:
    def __init__(self, analyzer_results):
        self.analyzer_results = analyzer_results
        self.results = {}

    def calc_speedups(self):
        pass

    def export_graph(self):
        pass

    def analyze(self):
        print("MPI Compare!!")
        print(self.analyzer_results)
        return self.results
