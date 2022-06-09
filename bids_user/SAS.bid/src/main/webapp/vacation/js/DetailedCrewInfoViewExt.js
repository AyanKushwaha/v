
js.crewweb.warp.widgets.DetailedCrewInfoViewExt = Ext.sequence(js.vacation.crewinfo.DetailedCrewInfoView.prototype, 'initComponent', function(config) {
	this.bodyCssClass = 'detailed-crew-info-body';
});

js.crewweb.warp.widgets.capitalFirstLetter = function(string) {
	return string.charAt(0).toUpperCase() + string.slice(1);
}

js.crewweb.warp.widgets.sortdata = function(value) {
	
	var order = {
			'va': 	'1',
			'va1':	'2',
			'f7': 	'3',
			'sum': 	'4'
	}
	
	for (var i=0; i < value.length; i++) {
		if (value[i].name.toLowerCase() === 'balance') {
			value[i].infoEntry.sort(function(val_a,val_b) {
				var a = val_a['name'].toLowerCase(),
				b = val_b['name'].toLowerCase();
				
				o_a = order[a];
				o_b = order[b];
				
				return o_a && o_b ? (o_a < o_b ?  -1 : 1) : (!o_a ? 1 : -1);
				
			});
		}
	}
	return "";
}

