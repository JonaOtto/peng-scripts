# import matplotlib as mpl  # FIXME See below


class MPIComparator:
    def __init__(self, analyzer_results):
        self.analyzer_results = analyzer_results
        self.results = {}
        self.intermediate_res = []

    def calc_speedups(self):
        # sort them by cores
        for key, item in self.analyzer_results.items():
            self.intermediate_res.append((key, item))
        self.intermediate_res = sorted(self.intermediate_res, key=lambda x: x[0])
        # calculate speedups
        self.results["mpi_compare"] = {}
        for cores, results in self.intermediate_res:
            if (cores, results) == self.intermediate_res[0]:
                # first is baseline. Optimal this should be a result with one core
                print(results)
                try:
                    self.results["mpi_compare"][str(cores)] = {"calculation_time": results["calculation_time"]}
                except KeyError as e:
                    print(e)
            else:
                # Speedup = time(1 core)/time(p processors)
                speedup = results["calculation_time"]/self.intermediate_res[0][1]["calculation_time"]
                self.results["mpi_compare"][str(cores)] = {"calculation_time": results["calculation_time"], "speedup_to_first": speedup}
        self.results["mpi_compare"]["average"] = sum([ct[1]["calculation_time"] for ct in self.intermediate_res])/len(self.intermediate_res)

    def export_graph(self):
        # FIXME: The whole programm fails, if started from a venv. But: We need a venv for matplotlib if we want to generate plots
        # FIXME ... matplotlib! How? Why is this happening? I guess something with subprocesses...
        pass

    def analyze(self):
        print("MPI Compare!!")
        print(self.analyzer_results)
        self.calc_speedups()
        print(self.results)
        return self.results
