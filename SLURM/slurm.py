# from __future__ import annotations

import os
import subprocess
import time
from typing import Optional, List

from SLURM.exceptions import ModuleDependencyConflict, ScriptNotFoundException, CommandExecutionException


class MailType:
    """
    Enum for SLURM Mail types (--mail-type setting).
    """
    BEGIN = "BEGIN"
    END = "END"
    FAIL = "FAIL"
    ALL = "ALL"
    NONE = "None"


class _Module:
    """
    Helper class for module system modules.
    """

    def __init__(self, name: str, version: Optional[str] = None, depends_on: Optional[List[str]] = None):
        """
        Constructor.
        :param name: The modules name.
        :param version: The modules version.
        :param depends_on: List of module names the modules depends on. These will be loaded bevor this module.
        """
        self.name = name
        self.version = version
        self.depends_on = depends_on

    def check_dependency_conflicts(self, other_modules) -> None:
        """
        Checks if there are circular conflicts in dependencies.
        :param other_modules: List of other modules to check with.
        :return: void, raises ModuleDependencyConflict exception if a conflict was detected.
        """
        if self.depends_on:
            for dependency in self.depends_on:
                for compare_module in other_modules:
                    # if compare module in general is a dependency, or the compare module in its version.
                    if compare_module.name == dependency or \
                            (compare_module.version is not None and compare_module.name + "/" + compare_module.version == dependency):
                        if compare_module.depends_on:
                            # if either general module or module with version depends back on this module
                            if self.name in compare_module.depends_on or \
                                    (self.version is not None and self.name+"/"+self.version in compare_module.depends_on):
                                raise ModuleDependencyConflict(f"Dependency conflict: Module {self.name} depends on "
                                                               f"{dependency}, but {compare_module.name} "
                                                               f"depends on {self.name}.")


