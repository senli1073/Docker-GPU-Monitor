from flask import Flask, render_template
import datetime
import platform
import json
from _inspect_cuda import get_gpus
import config


app = Flask(__name__)


@app.route("/")
def index():
    # Datetime
    dt_str = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")

    # Host name
    page_title = platform.node()
    main_title = f"{page_title} GPU Status".upper()

    return render_template(
        "index.html",
        page_title=page_title,
        main_title=main_title,
        datetime_str=dt_str,
        copyright_text=config.conf["copyright_text"],
    )


@app.route("/status", methods=["POST"])
def status():

    # Datetime
    dt_str = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")

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

    return_data = {
        "interval": config.conf["interval_ms"],
        "datetime_str": dt_str,
        "main_content" : render_template("status.html",
                                driver_version=driver_version,
                                cuda_version=cuda_version,
                                gpu_info_list=gpu_info_list,
                                proc_info_list=proc_info_list,
                                err_infos=err_infos)
    }

    return json.dumps(return_data)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.conf["port"], debug=True, threaded=True)
