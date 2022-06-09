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
js.crewweb.warp.widgets.ValidityPeriodWithDisableDays = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel) {
	this.bidModel = bidModel;
	this.bidProperty = bidProperty;
    this.config = config;
    this.periodModel = periodModel;
	
	this.name = config.attributes.name;
	this.id = config.id;
	this.label = config.label;
	this.labelOff = config.attributes.labelOff;
	
	this.allowBlank = config.attributes.allowBlank === 'true';
//	this.startEmpty = config.attributes.startEmpty === 'true';
	
	var startValue = Environment.parseDate(this.bidProperty.get('start'));
	if (!startValue) {
		startValue = this._getStartValue();
	}
	
	var endValue = Environment.parseDate(this.bidProperty.get('end'));
	if (!endValue) {
		endValue = this._getEndValue();
	}
	
	this.periodStart = Environment.parseDate(this.periodModel.periodData.bidPeriod.from);
	this.periodEnd = Environment.parseDate(this.periodModel.periodData.bidPeriod.to);
    
	
	// IMPROVEMENT: read start and end names from configuration
    var startDisabled = (((config.immutableStartValue) ? config.immutableStartValue : false) || (config.attributes.start && config.attributes.start.disabled === "true"));
	this.startDateField = new js.crewweb.warp.jsbase.ui.CWDateField({
        id: this.id + '_start',
        hideLabel: true,
		value: startValue,
        name: 'start',
		ufnEnabled: false,
		disabled: startDisabled,
		allowBlank: this.allowBlank,
		showToday: false,
		minValue: this.periodStart,
		maxValue: this.periodEnd
	});
	this.startDateField.on('cwSelect', this._setValue, this);
	this.startDateField.on('valid', this.isValid, this);
	this.startDateField.on('afterrender', this._setValue, this);
	
    var ufnEnabled = (config.attributes.end && config.attributes.end.ufnEnabled === "true");
    var endDisabled = (((config.immutableEndValue)?config.immutableEndValue:false) || (config.attributes.end && config.attributes.end.disabled === "true"));
	this.endDateField = new js.crewweb.warp.jsbase.ui.CWDateField({
        id: this.id + '_end',
        hideLabel: true,
        value: endValue, 
        name: 'end',
        ufnEnabled: ufnEnabled,
        disabled: endDisabled,
        allowBlank: this.allowBlank,
        showToday: false,
        minValue: this.periodStart,
        maxValue: this.periodEnd
	});
   
	if (config.dataSources && config.dataSources.start_disabledates && config.dataSources.end_disabledates) {
		this.startDataStore = dataSourceManager.getGenericStore(config.dataSources.start_disabledates);
		this.endDataStore = dataSourceManager.getGenericStore(config.dataSources.end_disabledates);
		if (this.startDataStore.getCount() > 0 && this.endDataStore.getCount() > 0) {
            this._setDisabledDates();
        } 
        else {
            this.startDataStore.on('load', function(){
                    this._setDisabledDates();
            }, this);
            
            this.endDataStore.on('load', function() {
            	this._setDisabledDates();
            }, this);
        }
	}
	
    this.endDateField.on('cwSelect', this._setValue, this);
    this.endDateField.on('valid', this.isValid, this);
    this.endDateField.on('afterrender', this._setValue, this);
    
    var itemList = [
                    {colspan: 1, item:new js.crewweb.warp.jsbase.ui.CWTextLabel({text:js.crewweb.warp.jsbase.util.Localization.translate("From")})},
            		{colspan: 1, item:new js.crewweb.warp.jsbase.ui.CWTextLabel({text:js.crewweb.warp.jsbase.util.Localization.translate("To")})},
            	    {colspan: 1, item: this.startDateField},
            	    {colspan: 1, item: this.endDateField}
            	];
    
    js.crewweb.warp.widgets.ValidityPeriodWithDisableDays.superclass.constructor.call(this, 2, itemList);
    
    this.startDateField.other = this.endDateField;
    this.endDateField.other = this.startDateField;
    
    Ext.sequence(js.crewweb.warp.jsbase.ui.CWDateField.prototype, 'onTriggerClick', function() {
    	if (this.getValue() == undefined || this.getValue() === "") {
    		this.menu.picker.setValue(this.other.getValue() || this.minValue);
    	} else {
    		this.menu.picker.setValue(this.getValue() || this.minValue);
    	}
    });
    
};

