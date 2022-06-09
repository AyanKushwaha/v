var PORTALCONTEXT = function (pathName) {
	var CONTEXTPATH = "sas";
    var fullPathNameArray = pathName.split('/');
    var pathContextIndex = fullPathNameArray.lastIndexOf(CONTEXTPATH);
    var pathNameArray = fullPathNameArray.slice(0,pathContextIndex + 1);
    var path = pathNameArray.join("/");
    return path;
}