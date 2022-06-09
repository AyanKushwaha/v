/**
 * @class js.crewweb.warp.widgets.ValidityPeriod
 * This widget contains two date fields, hard coded to names start and end.
 * @extends js.crewweb.warp.jsbase.ui.CWTablePanel
 */

/**
 * @constructor
 * Default constructor
 * called when a bid dialog containing this widget is created.
 * @param {js.crewweb.warp.dialog.BidModel} bidModel holds information about the current bid's values and properties. {@link js.crewweb.warp.dialog.BidModel}
 * @param {js.crewweb.warp.dialog.BidProperty} bidProperty the current bid property. {@link js.crewweb.warp.dialog.BidProperty}
 * @param {Object} config contains certain configuration. The attributes from the bid property xml are found in
 *        config.attributes.
 * @param {js.ib.data.DataSourceManager} dataSourceManager used to access data sources if any should be used. {@link js.ib.data.DataSourceManager}
 * @param {js.crewweb.warp.dialog.BidView} view the view that this widget is displayed in.
 * @param {js.ib.PeriodModel} periodModel used to access period data if needed.{@link js.ib.PeriodModel}
 */
js.crewweb.warp.widgets.ValidityPeriod2 = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel) {
	this.bidModel = bidModel;
	this.bidProperty = bidProperty;
    this.config = config;
    this.periodModel = periodModel;
	
	this.name = config.attributes.name;
	this.id = config.id;
	this.label = config.label;
	this.labelOff = config.attributes.labelOff;
	
	this.weekday = this.bidModel.presets.weekdays;
	
	this.ufnAsDefault = config.attributes.end.ufnAsDefault;
	
	this.dateFormat = config.attributes.dateFormat ? config.attributes.dateFormat
			: js.ib.Environment.DATEFORMAT;
    
    this.altDateFormats = config.attributes.altDateFormats ? config.attributes.altDateFormats
			: 'm/d/Y|n/j/Y|n/j/y|m/j/y|n/d/y|m/j/Y|n/d/Y|m-d-y|m-d-Y|m/d|m-d|md|mdy|mdY|d|Y-m-d|dMY';
    
    var originalDatesEnabled = config.attributes.originalDatesEnabled ? (config.attributes.originalDatesEnabled == 'true') : false;

    var invalidTextMessage = "{0} is not a valid date - valid format is ddmmmyy";
	
    var startValue = Environment.parseDate(this.bidProperty.get('start'));
    if (originalDatesEnabled) {
	var originalStartDate = Environment.formatISODate(startValue);
	this.bidProperty.set('originalStartDate', originalStartDate, false);
    }
    if (!startValue && this.bidModel.presets) {
        startValue = this.bidModel.presets.start;
    }
    if (!startValue) {
        startValue = new Date();
    }
    
    var endValue = Environment.parseDate(this.bidProperty.get('end'));
    if (originalDatesEnabled) {
	var originalEndDate = Environment.formatISODate(endValue);
	this.bidProperty.set('originalEndDate', originalEndDate, false);
    }
    if (!endValue && this.bidModel.presets.end) {
    	
    	var bidModelStart = this.bidModel.presets.start.clearTime();
    	var periodModelStart = this.periodModel.getStartDateTime().clearTime();
    	
    	var bidModelEnd = this.bidModel.presets.end.clearTime();
        var periodModelEnd = this.periodModel.getEndDateTime().clearTime();
        
    	if (bidModelEnd.getTime() === periodModelEnd.getTime() && bidModelStart.getTime() === periodModelStart.getTime()) {
    		endValue = null;
    	} else {
    		endValue = this.bidModel.presets.end;
    	}
    }
    if (!endValue && config.attributes.end.ufnEnabled === "true") {
    	endValue = null;
    } else if (!endValue) {
	if (config.attributes.defaultPeriodLength) {
	    var endValue = new Date(startValue.getTime());
	    var defaultPeriodLength = parseInt(config.attributes.defaultPeriodLength);
	    endValue.setDate(endValue.getDate() + defaultPeriodLength - 1);
	} else {
    	    endValue = this.bidModel.presets.end;
	}
    }
    
	// IMPROVEMENT: read start and end names from configuration
    var startDisabled = (((config.immutableStartValue) ? config.immutableStartValue : false) || (config.attributes.start && config.attributes.start.disabled === "true"));
	this.startDateField = new js.crewweb.warp.jsbase.ui.CustomDateField({
        id: this.id + '_start',
        hideLabel: true,
		format : this.dateFormat,
		altFormats : this.altDateFormats,
		value: startValue,
        name: 'start',
		ufnEnabled: false,
		disabled: startDisabled,
		showToday: false,
		invalidText: invalidTextMessage
	});
	this.startDateField.on('blur', this.isValid, this);
	this.startDateField.on('blur', this._setValue, this);
	this.startDateField.on('cwSelect', this._setValue, this);
    
    var ufnEnabled = (config.attributes.end && config.attributes.end.ufnEnabled === "true");
    var endDisabled = (((config.immutableEndValue)?config.immutableEndValue:false) || (config.attributes.end && config.attributes.end.disabled === "true"));
	this.endDateField = new js.crewweb.warp.jsbase.ui.CustomDateField({
        id: this.id + '_end',
        hideLabel: true,
		format : this.dateFormat,
		altFormats : this.altDateFormats,
        value: endValue, 
        name: 'end',
        ufnEnabled: ufnEnabled,
        disabled: endDisabled,
        showToday: false,
        invalidText: invalidTextMessage,
        emptyText: 'UFN',
        allowBlank: true,
        startDateField: this.startDateField ? this.startDateField : undefined
	});
	this.endDateField.on('blur', this.isValid, this);
	this.endDateField.on('blur', this._setValue, this);
	this.endDateField.on('cwSelect', this._setValue, this);
    this.endDateField.on('valid', this.isValid, this);
    
    var itemList = [
        {colspan: 1, item:new js.ib.ui.CWTextLabel({text:js.crewweb.warp.jsbase.util.Localization.translate("From")})},
		{colspan: 1, item:new js.ib.ui.CWTextLabel({text:js.crewweb.warp.jsbase.util.Localization.translate("To")})},
	    {colspan: 1, item: this.startDateField},
	    {colspan: 1, item: this.endDateField}
	];
    
    var panelConf = {
    	layout: 'table',
    	border: false,
    	defaults: {
    		bodyStyles:'margin:55px'
    	}
    };
    js.crewweb.warp.widgets.ValidityPeriod2.superclass.constructor.call(this, 2, itemList);
};

