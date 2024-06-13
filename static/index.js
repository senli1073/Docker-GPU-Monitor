var interval = 30000;
var statusInterval;

function hide_loader() {
    document.getElementById("main_title_loading").style.display = "none";
    document.getElementById("main_title_text").style.display = "block"; 
}

var init_flag = true;
var content_keys = ["datetime_str", "main_content"];
function update_content(data) {
    if (init_flag) {
        content_keys.forEach(key => {
            $(`#${key}`).fadeOut(200, function() {
                $(this).html(data[key]).fadeIn(300);
            });
        });
        hide_loader();
        init_flag = false;
    } else {
        content_keys.forEach(key => {
            document.getElementById(key).innerHTML = data[key];
        });
    }
}

function get_status() {
    $.ajax({
        type: "post",
        async: true,
        url: "/status",
        dataType: "json",
        success: function(data) {
            if (data) {
                update_content(data);
                set_status_interval(data["interval"]);
            }
        },
        error: function(errorMsg) {
            console.log(errorMsg);
        }
    });
}

function set_status_interval(val) {
    if (val!=interval){
        interval = val;
        if (statusInterval) {
            clearInterval(statusInterval);
        }
        statusInterval = setInterval(get_status, interval);
    }
    
}

$(function() {
    get_status();
});