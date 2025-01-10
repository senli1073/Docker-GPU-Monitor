
const FRONTEND_VERSION = '2.0.3';

const requestIntervalDefault = 30 * 1000; // Default value for status requests (30 seconds)
const sleepIntervalDefault = 10 * 60 * 1000; // Default value for sleep mode (10 minutes)
let requestInterval = requestIntervalDefault;
let sleepInterval = sleepIntervalDefault;

let statusInterval; // Interval object
let sleepTimer; // Timer object

// Initializing
let initFlag = true

// Loader
let loadingFlag = true;
function showLoader() {
    $("#main_title_text").fadeOut(200, function () {
        $(this).html("Loading Data ...").fadeIn(300);
    });
    $("#main_content").fadeOut(200, function () {
        $(this).html("");
    });
    document.getElementById("loader").style.display = "block";
    loadingFlag = true;
}
function hideLoader() {
    document.getElementById("loader").style.display = "none";
    loadingFlag = false;
}

// Elemtent IDs
const contentKeys = ["main_title_text","datetime_str", "main_content"];

// Update contents 
function updateContents(data) {
    contentKeys.forEach(key => {
        document.getElementById(key).innerHTML = data[key];
    });
}
function updateContentsWithFade(data) {
    contentKeys.forEach(key => {
        $(`#${key}`).fadeOut(200, function () {
            $(this).html(data[key]).fadeIn(300);
        });
    });
}

// Update GPU info and Proc info
function updateGPUStatus(data) {
    // Initialize
    if (loadingFlag) {
        updateContentsWithFade(data);
    } else {
        // Keep the scroll bar in its original position after updating data
        const scroll_gpu_pos = document.getElementById("scroll_gpu").scrollLeft;
        const scroll_proc_pos = document.getElementById("scroll_proc").scrollLeft;
        // Update HTML
        updateContents(data);
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
        data: { version: FRONTEND_VERSION },
        dataType: "json",
        success: function (data) {
            if (data) {
                if (data["expired"]){
                    updateContentsWithFade(data);
                    clearInterval(statusInterval);
                } else {
                    updateGPUStatus(data);
                    setRequestInterval(data["request_interval"]); // Update status request interval
                    setSleepInterval(data["sleep_interval"]); // Update sleep interval if provided
                }
                hideLoader();
            } else {
                showLoader();
            }
        },
        error: function (errorMsg) {
            console.log(errorMsg);
            showLoader();
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
    } else {
        console.log("Got invalid value, use default value of 'requestInterval'.")
        requestInterval = requestIntervalDefault;
        resetRequestInterval();
    }
}

// Reset sleep timer
function resetRequestInterval() {
    clearInterval(statusInterval);
    statusInterval = setInterval(getStatus, requestInterval);
    getStatus();
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
        console.log("Got invalid value, use default value of 'sleepInterval'.")
        sleepInterval = sleepIntervalDefault;
        resetSleepTimer(); 
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

    resetRequestInterval();
    resetSleepTimer();
}

// Initialize
$(function () {
    resetRequestInterval();
    resetSleepTimer();
});

// Event listener for resume button
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('resumeButton').addEventListener('click', resumeRequests);
});