Ext.extend(js.crewweb.warp.widgets.ValidityPeriod2, js.crewweb.warp.jsbase.ui.CWTablePanel, 
/** @scope js.crewweb.warp.widgets.ValidityPeriod */
{
	
	_setValue: function(dateFieldCmp, date){
        var startDate = this._getDateValue(this.startDateField);
        var endDate = this._getDateValue(this.endDateField);
        var endValue = endDate ? endDate + ' 23:59' : '';
        if (endValue == '2035-12-31 23:59') {
        	endValue = null;
        	endDate = null;
        }
        
        if (endValue === "") {
        	endValue = null;
        	endDate = null;
        }
        this.bidProperty.set('startDate', startDate, false);
        this.bidProperty.set('endDate', endDate, false);
        this.bidProperty.set('alternative', this.config.attributes.alternative, false);
        
        var startValue = startDate ? startDate + ' 00:00' : '';
        this.bidProperty.set('start', startValue, false);
		this.bidProperty.set('end', endValue, true);
		
		if (this.weekday) {
			var day = this.weekday;
			if (this.weekday == 0) {
				day = 7;
			} 
			this.bidProperty.set('weekday', day, false);
		}
	},
    
    _getDateValue: function(component) {
        var value = component.getValue();
        if (value.format) {
            return Environment.formatISODate(value);
        }
        return "";
    },
    
    /**
     * Get the id of the component in this widget that should receive focus.
     * @return {String} the id of the component in this widget that should receive focus.
     */
    getFocusComponentId: function(){
    	return this.startDateField.id;
    },
	
    /**
	 * Clear the components in this widget.
	 */
    clear: function() {
        this.startDateField.clear();
        this.endDateField.clear();
    },
    
    /**
	 * Set focus on this widget.
	 */
    focus: function() {
    	Ext.getCmp(this.getFocusComponentId()).focus(/*shouldSelectText*/true);
    },
    
    /**
	 * Validate data in the widget's components.
	 * @return {Boolean} true if the data is valid, false otherwise.
	 */
    isValid: function() {
        var result = true;
        [this.startDateField].each(function(component) {
            if (component.getValue() === "") {
                component.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('blank_field_warning'));
                result = false;
            } else {
                component.suspendEvents();
                component.clearInvalid();
                component.resumeEvents();
            }
        }, this);
        
        var endValue = this.endDateField.getValue();
        var rawValue = this.endDateField.getRawValue();
        if (result && !(endValue == null || endValue === "")) {
            if (this.startDateField.getValue() > this.endDateField.getValue()) {
                this.startDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('Start_time_must_be_less_than_end_time'));
                return false;
            }
        } 
        
        if (result && (endValue == null || endValue === "")) {
        	if (rawValue.toLowerCase() === "ufn" || rawValue.toLowerCase() === "") {
        		if (rawValue !== "") {
        			this.endDateField.setRawValue("UFN");
        		}
        		this.endDateField.suspendEvents();
        		this.endDateField.clearInvalid();
        		this.endDateField.resumeEvents();
        		
        	} else {
        		this.endDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('blank_field_warning'));
        		result = false;
        	}
        } 
        
        return result;
    },
    
    setPropertyValue : function() {
        this._setValue();
    }

    
});
