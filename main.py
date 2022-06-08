from Runs.run import App, Resolution, GProfRun, CompilerVectorizationReportRun, BaseRun
from Management.run_swarm import RunSwarm

if __name__ == '__main__':

    r = RunSwarm(name="GPROF_BOTH_MINIAPPS_G16000")
    # gprof miniapps
    r.add_run(GProfRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000
    ))
    r.add_run(GProfRun(
        app=App.ISSM_MINIAPP_STRESSBALANCE,
        resolution=Resolution.G16000,
        # own_build=False
    ))
    r.do_run()

    # ALL Apps gprof:

    r = RunSwarm(name="GPROF_ALL_APPS_G16000")
    # make vanilla runs to compare
    r.add_run(BaseRun(
        app=App.ISSM_MINIAPP_STRESSBALANCE,
        resolution=Resolution.G16000
    ))
    r.add_run(BaseRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000,
        # own_build=False
    ))
    # gprof miniapps
    r.add_run(GProfRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000,
        # own_build=False
    ))
    r.add_run(GProfRun(
        app=App.ISSM_MINIAPP_STRESSBALANCE,
        resolution=Resolution.G16000,
        # own_build=False
    ))
    # run the plain app to compare
    r.add_run(GProfRun(
        app=App.ISSM_4_18,
        resolution=Resolution.G16000
    ))
    r.do_run()

    print("FINISHED!!!!!")


