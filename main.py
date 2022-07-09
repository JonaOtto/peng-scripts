from Runs.run import *
from Management.experiment import Experiment

if __name__ == '__main__':

    e = Experiment(name="GPROF_BOTH_MINIAPPS_G16000")
    # gprof miniapps
    e.add_run(GProfRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000,
        own_build=True,
        cleanup_build=True,
    ))
    e.add_run(GProfRun(
        app=App.ISSM_MINIAPP_STRESSBALANCE,
        resolution=Resolution.G16000,
        own_build=True,
        cleanup_build=True
    ))
    e.do_run()

    e = Experiment(name="VEC_REPORT_MINIAPPS")
    e.add_run(CompilerVectorizationReportRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000,
        own_build=True,
        cleanup_build=True,
    ))
    e.add_run(CompilerVectorizationReportRun(
        app=App.ISSM_MINIAPP_STRESSBALANCE,
        resolution=Resolution.G16000,
        own_build=True,
        cleanup_build=True,
    ))
    e.do_run()

    # e = Experiment(name="SCORE-P-RUNS")
    # e.add_run(ScorePRun(app=App.ISSM_MINIAPP_THERMAL, resolution=Resolution.G16000))
    # e.add_run(ScorePRun(app=App.ISSM_MINIAPP_STRESSBALANCE, resolution=Resolution.G16000))
    # e.do_run()
    # e.do_run()

    # e = Experiment(name="CACHEGRIND_WO_ARGS")
    # e.add_run(
    #     CachegrindRun(app=App.ISSM_MINIAPP_THERMAL, resolution=Resolution.G4000, append_args=False, own_build=True,
    #                   cleanup_build=True))
    # e.add_run(CachegrindRun(app=App.ISSM_MINIAPP_STRESSBALANCE, resolution=Resolution.G4000, append_args=False,
    #                         own_build=True, cleanup_build=True))
    # e.do_run()
    # e.do_run()
    # e.do_run()
    #
    # e = Experiment(name="CACHEGRIND_W_ARGS")
    # e.add_run(
    #     CachegrindRun(app=App.ISSM_MINIAPP_THERMAL, resolution=Resolution.G64000,
    #                   append_args=True, l1_size=128000, l1_associativity=2, l1_line=64, ll_size=143000000,
    #                   ll_associativity=2, ll_line=64,
    #                   own_build=True, cleanup_build=True))
    # e.add_run(CachegrindRun(app=App.ISSM_MINIAPP_STRESSBALANCE, resolution=Resolution.G64000,
    #                         append_args=True, l1_size=128000, l1_associativity=2, l1_line=64, ll_size=143000000,
    #                         ll_associativity=2,
    #                         ll_line=64,
    #                         own_build=True,
    #                         cleanup_build=True))
    # e.do_run()
    #
    # e = Experiment(name="CACHEGRIND_WO_ARGS")
    # e.add_run(
    #     CachegrindRun(app=App.ISSM_MINIAPP_THERMAL, resolution=Resolution.G64000, append_args=False, own_build=True,
    #                   cleanup_build=True))
    # e.add_run(CachegrindRun(app=App.ISSM_MINIAPP_STRESSBALANCE, resolution=Resolution.G64000, append_args=False,
    #                         own_build=True, cleanup_build=True))
    # e.do_run()

    # e = Experiment(name="MINIAPPS-PLAIN-G16000")
    # e.add_run(BaseRun(app=App.ISSM_MINIAPP_THERMAL, resolution=Resolution.G16000, own_build=True, cleanup_build=True))
    # e.add_run(BaseRun(app=App.ISSM_MINIAPP_STRESSBALANCE, resolution=Resolution.G16000, own_build=True, cleanup_build=True))
    # e.do_run()
    #
    # e = Experiment(name="CACHEGRIND_WO_ARGS")
    # e.add_run(CachegrindRun(app=App.ISSM_MINIAPP_THERMAL, resolution=Resolution.G16000, append_args=False, own_build=True, cleanup_build=True))
    # e.add_run(CachegrindRun(app=App.ISSM_MINIAPP_STRESSBALANCE, resolution=Resolution.G16000, append_args=False, own_build=True, cleanup_build=True))
    # e.do_run()
    #
    #
    # e = Experiment(name="SCORE-P-REGIONS")
    # e.add_run(ScorePRun(app=App.ISSM_ANNOTATED_MINIAPP_THERMAL, resolution=Resolution.G16000,
    #                     compiler_instrumentation=False,
    #                     user_instrumentation=True,
    #                     own_build=True, cleanup_build=True))
    # e.add_run(ScorePRun(app=App.ISSM_ANNOTATED_MINIAPP_STRESSBALANCE, resolution=Resolution.G16000,
    #                     compiler_instrumentation=False,
    #                     user_instrumentation=True,
    #                     own_build=True, cleanup_build=True))
    # e.do_run()
    #
    #
    print("FINISHED!!!!!")


