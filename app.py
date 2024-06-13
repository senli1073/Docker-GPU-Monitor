from flask import Flask, render_template
import datetime
import platform
import json
from _inspect_cuda import get_gpus
import config


app = Flask(__name__)

# Host name
_page_title = platform.node()
_main_title = f"{_page_title} GPU Status".upper()


@app.route("/")
def index():
    # Datetime
    dt = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    return render_template(
        "index.html",
        page_title=_page_title,
        ur_text=dt,
        copyright_text=config.conf["copyright_text"],
    )


@app.route("/status", methods=["POST"])
def status():

    # Datetime
    dt = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")

    # Get GPUs
    gpu_objects_dict, err_infos = get_gpus()
    gpu_info_list = list(gpu_objects_dict.values())

    # Driver version
    driver_versions = set([g.driver_version for g in gpu_info_list])
    cuda_versions = set([g.cuda_version for g in gpu_info_list])
    driver_version = (
        driver_versions.pop() if len(driver_versions) == 1 else tuple(driver_versions)
    )
    cuda_version = (
        cuda_versions.pop() if len(cuda_versions) == 1 else tuple(cuda_versions)
    )

    # Processes
    proc_info_list = [p for g in gpu_info_list for p in g.processes.values()]
    for i in range(len(proc_info_list)):
        # Set gloabl index
        proc_info_list[i].global_index = i

    return render_template(
        "status.html",
        main_title=_main_title,
        ur_text=dt,
        driver_version=driver_version,
        cuda_version=cuda_version,
        gpu_info_list=gpu_info_list,
        proc_info_list=proc_info_list,
        err_infos=err_infos,
    )


@app.route("/interval", methods=["POST"])
def interval():
    conf = {"value": config.conf["interval_ms"]}
    return json.dumps(conf)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.conf["port"], debug=True, threaded=True)
