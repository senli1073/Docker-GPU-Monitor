let interval = 30000; //Default value
let statusInterval;

// Hide loader after getting status
function hideLoader() {
    document.getElementById("main_title_loading").style.display = "none";
    document.getElementById("main_title_text").style.display = "block"; 
}

let initFlag = true;
const contentKeys = ["datetime_str", "main_content"];

// Update GPU info and Proc info
function updateContent(data) {
    // Init
    if (initFlag) {
        contentKeys.forEach(key => {
            $(`#${key}`).fadeOut(200, function() {
                $(this).html(data[key]).fadeIn(300);
            });
        });
        hideLoader();
        initFlag = false;
    } else {
        // Keep the scroll bar in its original position after updating data
        const scroll_gpu_pos = document.getElementById("scroll_gpu").scrollLeft;
        const scroll_proc_pos = document.getElementById("scroll_proc").scrollLeft;
        // Update HTML
        contentKeys.forEach(key => {
            document.getElementById(key).innerHTML = data[key];
        });
        // Set pos
        document.getElementById("scroll_gpu").scrollLeft = scroll_gpu_pos;
        document.getElementById("scroll_proc").scrollLeft = scroll_proc_pos;

    }
}

// Request data
function getStatus() {
    $.ajax({
        type: "post",
        async: true,
        url: "/status",
        dataType: "json",
        success: function(data) {
            if (data) {
                updateContent(data);
                setStatusInterval(data["interval"]);
            }
        },
        error: function(errorMsg) {
            console.log(errorMsg);
        }
    });
}

// Set interval
function setStatusInterval(val) {
    if (val!=interval){
        interval = val;
        if (statusInterval) {
            clearInterval(statusInterval);
        }
        statusInterval = setInterval(getStatus, interval);
    }
    
}

$(function() {
    setStatusInterval(interval);
    getStatus();
});