class SlurmConfiguration:
    """
    Holds config for SLURM run. Wrapper for an SLURM-script.
    """

    def __init__(self, slurm_script_file: str,
                 job_name: str,
                 std_out_path: str, std_err_path: str,
                 time_str: str,
                 mem_per_cpu: int,
                 number_of_tasks: int, number_of_cores_per_task: int,
                 cpu_frequency_str: Optional[str] = None,
                 partition: Optional[str] = None, reservation: Optional[str] = None, account: Optional[str] = None,
                 job_array_start: Optional[int] = None, job_array_end: Optional[int] = None, job_array_step: int = 1,
                 exclusive: bool = False,
                 dependencies: Optional[List[str]] = None,
                 mail_types: Optional[List[MailType]] = None, mail_address: Optional[str] = None,
                 echo_job_task_info: bool = True,
                 uses_module_system: bool = False,
                 shell: str = "/bin/bash",
                 purge_modules_at_start: bool = True,
                 check_dirs_to_out: bool = True,
                 use_set_u: bool = False
                 ) -> None:
        """
        Constructor.
        :param slurm_script_file: The file to save the SLURM script.
        :param job_name: Job name, -J or --job-name setting.
        :param std_out_path: Path to put the stdout of the job, -o or --out setting. Give the absolute file path.
        The job id will be added at the back automatically.
        :param std_err_path: Path to put the stderr of the job, -e or --err setting. Give the absolute file path.
        The job id will be added at the back automatically.
        :param time_str: Time limit for the job, --time or -t setting. Give string in ‘mm’, ‘mm:ss’ or ‘hh:mm:ss’
        :param mem_per_cpu: Memory per thread, the --mem-per-cpu setting.
        :param number_of_tasks: Number of cores/individual processing units you want, the -n or --ntasks setting.
        E.g. important for MPI.
        :param number_of_cores_per_task: Number of threads per process you want, the --cpus-per-task or -c setting.
        :param cpu_frequency_str: Set this to ensure the processors run on equal speeds
        (disables all fancy overclocking, hyperboots, ... features), the --cpu-freq setting.
        Do not specify if you do not want a fixed cpu speed. Default: None.
        :param partition: Partition for the job, -p or --partition setting. Default: None.
        :param reservation: Reservation for the job, the --reservation setting. Default: None.
        :param account: Allocation for the job, the -A option. Default: None.
        :param job_array_start: Start id for job array, part of the -a setting.
        If you do not want a job array, do not specify job_array_start and job_array_end. Default: None.
        :param job_array_end: End id for job array, part of the -a setting.
        If you do not want a job array, do not specify job_array_start and job_array_end. Default: None.
        :param job_array_step: Step for the job array, part of the -a setting. Default: 1.
        :param mail_types: Mail types, the --mail-type setting.
        If not specified, --mail-type=NONE will be set automatically. Default: None.
        :param mail_address: Mail address, the --mail-user setting. Default: None.
        :param exclusive: If the job should run exclusively on the node, the --exclusive setting. Default: False.
        :param dependencies: List of dependency stings. Default: None.
        :param echo_job_task_info: If echoing commands with job id,
        and task id prints should be added to the SLURM script automatically. Default: True.
        :param uses_module_system: Whether the system uses a module system, with "module load/purge" commands.
        :param shell: The shell/shebang for the system. Default: "/bin/bash".
        :param purge_modules_at_start: If modules should be purged bevor module load commands.
        Has no effect if "uses_module_system" is not True. Default: True.
        :param check_dirs_to_out: Check the path to stdout and stderr files for non-existing directories,
        and add them if some are missing. Default: True.
        :param use_set_u: If the command "set -u" should be added to your SLURM job file. Default: False.
        """
        self.__slurm_script_file = slurm_script_file
        self.__job_name = job_name
        self.__std_out_path = std_out_path
        self.__std_err_path = std_err_path
        self.__time_str = time_str
        self.__mem_per_cpu = mem_per_cpu
        self.__number_of_tasks = number_of_tasks
        self.__number_of_cores_per_task = number_of_cores_per_task
        self.__cpu_frequency_str = cpu_frequency_str
        self.__partition = partition
        self.__reservation = reservation
        self.__account = account
        self.__job_array = None
        self.set_job_array(job_array_start, job_array_end, job_array_step)
        self.__exclusive = exclusive
        self.__dependencies = dependencies
        self.__mail_types = ",".join(str(mt) for mt in mail_types) if mail_types else None
        self.__mail_address = mail_address
        self.__echo_job_task_info = echo_job_task_info
        self.__uses_module_system = uses_module_system
        self.__shell = shell
        self.__purge_modules_at_start = purge_modules_at_start
        self.__check_dirs_to_out = check_dirs_to_out
        self.__use_set_u = use_set_u
        # Non-parameter variables
        self.__modules: List[_Module] = []
        self.__commands: List[str] = []

    def set_system_info(self, shell: str = "/bin/bash", uses_module_system: bool = False,
                        purge_modules_at_start: bool = True) -> None:
        """
        Sets infos about the system.
        :param shell: The systems shell for bash.
        :param uses_module_system: Whether the system uses a module system, with "module load/purge" commands.
        :param purge_modules_at_start: If modules should be purged bevor module load commands.
        Has no effect if "uses_module_system" is not True. Default: True.
        :return: void.
        """
        self.__shell = shell
        self.__uses_module_system = uses_module_system
        self.__purge_modules_at_start = purge_modules_at_start

    def set_mail_settings(self, mail_types: Optional[List[MailType]] = None,
                          mail_address: Optional[str] = None) -> None:
        """
        Sets mail settings.
        :param mail_types: Mail types, the --mail-type setting.
        If not specified, --mail-type=NONE will be set automatically. Default: None.
        :param mail_address: Mail address, the --mail-user setting. Default: None.
        :return: void.
        """
        self.__mail_types = ",".join(str(mt) for mt in mail_types) if mail_types else None
        self.__mail_address = mail_address

    def set_helping_options(self,
                            echo_job_task_info: bool = True,
                            check_dirs_to_out: bool = True,
                            use_set_u: bool = False) -> None:
        """
        Sets helping options.
        :param echo_job_task_info: If echoing commands with job id,
        and task id prints should be added to the SLURM script automatically. Default: True.
        :param check_dirs_to_out: Check the path to stdout and stderr files for non-existing directories,
        and add them if some are missing. Default: True.
        :param use_set_u: If the command "set -u" should be added to your SLURM job file. Default: False.
        :return: void.
        """
        self.__echo_job_task_info = echo_job_task_info
        self.__check_dirs_to_out = check_dirs_to_out
        self.__use_set_u = use_set_u

    def set_job_array(self, start: Optional[int] = None, end: Optional[int] = None, step: int = 1) -> None:
        """
        Set job array settings. This will set the self.__job_array variable.
        :param start: start index.
        :param end: end index.
        :param step: step width.
        :return: void.
        """
        if start is not None and end is not None:
            self.__job_array = str(start) + "-" + str(end) + "%" + str(step)

    def get_slurm_file_path(self):
        """
        Getter for slurm script path.
        """
        return self.__slurm_script_file

    def add_module(self, name: str, version: str = None, depends_on: Optional[List[str]] = None):
        """
        Adds a module to be load from the module system. If this module (same name) was already added, this will
        only override the version, or do nothing.
        This is just like adding a command "module load <name>",
        just for more convince on systems with a module system in place.
        :param name: The name of the module to load.
        :param version: The version of the module. If not give it will be loaded without a specific version,
        therefore it will be the default version of the module system.
        :param depends_on: List of module names the modules depends on. These will be loaded bevor this module.
        :return: void.
        """
        module = _Module(name, version, depends_on)
        try:
            module.check_dependency_conflicts(self.__modules)
        except ModuleDependencyConflict as e:
            print(e)
            raise RuntimeError(e)
        self.__modules.append(module)

    def add_command(self, command: str) -> None:
        """
        Adds a command to run from inside the sbatch job. These are the actual working commands,
        not the SLURM config comments.
        :param command: The command to add.
        :return: void.
        """
        self.__commands.append(command)

    def clear_commands(self) -> None:
        """
        Clears commands.
        :return: void.
        """
        self.__commands.clear()

    def add_bash_script(self, script_path: str) -> None:
        """
        If you pre-scripted your execution in a bash script for local execution,
        you can use this method to add all commands from it to your SLURMConfiguration.
        :param script_path: Path to the script.
        :return: void.
        """
        try:
            with open(script_path, "r") as f:
                for line in f.readlines():
                    if line[:-1] == "":
                        continue
                    if line.startswith("#"):
                        continue
                    self.add_command(line)
        except FileNotFoundError as e:
            raise ScriptNotFoundException("You tried to add commands from a "
                                          f"bash script, but the script could not be found: {e}.")

    def __sort_module_loads(self) -> None:
        """
        Sorts the module loads, by dependencies.
        :return: void.
        """
        modules_sorted = []
        # move modules without dependencies to the front
        for module in self.__modules:
            if not module.depends_on:
                self.__modules.remove(module)
                modules_sorted.append(module)
        modules_with_deps = sorted(self.__modules, key=lambda mod: len(mod.depends_on))
        # tries should not exceed (len(modules_with_deps) * (len(modules_with_deps)-1)) / 2.
        # This would resemble all possible combinations. If at that point, some module is still not sorted,
        # we should raise an error.
        tries = 0
        while len(modules_with_deps) > 0:
            module = modules_with_deps.pop(0)
            dependencies_fulfilled = True
            for dependency in module.depends_on:
                if dependency not in [mod.name for mod in modules_sorted] and \
                        dependency not in [mod.name+"/"+mod.version if mod.version is not None else "NO_VERSION" for mod in modules_sorted]:
                    dependencies_fulfilled = False
                    # put it back at the end of the list, to check later
                    modules_with_deps.append(module)
                    tries = tries + 1
            if dependencies_fulfilled:
                modules_sorted.append(module)
            # sanity check for tries
            if tries >= (len(self.__modules) * (len(self.__modules) - 1)) / 2:
                conflicts_on = [f"{mod.name} (depends on {mod.depends_on})" if mod.version is None else
                                f"{mod.name}/{mod.version} (depends on {mod.depends_on})" for mod in modules_with_deps]
                raise ModuleDependencyConflict(f"Modules could not be sorted in a way they do not conflict each other "
                                               f"or some module dependencies cannot be fulfilled. "
                                               f"Modules that cannot be sorted in are: {conflicts_on}.")
        self.__modules = modules_sorted

    def write_slurm_script(self) -> None:
        """
        Saves the SLURM script to the specified location.
        This will also check the stdout and stderr directories if set, and add the helper echo commands if set.
        :return: void.
        """
        try:
            self.__sort_module_loads()
        except ModuleDependencyConflict as e:
            print(e)
            raise RuntimeError(f"Conflict while module sorting: {e}")
        if self.__echo_job_task_info:
            self.__commands.insert(0, "echo [SlurmConfiguration] This is job ID $SLURM_ARRAY_JOB_ID")
            if self.__job_array:
                self.__commands.insert(1,
                                       "echo [SlurmConfiguration] This is task  $SLURM_ARRAY_TASK_ID (configuration: " + self.__job_array + ")")
            self.__commands.insert(0, "echo '[SlurmConfiguration] STARTING.'")
            self.__commands.append("echo '[SlurmConfiguration] FINISHED.'")
        try:
            with open(self.__slurm_script_file+".sh", "w") as f:

                # write header
                f.write(f"#!{self.__shell}\n\n")
                f.write(f"### SLURM Script for Job: {self.__job_name} ###\n")
                f.write("### autogenerated by SlurmConfiguration\n\n")

                # write SLURM settings
                f.write("### SYSTEM SETTINGS ###\n")
                f.write(f"### Environment: {self.__shell}.\n")
                f.write(f"### Uses 'module' system: {self.__uses_module_system}.\n")

                # mail settings
                f.write("\n### MAIL SETTINGS ###\n")
                f.write(f"### Mail Address: {self.__mail_address}.\n")
                f.write(f"### Selected Mail Types: {self.__mail_types}.\n")

                # SLURM accounting settings
                f.write("\n### USER SETTINGS ###\n")
                if self.__reservation or self.__account or self.__partition:
                    if self.__reservation:
                        f.write(f"### Reservation: {self.__reservation}.\n")
                    if self.__account:
                        f.write(f"### Account: {self.__account}.\n")
                    if self.__partition:
                        f.write(f"### Partition: {self.__partition}.\n")
                else:
                    f.write("### Reservation, Account and Partition not specified.\n")

                # SLURM settings
                f.write("\n\n### SLURM SCRIPT ###\n\n")
                if self.__account:
                    f.write(f"#SBATCH --account={self.__account}\n")
                if self.__reservation:
                    f.write(f"#SBATCH --reservation={self.__reservation}\n")
                if self.__partition:
                    f.write(f"#SBATCH --partition={self.__partition}\n\n")

                f.write("### Job information:\n")
                f.write(f"#SBATCH --job-name='{self.__job_name}'\n")
                if self.__job_array:
                    f.write(f"#SBATCH --error={self.__std_err_path}.%A_%a\n")
                    f.write(f"#SBATCH --output={self.__std_out_path}.%A_%a\n")
                else:
                    f.write(f"#SBATCH --error={self.__std_err_path}.%j\n")
                    f.write(f"#SBATCH --output={self.__std_out_path}.%j\n")
                f.write(f"#SBATCH --time={self.__time_str}\n")
                # TODO Add job array! If job-array is in place, name the out and err files with the id?

                if self.__dependencies:
                    for dependency in self.__dependencies:
                        f.write(f"#SBATCH --dependency={dependency}\n")

                f.write("\n### Mail settings:\n")
                if self.__mail_types:
                    f.write(f"#SBATCH --mail-user={self.__mail_address}\n")
                    f.write(f"#SBATCH --mail-type={self.__mail_types}\n")
                else:
                    f.write("### No mail settings were specified.\n")

                f.write("\n### Compute settings:\n")
                f.write(f"#SBATCH --mem-per-cpu={self.__mem_per_cpu}\n")
                f.write(f"#SBATCH --ntasks={self.__number_of_cores_per_task}\n")
                f.write(f"#SBATCH --cpus-per-task={self.__number_of_tasks}\n")
                if self.__exclusive:
                    f.write("#SBATCH --exclusive\n")
                f.write(f"#SBATCH --cpu-freq={self.__cpu_frequency_str}\n")

                f.write("\n### MODULE SYSTEM ###\n")
                if self.__uses_module_system:
                    if self.__purge_modules_at_start:
                        f.write("module purge\n")
                    for module in self.__modules:
                        if module.version:
                            f.write(f"module load {module.name}/{module.version}\n")
                        else:
                            f.write(f"module load {module.name}\n")
                    f.write("\n")
                else:
                    f.write("### Module System not in use.\n")

                f.write("\n### COMMANDS FOR EXECUTION ###\n")
                f.write("\nset -u\n\n")
                for command in self.__commands:
                    f.write(f"{command}\n")

        except FileNotFoundError as e:
            print(e)
            raise RuntimeError(f"Slurm script file cannot be found or created: {e}.")

    def sbatch(self) -> int:
        """
        Saves the SLURM script to the file and submits the job on the system via "sbatch"-command.
        Synchron version: It will just submit the job, you have to care about everything else.
        :return: The job id.
        """
        # check dirs: Just check for dirs, file may not be there, but slurm will create it
        # as long as the directory is in place
        err_dir = "/".join(self.__std_err_path.split("/")[:-1])
        out_dir = "/".join(self.__std_out_path.split("/")[:-1])
        if not os.path.isdir(err_dir):
            res = subprocess.run(["mkdir", "-p", err_dir])
            if not res.returncode == 0:
                raise CommandExecutionException(f"mkdir -p {err_dir}")
        if not os.path.isdir(out_dir):
            res = subprocess.run(["mkdir", "-p", out_dir])
            if not res.returncode == 0:
                raise CommandExecutionException(f"mkdir -p {out_dir}")

        # sbatch it
        try:
            res = subprocess.run(["sbatch", self.__slurm_script_file+".sh"], stdout=subprocess.PIPE, executable="/bin/bash")
            if res.returncode != 0:
                raise CommandExecutionException(f"sbatch {self.__slurm_script_file}")
            res = res.stdout.decode("utf-8")
            res = res.splitlines()[0].split("batch job ")[1]
            res = int(res.split(" ")[0])
            return res
        except FileNotFoundError:
            raise CommandExecutionException(f"sbatch {self.__slurm_script_file}", non_zero=False, invalid=True)

    def __check_squeue(self, job_id: int) -> bool:
        """
        Checks the output of the "squeue" command and returns whether job with that id is completed or not.
        :param job_id: The job id to find status for.
        :return: True if job is completed, false otherwise.
        """
        # example squeue output
        #      JOBID PARTITION     NAME     USER    STATE       TIME TIME_LIMIT PRIORITY    NODES NODELIST(REASON)
        #   28712165 kurs00054 JOB_ISSM jo83xafu  RUNNING       0:24      15:00 13054           1 mpsc0154
        sq = subprocess.Popen(["squeue"], stdout=subprocess.PIPE)
        res = subprocess.run(["grep", str(job_id)], stdin=sq.stdout, stdout=subprocess.PIPE)
        if res.stdout.decode("utf-8") != "":
            return True
        else:
            return False

    def wait(self, job_id):
        """
        Wait for the SLURM job to finish execution.
        :return: It will return the paths to the result files of the job.
        """
        while not self.__check_squeue(job_id):
            time.sleep(60)
        return self.__std_out_path, self.__std_err_path
