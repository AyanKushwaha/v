function enableAutomaticLogoutOnSessionTimout() {

    // get server time and calulcate client time offset
    portalPing(function(data, status, jqXHR) {
        if (status == "success") {
            calcClientOffset(data.serverTime);
            checkSession();
        }
    }, function(response, textStatus, jqXHR) {
        return; // can not enable the auto logout without server time
    });

}

// SessionTimeout cookie check
function getCookie(c_name) {
    var c_value = document.cookie;
    var c_start = c_value.indexOf(" " + c_name + "=");
    if (c_start == -1) {
        c_start = c_value.indexOf(c_name + "=");
    }
    if (c_start == -1) {
        c_value = null;
    } else {
        c_start = c_value.indexOf("=", c_start) + 1;
        var c_end = c_value.indexOf(";", c_start);
        if (c_end == -1) {
            c_end = c_value.length;
        }
        c_value = unescape(c_value.substring(c_start, c_end));
    }
    return c_value;
}

// sets window.clientTimeOffset
function calcClientOffset(currentServerTime) {
    var serverTime = currentServerTime == null ? null : Math.abs(currentServerTime);
    var clientTimeOffset = (new Date()).getTime() - serverTime;
    window.clientTimeOffset = clientTimeOffset;
}

function checkSession() {
        //setTimeout(showAutologoutDialog, 30000);
    }


