$.fx.speeds._default = 300;
$.fn.childform = function(name) {
	this.addClass('childform-content ui-widget-content ui-helper-reset ui-corner-bottom childform');
	this.before('<div class="childform ui-widget ui-helper-reset">');
	this.before('<div style="height: 19px" class="childform childform-header ui-widget-header ui-corner-top ui-helper-clearfix">'
			+ '<span style="position:relative; top:-2px; float: left">'
			+ name
			+ '</span></div>');
	this.after('</div">');
	return this;
}
$.fn.toolbarButton = function(name, clickfunc, icon, takeRow) {
	var id = this.selector.slice(1);
	if($("#t_" + id).length != 1) {
		alert('Can not add button "' + name + '" because the grid "' + id + '" does not have a toolbar.');
	} else {
		$("#t_" + id).css('height','30px');
		var btnid = 'toolbar_' + id + '_' + ($('button',$("#t_" + id)).length+1);
		$("#t_" + id).append('<button id="' + btnid + '" class="toolbarButton">'+name+'</button>');
		$("#"+btnid).button();
		if(clickfunc) {
			if(takeRow) {
				$("#"+btnid).click(function() {
			        var grid = $("#"+id)[0];
					if($('.ui-state-highlight',grid).length == 1) {
						clickfunc($('.ui-state-highlight',grid)[0].id);
					}
				});
			} else {
				$("#"+btnid).click(clickfunc);
			}
		}
		if(icon != null && icon != '') {
			$("#"+btnid).button({ icons: {primary:icon}});
		}
	}
	return this;
}
$.fn.linkButton = function(clickfunc, icon) {
	this.each(function() {
		var s = $(this);
		s.addClass('linkButton');
		if(icon != null) {
			var st = s.html();
			s.html('<span style="float: left" class="ui-button-icon-primary ui-icon ' + icon + '"></span><span>' + st + '</span>');
		}
		s.mouseover(function() {s.addClass('linkButton-hover');});
		s.mouseout(function() {s.removeClass('linkButton-hover');});
		if(clickfunc) s.click(clickfunc);
	});
	return this;
}
$.fn.tableGrid = function(url) {
	return this.jqGrid({
		url:url,
		datatype:'json',
		loadtext:'Loading...',
		loadonce:true
	})
	this.each(function() {
		var s = $(this);
		s.addClass('linkButton');
		if(icon != null) {
			var st = s.html();
			s.html('<span style="float: left" class="ui-button-icon-primary ui-icon ' + icon + '"></span><span>' + st + '</span>');
		}
		s.mouseover(function() {s.addClass('linkButton-hover');});
		s.mouseout(function() {s.removeClass('linkButton-hover');});
		if(clickfunc) s.click(clickfunc);
	});
}
$(function() {
		$('#alertSheet').dialog({
			autoOpen: false,
			resizable: false,
			modal: true, height: 160
		});
	});
function messageBox(title, message, func) {
   return ask(title, message, {'OK':func});
}
function errorBox(message) {
   return ask("Error", message, {'OK':null});
}
function askConfirm(title, message, okFunc, cancelFunc) {
	return ask(title, message, {'Cancel':cancelFunc, 'OK':okFunc});
}
function ask(title, message, buttons) {
   $('#alertSheet_text').html(message);
   var dlg = $('#alertSheet');
   dlg.dialog({title:title});
   dlg.dialog('open');
   var html = '<br /><br /><div style="width: 100%; text-align: right">';
   var idx = 0;
   for(var btn in buttons) {
	   var btnid = "alertSheet_btn_"+idx;
	   html += '&nbsp;<button style="width: 80px" id="'+btnid+'">' + btn+'</button>';
	   idx++;
   }
   html += "</div>";
   $('#alertSheet_text').append(html);
   idx = 0;
   for(var btn in buttons) {
	   var btnid = "alertSheet_btn_"+idx;
	   if(buttons[btn]) {
		   $('#' + btnid).button().click(buttons[btn]).click(function() {
			   dlg.dialog({beforeclose: null});
			   dlg.dialog('close');
		   });
		   if(idx == 0) {
			   dlg.dialog({beforeclose: buttons[btn]});
		   }
	   } else {
		   $('#' + btnid).button().click(function() {
			   dlg.dialog('close');
		   });
	   }
	   idx++;
   }
   return false;
}

function openForm(href, real_href) {
	if(!parent || parent == self) window.location.href = href;
	else parent.opentab(href, real_href);
}
