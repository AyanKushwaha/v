/**
 * @class js.ib.widgets.SingleDateWidget
 * @extends js.ib.ui.CWTablePanel
 * @constructor
 * called when a bid dialog containing this widget is created.
 * @param {js.ib.bid.dialog.BidModel} bidModel holds information about the current bid's values and properties. {@link js.ib.bid.dialog.BidModel}
 * @param {js.ib.bid.dialog.BidProperty} bidProperty the current bid property. {@link js.ib.bid.dialog.BidProperty}
 * @param {Object} config contains certain configuration. The attributes from the bid property xml are found in
 *        config.attributes.
 * @param {js.ib.data.DataSourceManager} dataSourceManager used to access data sources if any should be used. {@link js.ib.data.DataSourceManager}
 * @param {js.ib.bid.dialog.BidView} view the view that this widget is displayed in.
 * @param {js.ib.PeriodModel} periodModel used to access period data if needed.{@link js.ib.PeriodModel}
 */
js.ib.widgets.SingleDateWidget = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel) {
	this.bidProperty = bidProperty;
	this.bidModel = bidModel;

    var startValue = Environment.parseDate(bidProperty.get("start"));
    if (!startValue) {
		startValue = bidModel.presets && bidModel.presets.start || new Date();
    }
    
    this.dateFormat = config.attributes.dateFormat ? config.attributes.dateFormat
			: js.ib.Environment.DATEFORMAT;
    
    this.altDateFormats = config.attributes.altDateFormats ? config.attributes.altDateFormats
			: 'm/d/Y|n/j/Y|n/j/y|m/j/y|n/d/y|m/j/Y|n/d/Y|m-d-y|m-d-Y|m/d|m-d|md|mdy|mdY|d|Y-m-d|dMY';
    
    var invalidTextMessage = "{0} is not a valid date - valid format is ddmmmyy";

	this.startDateField = new js.ib.ui.CWDateField({
        id: this.id + "_start",
        hideLabel: true,
		format : this.dateFormat,
		altFormats : this.altDateFormats,
		value: startValue,
        name: "start",
		ufnEnabled: false,
		enableKeyEvents: true,
		startDay: 1,
		showToday: false,
		invalidText: invalidTextMessage
	});
	
	this.startDateField.on("cwSelect", this._setValue, this);
	this.startDateField.on('keyup', this._setValue, this);
	this.startDateField.on("cwSelect", this.isValid, this);
	
	js.ib.widgets.SingleDateWidget.superclass.constructor.call(this, 4, [{ colspan: 4, item: this.startDateField }]);
};

Ext.extend(js.ib.widgets.SingleDateWidget, js.ib.ui.CWTablePanel, {

	_setValue: function() {
        var startDate = this._getDateValue(this.startDateField);
		var startValue = startDate ? startDate + " 00:00" : "";

        this.bidProperty.set("startDate", startDate, false);
        this.bidProperty.set("start", startValue, false);
        this.bidModel;
	},
	
	_getDateValue: function(component) {
	    var value = component.getValue();
	    return value.format ? Environment.formatISODate(value) : "";
	},

    clear: function() {
    	this.startDateField.clear();
    },
    
    getFocusComponentId: function() {
    	return this.startDateField.id;
    },
    
    focus: function() {
    	Ext.getCmp(this.getFocusComponentId()).focus();
    },
    
    isValid: function() {
    	var result = true;
    	
    	var value = this.startDateField.getValue()
    	
    	if (!value && value === "") {
    		result = false;
    	} else if (!this.startDateField.isValid()) {
    		result = false;
    	}
    	
    	if (!result) {
    		this.startDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('not_a_valid_value'));
    	}
    	
        return result;
    },
    
    setPropertyValue : function() {
        this._setValue();
    }

});    
