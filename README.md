# peng-scripts
Scripts for performance engineering course at TU Darmstadt.

## Installation

1. Clone this repo to the lichtenberg

## Dependencies

- You will need a python3 interpreter or virtual environment
- It expects to find a computer with the SLURM workload manager and a "module" system. If this is not the case, more or less everything will break. This works best, or maybe only on the Lichtenberg cluster.

## Setup

To make the code working on your Lichtenberg account do the following:

- Dependent on where you put the `issm-4.18` code, the `issm-miniapp`s code, the `issm-build-scripts` and the `greenland-setup` repos, you need to update the paths in `source_path`, `executable_path` and `model_setup_path` at the top of `Runs/run.py`.
- Dependent on where you want your out and result files to be generated, update the top of `Management/exporter.py`: `default_out_dir`, `git_dir`, and `use_git`.
- You might want to adjust your SLURM settings in `SLURM/default_slurm.py`.

## Usage

First, you have to configure the experiments you want to run in the `main.py`. There are several `Run`s available: 

- `BaseRun`: Vanilla execution
- `GProfRun`: Run with GProf tool
- `CompilerVectorizationReportRun`: Run with GCC's compiler vectorization report
- `CallgrindRun`: Run with valgrind callgrind
- `MPIRun`: Run with multiple runs, to check the differences with different counts of MPI ranks.
- `ScorePRun`: Run with Score-P tool. You can configure compiler instrumentation, or user instrumentation with the parameters. Tracing is not enabled.
- `CachegrindRun`: Run with valgrind cachgrind

Each experiment have to have the parameters `app` and `resolution`.

The app describes which issm code from which folder (remember the `source_path` setting). Currently, there are versions for the miniapps and the issm-4.18, each with normal, custom, annotated, and annotated-custom variants. This is meant to give to opportunity to run the apps original and with custom updates or manual instrumentation (or both), to compare the results.
The resolution describes which greenland model should be used. That's either `G4000`, `G16000` and `G64000`.

Write your `main.py`:

An example for an experiment is given here:

```python
e = Experiment(name="HOTSPOTS-GPROF-CVR")
e.add_run(GProfRun(
	app=App.ISSM_MINIAPP_THERMAL,
	resolution=Resolution.G16000, 
	own_build=True, 
	cleanup_build=True
))
e.add_run(CompilerVectorizationReportRun(
	app=App.ISSM_MINIAPP_THERMAL,
	resolution=Resolution.G16000, 
	own_build=True, 
	cleanup_build=True
))
e.do_run()
```

You surely can have multiple experiments in your `main.py`. Each experiment can hold as many runs as you want, but at least one.

If you are happy with your setup, run `python3 main.py` to execute the experiments.

Please be aware: This is all code that evolved over time, and I did not use all its features for my research. Especially these part that I did not use, may have errors.

