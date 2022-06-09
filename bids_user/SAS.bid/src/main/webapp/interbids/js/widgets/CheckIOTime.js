/**
 * @class js.crewweb.warp.widgets.TwoTimes This widget contains two x two date+time fields, start and
 *        end
 * @extends js.crewweb.warp.jsbase.ui.CWTablePanel {@link js.crewweb.warp.jsbase.ui.CWTablePanel}
 */

/**
 * @constructor
 * called when a bid dialog containing this widget is created.
 * @param {js.crewweb.warp.dialog.BidModel} bidModel holds information about the current bid's values and properties. {@link js.crewweb.warp.dialog.BidModel}
 * @param {js.crewweb.warp.dialog.BidProperty} bidProperty the current bid property. {@link js.crewweb.warp.dialog.BidProperty}
 * @param {Object} config contains certain configuration. The attributes from the bid property xml are found in
 *        config.attributes.
 */
js.crewweb.warp.widgets.CheckIOTime = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel) {
	this.bidModel = bidModel;
	this.bidProperty = bidProperty;
	this.config = config;

	this.name = config.attributes.name;
	this.id = config.id;

	var checkIOTimeKey = config.attributes.checkIOTimeKey;
	var increment = parseInt(config.attributes.timeIncrement, 10);
	var startTime = config.attributes.startTime;
	var endTime = config.attributes.endTime;

    var timeValue = Environment.parseDate(this.bidProperty.get(checkIOTimeKey));
    if (!timeValue && this.bidModel && this.bidModel.presets) {
        timeValue = this.bidModel.presets.start;
    }
    if (!timeValue) {
        timeValue = startTime;
    }

	this.timeField = new js.crewweb.warp.jsbase.ui.CWTimeField({
        name: checkIOTimeKey,
        minValue: startTime,
        maxValue: endTime,
        increment: increment,
        compId: this.id + '_time',
        hideLabel: true,
        value: timeValue,
        width: 80,
        format: 'H:i'
    });
	this.timeField.on('select', this.isValid, this);
	this.timeField.on('blur', this.isValid, this);
	this.timeField.on('select', this._setValue, this);
	this.timeField.on('blur', this._setValue, this);

	js.crewweb.warp.widgets.CheckIOTime.superclass.constructor.call(this, 1, [
        {
            colspan: 1,
            item: this.timeField
        }
	]);
	this.on('render', this._setValue, this);
};

Ext.extend(js.crewweb.warp.widgets.CheckIOTime, js.crewweb.warp.jsbase.ui.CWTablePanel,
/** @scope js.crewweb.warp.widgets.TwoTimes */
{

	/**
	 * @private
	 */
	_setValue: function(){
		var timeValue = this.timeField.getValue();

		this.bidProperty.set(this.timeField.name, timeValue);

		this.timeField.validate();
	},

    /**
	 * Clear the components in this widget.
	 */
    clear: function() {
        this.timeField.clear();
    },

    /**
     * Get the id of the component in this widget that should receive focus.
     * @return {String} the id of the component in this widget that should receive focus.
     */
    getFocusComponentId: function(){
    	return this.timeField.id;
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
        return this.timeField.isValid();
    }
});
