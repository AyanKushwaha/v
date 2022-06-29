
var PortalLogo  = {
		setPortalLogo: function() {
			this.portalGetLogo( function(data, status, jqXHR) {
		    	if (status == "success") {
				var fullPathNameArray = document.location.pathname.split('/');
				var pathContextIndex = fullPathNameArray.lastIndexOf("sas");
				var pathNameArray = fullPathNameArray.slice(0,pathContextIndex + 1);
				var portalContextPath = pathNameArray.join("/");
				//var portalContextPath = PORTALCONTEXT(document.location.pathname);
				var p = portalContextPath.split("/");
				var pathName = p.slice(0, p.length -1);
		    		$("#logo").css('background-image', 'url('+pathName.join("/") + data['logo-img-url']+')');
		    	}
			}, function (response, textStatus, jqXHR){
				alert("Error: could not get logo ");
			});
		},
		
		portalGetLogo: function (callbackSuccess, callbackFail) {
			var restData= {
					url: RESTSERVICE_CONTEXTPATH() + "/portal/uisupport/logo",
					type: "get"
			};
			
			portalRestCall(restData, callbackSuccess, callbackFail);
		}
};
