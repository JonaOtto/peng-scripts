from SLURM.slurm import SlurmConfiguration, MailType


class DefaultPEngSlurmConfig(SlurmConfiguration):
    """Holds the default SLURM job for the PEng seminar. All the paths will be derived from the job name."""

    def __init__(self,
                 job_name: str,
                 output_directory: str = "/home/kurse/kurs00054/jo83xafu/OUT",
                 job_file_directory: str = "/home/kurse/kurs00054/jo83xafu/jobfile_archive",
                 num_mpi_ranks: int = 96):
        """
        Constructor.
        :param job_name: The jobs name. Use the job name wisely: Give info about the run, everything will be constructed upon this.
        Think about later processing!
        :param output_directory: The directory the std out- and err files goes in. Give without trailing slash.
        Defaults to /home/kurse/kurs00054/jo83xafu/OUT. The job name will be added as an sub-directory.
        :param job_file_directory: The directory the job file goes in. Give without trailing slash.
        Defaults to: /home/kurse/kurs00054/jo83xafu/jobfiles.
        :param num_mpi_ranks: The number of mpi ranks
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
                         time_str="00:30:00",
                         mem_per_cpu=3800,
                         number_of_tasks=1,
                         number_of_cores_per_task=num_mpi_ranks,
                         cpu_frequency_str="Medium-Medium",
                         partition="kurs00054",
                         reservation="kurs00054",
                         account="kurs00054",
                         shell="/bin/bash",
                         uses_module_system=False,
                         purge_modules_at_start=False,
                         # mail_types=[MailType.END],
                         mail_address="jonathan.otto.37@stud.tu-darmstadt.de",
                         echo_job_task_info=True,
                         check_dirs_to_out=True,
                         use_set_u=True
                         )

        # Modules - will be set by the build scripts
        #super().add_module(name="gcc", version="#")
        #super().add_module(name="clang", version="#", depends_on=["gcc/#"])
        #super().add_module(name="cmake", depends_on=["gcc/#"])

        # Commands - actual execution will be added later
        super().add_command("FOLDER=$(basename $PWD)")
        #super().add_command("mpirun -n 96 $ISSM_DIR/bin/issm.exe TransientSolution $PWD PAtransient_std_$FOLDER")
