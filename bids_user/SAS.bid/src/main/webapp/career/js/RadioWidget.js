/**
 * @class js.crewweb.warp.widgets.RadioWidget
 * @extends js.crewweb.warp.jsbase.ui.CWTablePanel
 */
/**
 * @constructor
 * called when a bid dialog containing this widget is created.
 * @param {js.crewweb.warp.dialog.BidModel} bidModel holds information about the current bid's values and properties. {@link js.crewweb.warp.dialog.BidModel}
 * @param {js.crewweb.warp.dialog.BidProperty} bidProperty the current bid property. {@link js.crewweb.warp.dialog.BidProperty}
 * @param {Object} config contains certain configuration. The attributes from the bid property xml are found in
 *        config.attributes.
 * @param {js.ib.data.DataSourceManager} dataSourceManager used to access data sources if any should be used. {@link js.ib.data.DataSourceManager}
 * @param {js.crewweb.warp.dialog.BidView} view the view that this widget is displayed in.
 * @param {js.ib.PeriodModel} periodModel used to access period data if needed.{@link js.ib.PeriodModel}
 */
js.crewweb.warp.widgets.RadioWidget = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel){

	this.bidProperty = bidProperty;
	this.config = config;
	
	this.name = config.attributes.name;
	this.parentId = config.id;
	
	this.radioButtons = [];
	
	// set default value
    this.defaultValue = config.attributes.defaultValue;
    
    // override with actual value if available
    var valueFromBidProperty = this.bidProperty.get(this.name);
    if (valueFromBidProperty) {
        this.defaultValue = valueFromBidProperty;
    }
	
	if (this.defaultValue) {
		this.bidProperty.set(this.name, this.defaultValue);
	}
	
	

	config.attributes.options.each(function(option){
		this.radioButtons[this.radioButtons.length] = new js.crewweb.warp.jsbase.ui.CWRadioButton({
			hideLabel:true,
			boxLabel:js.crewweb.warp.jsbase.util.Localization.translate(option.label),
			name: '' + this.parentId + '_radio',
			id: this.name + '_' + option.value, 
			inputValue: option.value,
			scope: this,
			checked: (this.defaultValue == option.value)
		});
	}, this);

	this.radioGroup = new js.crewweb.warp.jsbase.ui.CWRadioGroup({
		id: this.parentId,
		items: this.radioButtons,
		hideLabel: true,
		columns: 3,
		width: 300
	});
	this.radioGroup.on('change', this._setValue, this);
	
	js.crewweb.warp.widgets.RadioWidget.superclass.constructor.call(this, 1, 
		[
			 {
				 colspan: 1, 
				 item: this.radioGroup
			 }
		], {layout: 'expandtable'}
	);
	
};

Ext.extend(js.crewweb.warp.widgets.RadioWidget, js.crewweb.warp.jsbase.ui.CWTablePanel, 
{
        
	_setValue: function(fieldCmp, newValue, oldValue){
		this.bidProperty.set(this.name, newValue.getRawValue());
	},
	
    /**
     * Validate data in the widget's components. Called before submit of the bid to the server.
     * @return {Boolean} true if the validation succeeded, false otherwise.
     */
    isValid: function() {
		var value = this.bidProperty.get(this.name);
		if (value && value !== ""){
			return true;
		} else {
			this.radioButtons[0].markInvalid(js.crewweb.warp.jsbase.util.Localization.translate('must_select_an_option'));
            return false;
		}
	},
    
    /**
     * Clear the components in this widget.
     */
    clear: function() {
		this.radioGroup.clear();
        this.bidProperty.set(this.name, "");
    },
    
    /**
     * Get the id of the component in this widget that should receive focus.
     * @return {String} the id of the component in this widget that should receive focus.
     */
    getFocusComponentId: function(){
    	return this.radioGroup.id;
    },
    
    /**
     * Set focus on this widget.
     */
    focus: function() {
		Ext.getCmp(this.getFocusComponentId()).focus();
    }
});
