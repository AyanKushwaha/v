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
js.ib.widgets.SingleDateWidgetWithDataSource = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel) {
	this.bidProperty = bidProperty;
	this.bidModel = bidModel;

	var widget = this;
	var flightNumberProperty = widget.bidModel.propertiesByType['flight_number'][0];

    this.dateFormat = config.attributes.dateFormat ? config.attributes.dateFormat
			: js.ib.Environment.DATEFORMAT;
//	var flight_number_map = config.attributes.flight_number;
	
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
		format : this.dateFormat,
        hideLabel: true,
        allowBlank: this.allowBlank,
        emptyText: this.emptyText,
        invalidText: this.invalidText,
        blankText: this.blankText,
        allowNonStoreData: this.allowNonStoreData,
        width: this.width,
        editable:false,
        lastQuery: '',
        typeAhead: 'true',
        listeners: {
            beforequery: function(qe) {
        		var flightNumber = flightNumberProperty.get('flight_number');
        		widget.dataStore.filter('flightnumber', new RegExp('^' + flightNumber + '$'));
            }	    	
        }
    };
 // Setup the datastore
    this.dataStore = null;
    if (config.attributes.options) {
    	comboConfig.comboTranslationPrefix = config.attributes['comboTranslationPrefix'];
    	comboConfig.comboOptionList = config.attributes.options;
    }
    if (config.dataSources && config.dataSources.combo) {
        this.dataStore = dataSourceManager.getGenericStore(config.dataSources.combo);
        this.dataStore.on('load', this._onDataSourceLoaded, this, {single: true});
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
    
	this.departureDateComboBox = new js.crewweb.warp.jsbase.ui.CWComboBox(comboConfig);
	this.dataStore = this.departureDateComboBox.store;
	widget.dataStore.load({
		callback: function(records, operation, success) {
			widget._setInitialValue();
		}
	});
	
	this.departureDateComboBox.on('select', this._setValue, this);
	this.departureDateComboBox.on('render', this._setInitialValue, this);
	this.departureDateComboBox.on('blur', this._setValue, this);

	js.ib.widgets.SingleDateWidgetWithDataSource.superclass.constructor.call(this, 1, [{ colspan: 1, item: this.departureDateComboBox }]);

	flightNumberProperty.on('updated', function(prop) {
		widget.departureDateComboBox.reset();
   		var flightNumber = flightNumberProperty.get('flight_number');
   		widget.dataStore.filter('flightnumber', new RegExp('^' + flightNumber + '$')); 
    });	    	

};

Ext.extend(js.ib.widgets.SingleDateWidgetWithDataSource, js.ib.ui.CWTablePanel, {
	
	
	_onDataSourceLoaded: function() {
	},

	_setValue: function() {
		this.bidProperty.set('startDate', this.departureDateComboBox.getValue());
	},
	
	_setInitialValue : function() {
		if (this.rendered && !this.dataStore.isEmpty()) {
			if (this.bidProperty.get('startDate')) {
				this.departureDateComboBox.setValue(this.bidProperty.get('startDate'));
			}
		}
	},
	
    clear: function() {
    },
    
    getFocusComponentId: function() {
    	
    },
    
    focus: function() {
    	
    },
    
    isValid: function() {
   		return this.departureDateComboBox.isValid();
    },
});    
