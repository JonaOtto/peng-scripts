from Runs.run import App, Resolution, BaseRun

if __name__ == '__main__':
    run = BaseRun(
        app=App.ISSM_MINIAPP_THERMAL,
        resolution=Resolution.G64000,
        # own_build=False,
    )
    run.do_run()
    print("FINISHED!!!!!")


