from Runs.run import App, Resolution, GProfRun

if __name__ == '__main__':
    run = GProfRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G64000,
        own_build=True,
    )
    run.do_run()
    print("FINISHED!!!!!")


