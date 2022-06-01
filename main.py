from Runs.run import App, Resolution, GProfRun, CompilerVectorizationReportRun, BaseRun
from Management.run_swarm import RunSwarm

if __name__ == '__main__':
    # Run swarm 1
    run1 = GProfRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G64000
    )
    run2 = CompilerVectorizationReportRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G64000
    )
    r = RunSwarm(name="TestSwarm1", runs=[run1, run2])
    r.do_run()

    # timings test run:
    run3 = BaseRun(app=App.ISSM_MINIAPP_STRESSBALANCE, resolution=Resolution.G4000)
    run4 = BaseRun(app=App.ISSM_MINIAPP_THERMAL, resolution=Resolution.G4000, own_build=False)
    r2 = RunSwarm(name="Timing Test", runs=[run3, run4])
    #r2.do_run()
    print("FINISHED!!!!!")