Ext.extend(js.crewweb.warp.widgets.ValidityPeriodWithDisableDays, js.crewweb.warp.jsbase.ui.CWTablePanel, 
/** @scope js.crewweb.warp.widgets.ValidityPeriod */
{
	
	_getStartValue : function() {
		var useEmptyDefaultStartValue = this.config.attributes.start && this.config.attributes.start.useEmptyDefaultValue === "true";
		var startValue = null;
		if(!useEmptyDefaultStartValue) {
			startValue = Environment.parseDate(this.bidProperty.get('start'));
		    if (!startValue && this.bidModel.presets) {
		        startValue = this.bidModel.presets.start;
		    }
		    
		    if (!startValue) {
		        startValue = new Date();
		    }
		}
		
		return startValue;
	},
	
	_getEndValue : function() {
	    var useEmptyDefaultEndValue = this.config.attributes.end && this.config.attributes.end.useEmptyDefaultValue === "true";
	    var endValue = null;
		if(!useEmptyDefaultEndValue) {
			endValue = Environment.parseDate(this.bidProperty.get('end'));
		    if (!endValue && this.bidModel.presets) {
		        endValue = this.bidModel.presets.end;
		    }
		    if (!endValue) {
		        endValue = Environment.parseDate('2035-12-31');
		    }
		}
		
		return endValue;
	},
	
	
	_setValue: function(dateFieldCmp, date){
        var startDate = this._getDateValue(this.startDateField);
        var endDate = this._getDateValue(this.endDateField);
        var endValue = endDate ? endDate + ' 23:59' : '';
        if (endValue == '2035-12-31 23:59') {
        	endValue = null;
        	endDate = null;
        }
        
        if (!this._isValueEmpty(startDate) && !this._isValueEmpty(endDate)) {
        	this.bidProperty.set('startDate', startDate, false);
        	this.bidProperty.set('endDate', endDate, false);
        	this.bidProperty.set('alternative', this.config.attributes.alternative, false);
        	
        	var startValue = startDate ? startDate + ' 00:00' : '';
        	this.bidProperty.set('start', startValue, false);
        	this.bidProperty.set('end', endValue, true);
        } else {
        	this.bidProperty.remove('startDate');
        	this.bidProperty.remove('endDate');
        	
        	this.bidProperty.remove('start');
        	this.bidProperty.remove('end');
        	
        	this.bidProperty.remove('actual_number_of_days');
        }
	},
	
	_isValueEmpty: function(value) {
		return value == null || value === "";
	},
    
    _getDateValue: function(component) {
        var value = component.getValue();
        if (value.format) {
            return Environment.formatISODate(value);
        }
        return "";
    },
    
    /**
     * Disable the dates specified in data source
     */
    _setDisabledDates: function() {
    	var disabledStartDates = new Array();
    	var disabledEndDates = new Array();
    	
    	this.startDataStore.each(function(record){
    		if (record.data.disabledstartdates && record.data.disabledstartdates !== "") { // if it's blank all dates will be disabled
    			var date = Environment.parseDate(record.data.disabledstartdates);
    			disabledStartDates.push(js.crewweb.warp.jsbase.Environment.formatDate(date));
    		}
    	}, this);
    	this.endDataStore.each(function(record){
    		if (record.data.disabledenddates && record.data.disabledenddates !== "") { // if it's blank all dates will be disabled
    			var date = Environment.parseDate(record.data.disabledenddates);
    			disabledEndDates.push(js.crewweb.warp.jsbase.Environment.formatDate(date));
    		}
    	}, this);

    	if (disabledStartDates.length > 0) {
    		this.startDateField.setDisabledDates(disabledStartDates);
    	}
    	if (disabledEndDates.length > 0) {
    		this.endDateField.setDisabledDates(disabledEndDates);
    	}
    },
    
    
    _parseDate: function(date_string) {
    	var date = Date.parseDate(date_string, "Y-m-d H:i", false);
    	return date;
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
    isValid: function(comp) {
        var result = true;
        
        if (this.startDateField.getValue() === "" && (!this.allowBlank || this.endDateField.getValue() !== "")) {
        	this.startDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('blank_field_warning'));
            result = false;        	
        } else {
        	this.startDateField.suspendEvents();
        	this.startDateField.clearInvalid();
        	this.startDateField.resumeEvents();
        }
        
        if (this.endDateField.getValue() === "" && (!this.allowBlank || this.startDateField.getValue() !== "")) {
        	this.endDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('blank_field_warning'));
            result = false;        	
        } else {
        	this.endDateField.suspendEvents();
        	this.endDateField.clearInvalid();
        	this.endDateField.resumeEvents();
        }
        
        if (result) {
            if (this.startDateField.getValue() > this.endDateField.getValue()) {
                this.startDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('Start_time_must_be_less_than_end_time'));
                this.endDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('End_time_must_be_greater_than_start_time'))
                return false;
            }
        }
        
        if (result && comp) {
        	if (!comp.isValid()) {
        		result = false;
        	}
        }
        
        if (result) {
        	result = this._hasEnteredPreviousAlternative()
        	if (!result) {
        		this.startDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('prev_alt_needs_to_be_entered'));
        		this.endDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('prev_alt_needs_to_be_entered'))
        	}
        }
        
        if ((this.startDateField.getValue() !== "" && this.startDateField.getValue() < this.periodStart) ||
	    (this.endDateField.getValue() !== "" && this.endDateField.getValue() > this.periodEnd)) {
	    result = false;
	}
        
        return result;
    }, 
    
    _hasEnteredPreviousAlternative: function () {
    	var propertyIndex = this.bidModel.properties.indexOf(this.bidProperty);
    	
    	if (!this._isValueEmpty(this._getDateValue(this.startDateField))) {
    		if (propertyIndex > 0) {
    			var prevAlt = this.bidModel.properties[propertyIndex - 1];
    			if (this._isValueEmpty(prevAlt.entries['start'])) {
    				return false;
    			}
    		}
    	}
    	return true;
    }
});
