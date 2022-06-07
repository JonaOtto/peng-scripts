from Runs.run import App, Resolution, GProfRun, CompilerVectorizationReportRun, BaseRun
from Management.run_swarm import RunSwarm

if __name__ == '__main__':
    # Run swarm 1
    r = RunSwarm(name="GPROF_Tests")
    r.add_run(GProfRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000
    ))
    r.add_run(GProfRun(
        app=App.ISSM_MINIAPP_STRESSBALANCE,
        resolution=Resolution.G16000,
        own_build=False
    ))
    r.do_run()
    # r.add_run(GProfRun(
    #     app=App.ISSM_MINIAPP_THERMAL,
    #     resolution=Resolution.G64000,
    #     own_build=False
    # ))
    # r.add_run(GProfRun(
    #     app=App.ISSM_MINIAPP_STRESSBALANCE,
    #     resolution=Resolution.G64000,
    #     own_build=False
    # ))
    # r.add_run(GProfRun(
    #     app=App.ISSM_MINIAPP_THERMAL,
    #     resolution=Resolution.G4000,
    #     own_build=False
    # ))
    # r.add_run(GProfRun(
    #     app=App.ISSM_MINIAPP_STRESSBALANCE,
    #     resolution=Resolution.G4000,
    #     own_build=False
    # ))
    print("FINISHED!!!!!")


