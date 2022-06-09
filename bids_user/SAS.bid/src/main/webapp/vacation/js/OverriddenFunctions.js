// Add custom class for css formatting
js.crewweb.warp.widgets.BidPropertyViewExt = Ext.sequence(js.crewweb.warp.dialog.BidPropertyView.prototype, 'initComponent', function(config, bidProperty) {
	this.cls = this.cls + " " + 'bid-property-' + this.bidProperty.type;
	this.label.cls = this.label.cls + " " + "bid-property-label-" + this.bidProperty.type;
});

//Increase the bid receipt window width
js.crewweb.warp.widgets.PrintWindowExt = Ext.sequence(js.crewweb.warp.jsbase.ui.PrintWindow.prototype, 'initComponent', function(config) {
	this.width = 850;
});


js.crewweb.warp.widgets.DetailedCrewInfoViewExt = Ext.sequence(js.vacation.crewinfo.DetailedCrewInfoView.prototype, 'initComponent', function(config) {
	this.bodyCssClass = 'detailed-crew-info-body';
});