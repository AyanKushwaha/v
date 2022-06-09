/**
 * @class js.crewweb.warp.widgets.ComboBox
 * @extends js.crewweb.warp.jsbase.ui.CWTablePanel
 */
/**
 * @constructor
 * @param {js.crewweb.warp.dialog.BidModel} bidModel holds information about the current bid's values and properties. {@link js.crewweb.warp.dialog.BidModel}
 * @param {js.crewweb.warp.dialog.BidProperty} bidProperty the current bid property. {@link js.crewweb.warp.dialog.BidProperty}
 * @param {Object} config contains certain configuration. The attributes from the bid property xml are found in
 *        config.attributes.
 * @param {js.ib.data.DataSourceManager} dataSourceManager used to access data sources if any should be used. {@link js.ib.data.DataSourceManager}
 * @param {js.crewweb.warp.dialog.BidView} view the view that this widget is displayed in.
 * @param {js.ib.PeriodModel} periodModel used to access period data if needed.{@link js.ib.PeriodModel}
 */
js.crewweb.warp.widgets.DynamicDaysComboBox = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel) {
	this.bidProperty = bidProperty;
    this.waitingForLoadEvent = false;
    this.focusOnLoad = false;
    this.bidModel = bidModel;
    
    // Check if the combobox allows blank values.
    this.allowBlank = false;
    if (config.attributes.allowBlank) {
        this.allowBlank = 'false' !== config.attributes.allowBlank; 
    }
    
    this.name = config.attributes.name;
    
    // Setup value
    this.value = config.attributes.defaultValue;
    if (bidProperty.get(this.name)) {
        this.value = bidProperty.get(this.name);
    }
    
    // Setup validation and message texts.
    this.blankText = config.attributes.blankText ? config.attributes.blankText : 'blank_field_warning';
    this.valueField = config.attributes.valueField ? config.attributes.valueField : 'value';
    this.displayField = config.attributes.displayField ? config.attributes.displayField : 'label';
    this.emptyText = config.attributes.emptyText ? config.attributes.emptyText : '';
    this.invalidText = config.attributes.invalidText ? config.attributes.invalidText : 'invalidFieldValue';
    this.width = config.attributes.width ? config.attributes.width : js.crewweb.warp.jsbase.Environment.componentWidth;
    this.allowNonStoreData = config.attributes.allowNonStoreData;

    
    // Create the config object.
    var comboConfig = {
    	id: config.id,
        name: this.name,
        value: this.value,
        valueField: this.valueField,
        displayField: this.displayField,
        hideLabel: true,
        allowBlank: this.allowBlank,
        emptyText: this.emptyText,
        invalidText: this.invalidText,
        blankText: this.blankText,
        allowNonStoreData: this.allowNonStoreData,
        width: this.width
    };
    
	// Setup the datastore
    this.dataStore = null;
    if (config.attributes.options) {
    	comboConfig.comboTranslationPrefix = config.attributes['comboTranslationPrefix'];
    	comboConfig.comboOptionList = config.attributes.options;
    }
    if (config.dataSources && config.dataSources.combo) {
        this.dataStore = dataSourceManager.getGenericStore(config.dataSources.combo);
        this.dataStore.on('load', this._setInitialValueOnLoad, this, {single: true});
        this.dataStore.on('load', function() {
            if (this.allowBlank) {
            	this.dataStore.insert(0, new Ext.data.Record({
            		name: '',
            		value: ''
            	}));
            }
    	}, this);
        //If this widget should receive focus after datastore load then
        //we need to set up this flag
        this.waitingForLoadEvent = true;
        comboConfig.store = this.dataStore;
    }
    
    this.comboBox = new js.crewweb.warp.jsbase.ui.CWComboBox(comboConfig);
    this.dataStore = this.comboBox.store;
    
    this.comboBox.on('select', this._setModelValue, this);
    
    this.comboBox.on('render', this._setInitialValue, this);
    
    this.comboBox.on('blur', this._setModelValue, this);
    this.comboBox.on('blur', this.isValid, this);
    this.comboBox.on('select', this.isValid, this);
    
    
    js.crewweb.warp.widgets.DynamicDaysComboBox.superclass.constructor.call(this, 1, 
		[
			 {
				 colspan: 1, 
				 item: this.comboBox
			 }
		]
	);
    
    

    this.on('afterlayout', this._setModelValue, this, { single: true});
    
    if (!bidProperty.get(this.name)) {
        this.comboBox.preventMark = true;
    }

};


Ext.extend(js.crewweb.warp.widgets.DynamicDaysComboBox, js.crewweb.warp.jsbase.ui.CWTablePanel, 
{
	
	/**
	 * @private
	 * Method to handle choreography when this combobox is to receive focus
	 */
	_setInitialValueOnLoad: function() {
		this._setInitialValue();
		this.waitingForLoadEvent = false;
	    if (this.focusOnLoad) {
			this.focusOnLoad = false;
			this.comboBox.focus(true, true);
			this.comboBox.collapse();
		}
	},
	
	_setInitialValue: function() {
		if (this.rendered && !this.dataStore.isEmpty()) {
			// IMPROVEMENT: use getName of this.comboBox instead of this.name - but it's buggy-ish
			if (this.bidProperty.get(this.name)) {
				this.comboBox.setValue(this.bidProperty.get(this.name));
		    }
		}
		this.comboBox.validate();
	},
    
	_setModelValue: function(){
		var value = this.comboBox.getValue();
		this.bidProperty.set(this.name, value);
	},
    
    /**
     * Clear the components in this widget.
     */
    clear: function(){
        this.comboBox.setValue('');
        this.comboBox.validate();
    },
    
    /**
     * Get the id of the component in this widget that should receive focus.
     * @return {String} the id of the component in this widget that should receive focus.
     */
    getFocusComponentId: function(){
    	return this.comboBox.id;
    },
    
    /**
     * Set focus on comboBox.
     */
    focus: function() {
    	//maybe focus() is called too early to be able to focus properly.
    	//If we are waiting for a datastore load event: Just set the focusOnLoad flag,
    	// which will be used on datastore load event handler.
    	 if (!this.waitingForLoadEvent) {
    		 this.comboBox.focus(true, true);
    	 } else {
    		 this.focusOnLoad = true;
    	 }
    },
    
    /**
     * Validate data in the widget's components. Called before submit of the bid to the server.
     * @return true if the validation succeeded, and false otherwise.
     */
    isValid: function() {
    	if (this.disabled) {
    		return true;
    	}
    	
    	var valueField = this.valueField;
    	var displayField = this.displayField;
    	var displayValue = this.comboBox.getRawValue();

    	this.dataStore.each(function(record){
    		if (displayValue === record.get(displayField)) {
    			var value = record.get(valueField);
    	    	if (value !== this.comboBox.getValue()) {
    	    		this.comboBox.setValue(value);
    	    		this._setModelValue();
    	    		return false;
    	    	}
    		}
    	}, this);
    	
        return this.comboBox.isValid() || (this.comboBox.getValue() === "" && this.allowBlankl);
    }
});
