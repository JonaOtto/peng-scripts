from Runs.run import App, Resolution, GProfRun, CompilerVectorizationReportRun
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
    r = RunSwarm([run1, run2])
    r.do_run()

    print("FINISHED!!!!!")


