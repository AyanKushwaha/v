// Increase the bid receipt window width
js.crewweb.warp.widgets.PrintWindowExt = Ext.sequence(js.crewweb.warp.jsbase.ui.PrintWindow.prototype, 'initComponent', function(config) {
	this.width = 850;
});

// Add custom class for css formatting
js.crewweb.warp.widgets.BidPropertyViewExt = Ext.sequence(js.crewweb.warp.dialog.BidPropertyView.prototype, 'initComponent' , function(config, bidProperty) {
	this.cls = this.cls + " custom-bidProperty-panel";
	this.cls = this.cls + " " + "custom-" + this.type;
});


// Hide the awarding category tab
js.crewweb.warp.widgets.CareerTab = Ext.sequence(js.crewweb.warp.jmp.awardingType.AwardingTypeView.prototype, 'initComponent' , function(config, configModel) {
	var result = "";
	var type = this.initialConfig.model.selectedRecord.data.name;
	if (this.cls) {
		result = this.cls + "_";
	}
	
	result = result + "CustomCareerTab";
	
	if (type) {
		result = result + "_" + type;
	}
	
	this.cls = result + " ";
});