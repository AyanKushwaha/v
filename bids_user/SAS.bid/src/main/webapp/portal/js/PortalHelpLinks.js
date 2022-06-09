


function createLink(name, module) {
    var aElement = document.createElement('a');
    aElement.setAttribute("href", "javascript:openHelp(\'" + module + "\')");
    aElement.innerHTML = name;
    return aElement;
}

function initHelpLinks(webApps) {
    if (webApps == null) {
        return;
    }

    var adminLink = createLink('Admin Help', 'admin');
    var ibLink = createLink('Bids Help', 'interbids');

    var help2 = document.getElementById("help-link-2");
    help2.appendChild(ibLink);

    for ( var i = 0 ; i < webApps.length; i++) {
        var webApp = webApps[i];
        if (webApp.id === 'administration') {
            help1 = document.getElementById('help-link-1');
            help1.appendChild(adminLink);
        }  
    }
}


function openHelp(m) {
    var path = document.location.pathname;
    var pathArr = path.split("/");
    var url = '';
    if (!window.location.origin) {
        url = window.location.protocol+"//"+window.location.host + '/' + pathArr[1] + '/' + m + '/help/wwhelp.htm';
    } else {
        url = document.location.origin + '/' + pathArr[1] + '/' + m + '/help/wwhelp.htm';
    }
    window.open(url);
}
