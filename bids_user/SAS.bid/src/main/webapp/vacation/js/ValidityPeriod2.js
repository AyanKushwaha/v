Ext.namespace('js.vacation.widgets');
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
	
	this.allowBlank = config.attributes.allowBlank === 'true';
	this.startEmpty = config.attributes.startEmpty === 'true';
	
    var startValue = Environment.parseDate(this.bidProperty.get('start'));
    if (!startValue && this.bidModel.presets && !this.startEmpty) {
        startValue = this.bidModel.presets.start;
    }
    if (!startValue && !this.startEmpty) {
        startValue = new Date();
    }
    
    var endValue = Environment.parseDate(this.bidProperty.get('end'));
    if (!endValue && this.bidModel.presets && !this.startEmpty) {
        endValue = this.bidModel.presets.end;
    }
    if (!endValue && !this.startEmpty) {
        endValue = Environment.parseDate('2035-12-31');
    }
    
	// IMPROVEMENT: read start and end names from configuration
    var startDisabled = (((config.immutableStartValue) ? config.immutableStartValue : false) || (config.attributes.start && config.attributes.start.disabled === "true"));
	this.startDateField = new js.crewweb.warp.jsbase.ui.CWDateField({
        id: this.id + '_start',
        hideLabel: true,
		value: startValue,
        name: 'start',
		ufnEnabled: false,
		disabled: startDisabled,
		allowBlank: true
	});
	this.startDateField.on('cwSelect', this._setValue, this);
	this.startDateField.on('valid', this.isValid, this);
	this.startDateField.on('blur', this._setValue, this);
	this.startDateField.on('render', this.isValid, this);
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
        allowBlank: true
	});
	this.endDateField.on('cwSelect', this._setValue, this);
	this.endDateField.on('blur', this._setValue, this);
    this.endDateField.on('valid', this.isValid, this);
    this.endDateField.on('render', this.isValid, this);
    this.endDateField.on('afterrender', this._setValue, this);
    
    var itemList = [
        {colspan: 1, item:new js.crewweb.warp.jsbase.ui.CWTextLabel({text:js.crewweb.warp.jsbase.util.Localization.translate("From")})},
		{colspan: 1, item:new js.crewweb.warp.jsbase.ui.CWTextLabel({text:js.crewweb.warp.jsbase.util.Localization.translate("To")})},
	    {colspan: 1, item: this.startDateField},
	    {colspan: 1, item: this.endDateField}
	];
    
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
        this.bidProperty.set('startDate', startDate, false);
        this.bidProperty.set('endDate', endDate, false);
        this.bidProperty.set('alternative', this.config.attributes.alternative, false);
        
        var startValue = startDate ? startDate + ' 00:00' : '';
        this.bidProperty.set('start', startValue, false);
		this.bidProperty.set('end', endValue, true);
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
        [this.startDateField, this.endDateField].each(function(component) {
            if (component.getValue() === "" && !this.allowBlank) {
                component.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('blank_field_warning'));
                result = false;
            } else {
                component.suspendEvents();
                component.clearInvalid();
                component.resumeEvents();
            }
        }, this);
        
        if (result) {
            if (this.startDateField.getValue() > this.endDateField.getValue()) {
                this.startDateField.markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('Start_time_must_be_less_than_end_time'));
                return false;
            }
        }
        return result;
    }
});
