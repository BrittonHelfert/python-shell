import subprocess

from .types import BackgroundJob, ParsedCommand

assigned_nums: set[int] = set()
background_jobs: list[BackgroundJob] = []


def get_next_free_background_num() -> int:
    res = 1
    while res in assigned_nums:
        res += 1
    return res


def list_jobs() -> None:
    for job in background_jobs:
        status = "Running" + " " * 17 if job.proc.poll() is None else "Done" + " " * 20
        print(f"[{job.num}]{job.marker}  {status}  {job.command}")
    # remove completed jobs
    remove_completed_jobs()


def assign_markers() -> None:
    for i, job in enumerate(background_jobs):
        if i == len(background_jobs) - 1:
            job.marker = "+"
        elif i == len(background_jobs) - 2:
            job.marker = "-"
        else:
            job.marker = " "


def remove_completed_jobs(print_each: bool = False) -> None:
    still_running = []
    for job in background_jobs:
        if job.proc.poll() is not None:
            if print_each:
                print(f"[{job.num}]{job.marker}  Done{' ' * 20}{job.command}")
            assigned_nums.remove(job.num)
        else:
            still_running.append(job)
    background_jobs[:] = still_running
    assign_markers()


def add_job(command: ParsedCommand, proc: subprocess.Popen) -> None:
    job_num = get_next_free_background_num()
    background_jobs.append(
        BackgroundJob(
            proc=proc,
            num=job_num,
            command=command.raw_command,
        )
    )
    print(f"[{job_num}] {proc.pid}")
    assigned_nums.add(job_num)
    assign_markers()
