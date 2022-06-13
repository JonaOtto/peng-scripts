from Runs.run import *
from Management.experiment import Experiment

if __name__ == '__main__':

    # r = Experiment(name="GPROF_BOTH_MINIAPPS_G16000")
    # # gprof miniapps
    # r.add_run(GProfRun(
    #     app=App.ISSM_MINIAPP_THERMAL,
    #     resolution=Resolution.G16000,
    #     cleanup_build=False
    # ))
    # r.add_run(GProfRun(
    #     app=App.ISSM_MINIAPP_STRESSBALANCE,
    #     resolution=Resolution.G16000,
    #     own_build=False
    # ))
    # r.do_run()
    #
    # # ALL Apps gprof:
    #
    # r = Experiment(name="GPROF_ALL_APPS_G16000")
    # # make vanilla runs to compare
    # r.add_run(BaseRun(
    #     app=App.ISSM_MINIAPP_STRESSBALANCE,
    #     resolution=Resolution.G16000,
    #     cleanup_build=False
    # ))
    # r.add_run(BaseRun(
    #     app=App.ISSM_MINIAPP_THERMAL,
    #     resolution=Resolution.G16000,
    #     own_build=False,
    #     cleanup_build=False
    # ))
    # # gprof miniapps
    # r.add_run(GProfRun(
    #     app=App.ISSM_MINIAPP_THERMAL,
    #     resolution=Resolution.G16000,
    #     own_build=False,
    #     cleanup_build=False
    # ))
    # r.add_run(GProfRun(
    #     app=App.ISSM_MINIAPP_STRESSBALANCE,
    #     resolution=Resolution.G16000,
    #     own_build=False,
    #     cleanup_build=False
    # ))
    # # run the plain app to compare
    # r.add_run(GProfRun(
    #     app=App.ISSM_4_18,
    #     resolution=Resolution.G16000,
    #     cleanup_build=False
    # ))
    # r.do_run()
    #

    # e = Experiment(name="MINIAPPS-PLAIN-G16000")
    # e.add_run(BaseRun(app=App.ISSM_MINIAPP_THERMAL, resolution=Resolution.G16000, cleanup_build=False))
    # e.do_run()

    r = Experiment(name="CALLGRIND-G16000")
    r.add_run(CallgrindRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000,
    ))
    r.add_run(CallgrindRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000,
        cache_sim=True,
    ))
    r.add_run(CallgrindRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000,
        branch_sim=True,
    ))
    r.do_run()


    # r = Experiment(name="MPI-SCALE-TEST")
    # i = 3
    # r.add_run(
    #     MPIRun(app=App.ISSM_MINIAPP_THERMAL,
    #            resolution=Resolution.G16000,
    #            num_mpi_ranks=1)
    # )
    # while i <= 96:
    #     r.add_run(
    #         MPIRun(app=App.ISSM_MINIAPP_THERMAL,
    #                resolution=Resolution.G16000,
    #                num_mpi_ranks=i)
    #     )
    #     i = i * 2
    # r.do_run()

    print("FINISHED!!!!!")


