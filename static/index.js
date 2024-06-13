var interval = 60000;
var statusInterval;

function get_interval() {
    $.ajax({
        type: "post",
        async: true,
        url: "/interval",
        dataType: "json",
        success: function(data) {
            if (data) {
                interval = data["value"];
                set_status_interval();
            }
        },
        error: function(errorMsg) {
            console.log(errorMsg);
        }
    });
}

function get_status() {
    $.ajax({
        type: "post",
        async: true,
        url: "/status",
        dataType: "text",
        success: function(data) {
            if (data) {
                var contentContainer = document.getElementById('status_content');
                contentContainer.innerHTML = data;
            }
        },
        error: function(errorMsg) {
            console.log(errorMsg);
        }
    });
}

function set_status_interval() {
    if (statusInterval) {
        clearInterval(statusInterval);
    }
    statusInterval = setInterval(get_status, interval);
}

$(function() {
    get_interval();
    get_status();
    set_status_interval();
});