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
js.ib.widgets.FlightNumber = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel) {
	this.bidProperty = bidProperty;

//	var flight_number_map = config.attributes.flight_number;
	
	// Setup validation and message texts.
    this.width = config.attributes.width ? config.attributes.width : js.crewweb.warp.jsbase.Environment.componentWidth;
    this.allowNonStoreData = config.attributes.allowNonStoreData;
    
	createFlightNumberComboBox(this, config, dataSourceManager);
	
	this.comment = new js.crewweb.warp.jsbase.ui.CWTextLabel({
    	text: js.crewweb.warp.jsbase.util.Localization.translate(config.attributes.flightComment)
    });


	js.ib.widgets.FlightNumber.superclass.constructor.call(this, 2, [{ colspan: 1, item: this.flightNumberComboBox }, { colspan: 1, item: this.comment }]);
};

function createFlightNumberComboBox(widget, config, dataSourceManager) {
    var blankText = config.attributes.flightBlankText ? config.attributes.flightBlankText : 'blank_field_warning';
    var valueField = config.attributes.flightValueField ? config.attributes.flightValueField : 'value';
    var displayField = config.attributes.flightDisplayField ? config.attributes.flightDisplayField : 'label';
    var emptyText = config.attributes.flightEmptyText ? config.attributes.flightEmptyText : '';
    var invalidText = config.attributes.flightInvalidText ? config.attributes.flightInvalidText : 'invalidFieldValue';

    // Create the config object.
    var comboConfig = {
    	id: config.id  + '_flnr',
        name: widget.name,
        value: widget.value,
        valueField: valueField,
        displayField: displayField,
        hideLabel: true,
        allowBlank: widget.allowBlank,
        emptyText: emptyText,
        invalidText: invalidText,
        blankText: blankText,
        allowNonStoreData: widget.allowNonStoreData,
        width: widget.width,
    };
	
 // Setup the datastore
    widget.flightDataSource = null;
    if (config.attributes.options) {
    	comboConfig.comboTranslationPrefix = config.attributes['comboTranslationPrefix'];
    	comboConfig.comboOptionList = config.attributes.options;
    }
    if (config.dataSources && config.dataSources.flights) {
    	widget.flightDataSource = dataSourceManager.getGenericStore(config.dataSources.flights);
    	widget.flightDataSource.on('load', widget._onDataSourceLoaded, widget, {single: true});
    	widget.flightDataSource.on('load', function() {
            if (widget.allowBlank) {
            	widget.flightDataSource.insert(0, new Ext.data.Record({
            		name: '',
            		value: ''
            	}));
            }
    	}, widget);
        //If this widget should receive focus after datastore load then
        //we need to set up this flag
    	widget.waitingForLoadEvent = true;
        comboConfig.store = widget.flightDataSource;
    }
    
    widget.flightNumberComboBox = new js.crewweb.warp.jsbase.ui.CWComboBox(comboConfig);
    widget.flightDataSource = widget.flightNumberComboBox.store;
	widget.flightDataSource.load({
		callback: function(records, operation, success) {
			widget._setFlightInitialValue();
		}
	});
    
    widget.flightNumberComboBox.on('select', widget._setFlightValue, widget);
    widget.flightNumberComboBox.on('render', widget._setFlightInitialValue, widget);
    widget.flightNumberComboBox.on('blur', widget._setFlightValue, widget);
}

Ext.extend(js.ib.widgets.FlightNumber, js.ib.ui.CWTablePanel, {
	
	_onDataSourceLoaded: function() {
	},

	_setFlightValue: function() {
		this.bidProperty.set('flight_number', this.flightNumberComboBox.getValue());
	},

	_setFlightInitialValue : function() {
		if (this.rendered && !this.flightDataSource.isEmpty()) {
			if (this.bidProperty.get('flight_number')) {
				this.flightNumberComboBox.setValue(this.bidProperty.get('flight_number'));
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
   		return this.flightNumberComboBox.isValid();
    },
});    
