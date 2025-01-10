const requestIntervalDefault = 30 * 1000; // Default value for status requests (30 seconds)
const sleepIntervalDefault = 10 * 60 * 1000; // Default value for sleep mode (10 minutes)
let requestInterval = requestIntervalDefault;
let sleepInterval = sleepIntervalDefault;
let statusInterval;
let sleepTimer;

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
            $(`#${key}`).fadeOut(200, function () {
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
        success: function (data) {
            if (data) {
                updateContent(data);
                setRequestInterval(data["requestInterval"]); // Update status request interval
                setSleepInterval(data["sleepInterval"]); // Update sleep interval if provided
            }
        },
        error: function (errorMsg) {
            console.log(errorMsg);
        }
    });
}

// Set status request interval
function setRequestInterval(val) {
    if (val !== undefined && val !== null) {
        if (val !=requestInterval){
            requestInterval = val;
            clearInterval(statusInterval);
            statusInterval = setInterval(getStatus, requestInterval);
        }
    }
}
// Reset sleep timer
function resetRequestInterval() {
    clearInterval(statusInterval);
    statusInterval = setInterval(getStatus, requestInterval);
}

// Set sleep interval 
function setSleepInterval(val) {
    if (val !== undefined && val !== null) {
        if (sleepInterval != val)
        {   
            sleepInterval = val; // Use the value from the server
            resetSleepTimer(); // Reset the sleep timer with the new interval
        }
    } else {
        console.log("Got invalid value, use default 'sleepInterval'.")
    }
    
}

// Reset sleep timer
function resetSleepTimer() {
    clearTimeout(sleepTimer);
    sleepTimer = setTimeout(enterSleepMode, sleepInterval); // Use dynamic sleepInterval
}


// Enter sleep mode
function enterSleepMode() {
    clearInterval(statusInterval);
    const statusContent = document.getElementById('status_content');
    const overlay = document.getElementById('overlay');
    const sleepModal = document.getElementById('sleepModal');

    statusContent.style.filter = 'blur(10px)';
    overlay.style.opacity = '1';
    sleepModal.style.display = 'block';
}

// Resume requests
function resumeRequests() {
    const statusContent = document.getElementById('status_content');
    const overlay = document.getElementById('overlay');
    const sleepModal = document.getElementById('sleepModal');

    statusContent.style.filter = 'blur(0)';
    overlay.style.opacity = '0';
    sleepModal.style.display = 'none';

    setStatusInterval(interval);
    resetSleepTimer();
}


// Initialize
$(function () {
    setRequestInterval(requestInterval);
    getStatus();
    resetSleepTimer();
});

// Event listener for resume button
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('resumeButton').addEventListener('click', resumeRequests);
});