import os
import shutil
import subprocess as sp
import sys
import datetime
import dateutil.parser as dtparser
import re
import numpy as np
from typing import Dict, Tuple, List

# Check Python version
if not sys.version_info >= (3, 7, 0):
    raise Exception("Python>=3.7.0 is required.")


# Determines plantform
class PlatformError(Exception):
    pass


if not sys.platform == "linux":
    raise PlatformError("Only applicable to Linux.")


def _safe_int(v):
    try:
        return int(v)
    except Exception as e:
        if ("N/A" in str(v)) or v is None:
            return np.nan
        print(e)
        return -1


def _safe_float(v):
    try:
        return float(v)
    except Exception as e:
        if "N/A" in str(v) or v is None:
            return np.nan
        print(e)
        return -1.0


def _strftimedelta(td: datetime.timedelta) -> str:
    """Convert `timedelta` to `str`.
    Representation: `[{days}d-]{hours}:{minutes}:{seconds}`
    """
    _secs = int(td.seconds + td.microseconds // 1e6)
    days = td.days
    hours = int(_secs // 3600)
    minutes = int(_secs % 3600 / 60)
    seconds = _secs % 60
    days_part = f"{days}d-" if days > 0 else ""
    hms_part = (
        str(hours).rjust(2, "0")
        + ":"
        + str(minutes).rjust(2, "0")
        + ":"
        + str(seconds).rjust(2, "0")
    )
    deltastr = days_part + hms_part
    return deltastr


class _GProcess:
    def __init__(
        self,
        pid,
        gpu_index,
        process_name,
        proc_start_time,
        proc_running_time,
        gpu_memory_used,
        main_memory_used,
        pid_in_container,
        container_name,
        command,
        **kwargs,
    ):
        self.pid = _safe_int(pid)
        self.gpu_index = _safe_int(gpu_index)
        self.process_name = str(process_name)
        self.proc_start_time = str(proc_start_time)
        self.proc_running_time = str(proc_running_time)
        self.gpu_memory_used = _safe_int(gpu_memory_used)
        self.main_memory_used = _safe_int(main_memory_used)
        self.pid_in_container = _safe_int(pid_in_container)
        self.container_name = str(container_name)
        self.command = str(command)

        if np.isnan(self.pid_in_container):
            self.pid_in_container = "-"

    def __str__(self):
        s = "|+" + "-"* 98
        for k,v in self.__dict__.items():
            s += f"\n|| {k}: {v}"
        s += "\n|+" + "-"* 98
        return s

class _GPU:
    def __init__(
        self,
        index,
        uuid,
        name,
        driver_version,
        compute_capability,
        utilization_gpu,
        utilization_memory,
        memory_total,
        memory_used,
        memory_free,
        power_limit,
        power_draw,
        display_active,
        display_mode,
        temperature_gpu,
        temperature_memory,
        fan_speed,
        pcie_width_current,
        pcie_gen_current,
        cuda_version,
        processes={},
        **kwargs,
    ):

        self.index = _safe_int(index)
        self.uuid = str(uuid)
        self.name = str(name)
        self.driver_version = str(driver_version)
        self.compute_capability = _safe_float(compute_capability)
        self.utilization_gpu = _safe_int(utilization_gpu)
        self.utilization_memory = _safe_int(utilization_memory)
        self.memory_total = _safe_int(memory_total)
        self.memory_used = _safe_int(memory_used)
        self.memory_free = _safe_int(memory_free)
        self.power_limit = round(_safe_float(power_limit),1)
        self.power_draw = round(_safe_float(power_draw),1)
        self.display_active = str(display_active)
        self.display_mode = str(display_mode)
        self.temperature_gpu = _safe_int(temperature_gpu)
        self.temperature_memory = _safe_int(temperature_memory)
        self.fan_speed = _safe_int(fan_speed)
        self.pcie_width_current = _safe_int(pcie_width_current)
        self.pcie_gen_current = _safe_int(pcie_gen_current)
        self.cuda_version = str(cuda_version)
        self.processes = {
            k: _GProcess(gpu_index=self.index, **v) for k, v in processes.items()
        }  

    def __str__(self):
        s = "\n+" + "="*100
        for k,v in self.__dict__.items():
            if isinstance(v,dict):
                s += f"\n| {k}:\n" + "\n".join([f"{vv}" for vv in v.values()])
            else:
                s += f"\n| {k}: {v}"
        s += "\n+" + "="*100
        return s




class CommandNotFoundError(Exception):
    pass

def get_gpus()->Tuple[dict,list]:
    command_nvidia_smi = shutil.which("nvidia-smi")

    if command_nvidia_smi is None:
        raise CommandNotFoundError("`nvidia-smi` was not found.")

    err_infos = []

    # Get CUDA Version
    try:
        stdout = sp.check_output([command_nvidia_smi, "--query"])
        cuda_info = stdout.decode("utf-8")
        cuda_version = re.findall(
            "CUDA Version.*?: ([0-9]+\.[0-9]+)", cuda_info, re.M | re.I
        )[0]
    except Exception as e:
        err_infos.append(str(e))
        cuda_version = ""

    # GPUs
    gpus_dict: Dict[str, _GPU] = {}

    # Query GPU info
    query_format = "--format=csv,noheader,nounits"
    gpu_query_fields = {
        "index": "index",
        "uuid": "uuid",
        "name": "name",
        "driver_version": "driver_version",
        "compute_capability": "compute_cap",
        "utilization_gpu": "utilization.gpu",
        "utilization_memory": "utilization.memory",
        "memory_total": "memory.total",
        "memory_used": "memory.used",
        "memory_free": "memory.free",
        "power_limit": "power.limit",
        "power_draw": "power.draw",
        "display_active": "display_active",
        "display_mode": "display_mode",
        "temperature_gpu": "temperature.gpu",
        "temperature_memory": "temperature.memory",
        "fan_speed": "fan.speed",
        "pcie_width_current": "pcie.link.width.current",
        "pcie_gen_current": "pcie.link.gen.gpucurrent",
    }

    try:
        stdout = sp.check_output(
            [
                command_nvidia_smi,
                f"--query-gpu={','.join(gpu_query_fields.values())}",
                query_format,
            ]
        )
        gpu_info = stdout.decode("utf-8")
    except Exception as e:
        err_infos.append(str(e))
        gpu_info = ""

    gpu_info_lines = gpu_info.split(os.linesep)
    gpu_info_lines = list(filter(lambda line: len(line.strip()) > 0, gpu_info_lines))
    for line in gpu_info_lines:
        gpu_vals_dict = {}
        str_vals = line.split(",")
        for gpu_qurey_name, str_val in zip(gpu_query_fields.keys(), str_vals):
            gpu_vals_dict[gpu_qurey_name] = str_val.strip()
        uuid = gpu_vals_dict["uuid"]
        gpus_dict[uuid] = gpu_vals_dict

    # Query GPU-Process Info
    for uuid in gpus_dict:
        gpus_dict[uuid]["processes"] = {}

    proc_query_fields = {
        "uuid": "gpu_uuid",
        "pid": "pid",
        "process_name": "process_name",
        "gpu_memory_used": "used_memory",
    }

    # Get processes on GPUs
    try:
        stdout = sp.check_output(
            [
                command_nvidia_smi,
                f"--query-compute-apps={','.join(proc_query_fields.values())}",
                query_format,
            ]
        )
        proc_info = stdout.decode("utf-8")
    except Exception as e:
        err_infos.append(str(e))
        proc_info = ""

    proc_info_lines = proc_info.split(os.linesep)
    proc_info_lines = list(filter(lambda line: len(line.strip()) > 0, proc_info_lines))
    for line in proc_info_lines:
        proc_vals_dict = {}
        str_vals = line.split(",")
        for proc_qurey_name, str_val in zip(proc_query_fields.keys(), str_vals):
            proc_vals_dict[proc_qurey_name] = str_val.strip()

        uuid = proc_vals_dict["uuid"]
        pid = proc_vals_dict["pid"]

        # Get PID info
        container_id = container_name = main_memory_used = pid_in_container = (
            proc_cmd
        ) = proc_start_time_str = proc_running_time_str = None
        # Container ID
        try:
            stdout = sp.check_output(["cat", f"/proc/{pid}/cgroup"])
            proc_cgroup = stdout.decode("utf-8")
            container_id = re.findall(
                ".*docker-([a-f0-9]+)\.scope.*", proc_cgroup, re.M
            )[0]
        except Exception as e:
            err_infos.append(str(e))

        # Process start time / running time
        try:
            stdout = sp.check_output(
                ["ps", "-o", "etimes=", "-o", "start=", "-p", f"{pid}"]
            )
            proc_time_str = stdout.decode("utf-8").strip()
            split_idx = proc_time_str.find(" ")
            proc_running_time_sec_str, proc_start_time_str = (
                proc_time_str[:split_idx],
                proc_time_str[split_idx:],
            )
            proc_running_time_sec = int(proc_running_time_sec_str)
            proc_running_time_td = datetime.timedelta(seconds=proc_running_time_sec)
            proc_running_time_str = _strftimedelta(proc_running_time_td)
            proc_start_time_dt = dtparser.parse(proc_start_time_str)
            proc_start_time_str = proc_start_time_dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            err_infos.append(str(e))

        # Container Name
        if container_id is not None:
            try:
                stdout = sp.check_output(
                    ["docker", "inspect", "--format", "{{.Name}}", container_id]
                )
                container_name = stdout.decode("utf-8")
                container_name = container_name.strip("\n").strip("/")
            except Exception as e:
                err_infos.append(str(e))
        else:
            container_name = "<host>"

        try:
            stdout = sp.check_output(["cat", f"/proc/{pid}/status"])
            proc_status = stdout.decode("utf-8")
        except Exception as e:
            err_infos.append(str(e))

        if proc_status is not None:
            if container_id is not None:
                # PID in Container
                try:
                    _, pid_in_container = re.findall(
                        "NSpid:.*?([0-9]+).*?([0-9]+)", proc_status, re.M | re.I
                    )[0]
                except Exception as e:
                    err_infos.append(str(e))
            else:
                pid_in_container = None

            # Main Memory Usage
            try:
                main_memory_used_kb_str = re.findall(
                    "VmRSS:.*?([0-9]+) kB", proc_status, re.M | re.I
                )[0]
                main_memory_used = _safe_int(
                    _safe_int(main_memory_used_kb_str) / 1024
                )
            except Exception as e:
                err_infos.append(str(e))

        try:
            stdout = sp.check_output(["cat", f"/proc/{pid}/cmdline"])
            proc_cmd = stdout.decode("utf-8").replace("\x00", " ").strip()
        except Exception as e:
            err_infos.append(str(e))

        proc_vals_dict["container_name"] = container_name
        proc_vals_dict["proc_start_time"] = proc_start_time_str
        proc_vals_dict["proc_running_time"] = proc_running_time_str
        proc_vals_dict["pid_in_container"] = pid_in_container
        proc_vals_dict["main_memory_used"] = main_memory_used
        proc_vals_dict["command"] = proc_cmd
        gpus_dict[uuid]["processes"][pid] = proc_vals_dict

    gpu_objects_dict = {
        uuid: _GPU(cuda_version=cuda_version, **fields)
        for uuid, fields in gpus_dict.items()
    }

    return gpu_objects_dict, err_infos


def test_inspect_gpus(gpu_objects_dict):
    dt = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    info = f" {dt}\n"
    for k, v in gpu_objects_dict.items():
        info += str(v) + "\n"
    print(info)


if __name__ == "__main__":
    gpu_objects_dict, err_infos = get_gpus()
    test_inspect_gpus(gpu_objects_dict)
