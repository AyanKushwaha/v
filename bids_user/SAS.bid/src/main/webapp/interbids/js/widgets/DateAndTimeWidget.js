/**
 */
js.ib.widgets.DateAndTimeWidget = function(
		bidModel, bidProperty, config, dataSourceManager, view, periodModel) {
	Date.useStrict = true;
	this.bidModel = bidModel;
	this.bidProperty = bidProperty;
	this.config = config;
	this.periodModel = periodModel;
	this.attr = config.attributes;
	this.id = config.id;
	this.label = config.label;
	this.bidPropertyName = this.attr.bidPropertyName;
	var initialDate;
	if (this.bidProperty.get(this.bidPropertyName)) {
		initialDate = Environment.parseDate(
			this.bidProperty.get(this.bidPropertyName));
	} else {
		initialDate = "start" == this.bidPropertyName
			? this.bidModel.presets.start : this.bidModel.presets.end;
	}
	this.dateField = new js.crewweb.warp.jsbase.ui.CWDateField({
		id : this.id + '_date',
		hideLabel : true,
		label : this.label,
		value : initialDate,
		name : 'date',
		ufnEnabled : false,
		disabled : false,
		allowBlank : false,
		enableKeyEvents: true
	});
	this.dateField.on('cwSelect', this.setDateValue, this);
	this.dateField.on('keyup', this.setDateValue, this);
	this.dateField.on('change', this.dateField.markValid, this);
	this.timeField = new js.crewweb.warp.jsbase.ui.CWTextField({
		id: this.id + '_time',
		hideLabel: true,
		name: 'time',
		value: initialDate.format("H:i"),
		digitOnly: false,
		allowBlank: false, 
		maxLength: 5,
		enforceMaxLength: true,
		width: 48,
		regex: /^([0-1]\d{1}|2[0-3]):[0-5]\d{1}$/,
		regexText: 'time_field_blank_text', 
		blankText: 'time_field_blank_text'
	});
	this.timeField.on("blur", this.timeField.isValid, this);
	this.timeField.on("cwSelect", this.setTimeValue, this);
	this.timeField.on("keyup", this.setTimeValue, this);
	this.timeField.on("change", this.setTimeValue, this);
	
	js.ib.widgets.DateAndTimeWidget.superclass.constructor.call(
			this, 2, 
	[{
		colspan : 1,
		item : this.dateField
	}, {
		colspan : 1,
		item : this.timeField
	}]);
	
	this.on('afterlayout', this.isValid, this);
};
Ext.extend(js.ib.widgets.DateAndTimeWidget,
 js.crewweb.warp.jsbase.ui.CWTablePanel, {

	isValid : function() {
		var isDateValid = this.dateField.isValid();
		var isTimeValid = this.timeField.isValid();
		if (isDateValid && isTimeValid) {
			var startProperty = this.bidModel.propertiesByType['date_time_start'];
			var startDateTime = startProperty[0].get('start');
			var endProperty = this.bidModel.propertiesByType['date_time_end'];
			var endDateTime = endProperty[0].get('end');
			if (startDateTime > endDateTime) {
				this.dateField.markInvalid(js.crewweb.warp.jsbase.util.Localization
						.translate('Start_time_must_be_less_than_end_time'));
				return false;
			}

			this.setDateValue();
			this.setTimeValue();
			this.dateField.clearInvalid();
			return true;
		} else {
			return false;
		}
	},

	/**
	 * Clear the components in this widget.
	 */
	clear : function() {
		this.dateField.clear();
		this.timeField.clear();
	},

	/**
	 * Set focus on this widget.
	 */
	focus : function() {
		Ext.getCmp(this.dateField).focus(true);
	},

	/**
	 * Set Year, Month and Day part of the bidproperty value
	 */
	setDateValue : function() {
		var value = this.dateField.getValue();
		var timeString = this.timeField.getValue();
		if (timeString != null && timeString != "") {
			this.updateHoursAndMinutes(value, timeString);
		}
		this.bidProperty.set(this.bidPropertyName,
		       	Environment.formatISODateTime(value), true);
	},

	/**
	 * Set the Hours and Minutes part of the bidproperty value
	 * Caller must ensure the value is valid
	 */
	setTimeValue : function() {
		var oldDateTime = Environment.parseDate(
			this.bidProperty.get(this.bidPropertyName));
		this.updateHoursAndMinutes(oldDateTime, this.timeField.getValue());
		this.bidProperty.set(this.bidPropertyName,
		       	Environment.formatISODateTime(oldDateTime), true);
	},	

	/**
	 * Updates the Hours and Minutes parts of a DateTime object.
	 */
	updateHoursAndMinutes : function(dateToUpdate, hoursAndMinutesString) {
		var hoursAndMinutes = hoursAndMinutesString.split(":"); 
		dateToUpdate.setHours(hoursAndMinutes[0]);
		dateToUpdate.setMinutes(hoursAndMinutes[1]);
	},
	
	/**
	 * Set copy start value, to be able to use existing ValidityPeriodAdjuster 
	 * functionality server side. Only 'end' fields get this as only a single 
	 * bid property can define a period.
	 */
//	setPropertyValue : function() {
//		if ('end' == this.bidPropertyName) {
//			var startProperty = this.bidModel.propertiesByType['date_time_start'];
//			var startDateTime = startProperty[0].get('start');
//			this.bidProperty.set('start', startDateTime);
//		}
//    }
});
