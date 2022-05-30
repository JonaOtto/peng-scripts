from Runs.run import App, Resolution, GProfRun

if __name__ == '__main__':
    run = GProfRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G16000,
        # own_build=False,
    )
    run.do_run()
    print("FINISHED!!!!!")


