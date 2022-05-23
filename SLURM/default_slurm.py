from SLURM.slurm import SlurmConfiguration, MailType


class DefaultPEngSlurmConfig(SlurmConfiguration):
    """Holds the default SLURM job for the PEng seminar. All the paths will be derived from the job name."""

    def __init__(self,
                 job_name: str,
                 output_directory: str = "/work/scratch/kurse/kurs00054/jo83xafu",
                 job_file_directory: str = "/home/kurse/kurs00054/jo83xafu/jobfiles"):
        """
        Constructor.
        :param job_name: The jobs name. Use the job name wisely: Give info about the run, everything will be constructed upon this.
        Think about later processing!
        :param output_directory: The directory the std out- and err files goes in. Give without trailing slash.
        Defaults to my $HPC_SCRATCH. The job name will be added as an sub-directory.
        :param job_file_directory: The directory the job file goes in. Give without trailing slash.
        Defaults to: /home/kurse/kurs00054/jo83xafu/jobfiles.
        """
        # Manage file names:
        slurm_script_file = f"{job_file_directory}/JOB_{job_name}"
        std_out_path = f"{output_directory}/{job_name}/OUT_{job_name}"
        std_err_path = f"{output_directory}/{job_name}/ERR_{job_name}"

        # construct it
        super().__init__(slurm_script_file=slurm_script_file,
                         job_name=job_name,
                         std_out_path=std_out_path,
                         std_err_path=std_err_path,
                         time_str="00:15:00",
                         mem_per_cpu=3800,
                         number_of_tasks=1,
                         number_of_cores_per_task=96,
                         cpu_frequency_str="Medium-Medium",
                         partition="kurs00054",
                         reservation="kurs00054",
                         account="kurs00054",
                         shell="/bin/bash",
                         uses_module_system=True,
                         purge_modules_at_start=True,
                         mail_types=[MailType.END],
                         mail_address="jonathan.otto.37@stud.tu-darmstadt.de",
                         echo_job_task_info=True,
                         check_dirs_to_out=True,
                         use_set_u=True
                         )
        # Modules
        super().add_module(name="gcc", version="#TODO")
        super().add_module(name="clang", version="#TODO", depends_on=["gcc/#TODO"])
        super().add_module(name="cmake", depends_on=["gcc/#TODO"])

        # Commands
        super().add_command("FOLDER=$(basename $PWD)")
        super().add_command("mpirun -n 96 $ISSM_DIR/bin/issm.exe TransientSolution $PWD PAtransient_std_$FOLDER")
