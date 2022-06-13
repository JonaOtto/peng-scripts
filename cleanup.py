import subprocess
import json
import os

base_dir = "/home/kurse/kurs00054/jo83xafu/issm-output"
res_dir = "RESULTS"
out_dir = "OUT"

if __name__ == "__main__":
    jobids_to_keep = []
    for result_dir in os.listdir(f"{base_dir}/{res_dir}"):
        with open(f"{base_dir}/{res_dir}/{result_dir}/{result_dir}.json", "r") as f:
            jc = json.loads(f.read())
            for job in jc["jobs"].keys():
                jobids_to_keep.append(job)
    for experiment in os.listdir(f"{base_dir}/{out_dir}"):
        if not experiment.split(".", 1)[1] in jobids_to_keep:
            print(f"Deleting {experiment}, it is not part of any result!")
            # subprocess.run(["bash", "-c", f"rm -r {base_dir}/{out_dir}/{experiment}"])
        else:
            print(f"{experiment} will be kept, it is part of an result!")
