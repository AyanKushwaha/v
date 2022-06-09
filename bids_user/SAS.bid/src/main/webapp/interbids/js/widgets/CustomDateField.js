/**
 * @class js.crewweb.warp.jsbase.ui.CWDateField
 * @extends Ext.form.DateField
 */
/**
 * @constructor
 * 
 * Create a new CWDateField.
 * 
 * @param {Object} config the configuration object.
 *
 */
js.crewweb.warp.jsbase.ui.CustomDateField = function(config) {
	/**
	 * @cfg {boolean} disabled true if the box is disabled. Defaults to false.
	 */
	/**
	 * @cfg {Array} disabledDays an array of days to disable, 0 based. For example, [0, 6] disables
	 *                Sunday and Saturday. Defaults to null.
	 */
	/**
	 * @cfg {String} disabledDaysText the tooltip to display when the date falls on a disabled day. Defaults to 'Disabled'.
	 */
	/**
	 * @cfg {Array} disabledDates An array of "dates" to disable, as strings. These strings will be used to 
	 *        build a dynamic regular expression so they are very powerful. Some examples:
	 *        <br/> ["03/08/2003", "09/16/2003"] would disable those exact dates
	 *        <br/> ["03/08", "09/16"] would disable those days for every year
	 *        <br/> ["^03/08"] would only match the beginning (useful if you are using short years)
	 *        <br/> ["03/../2006"] would disable every day in March 2006
	 *        <br/> ["^03"] would disable every day in every March
	 *        <br/> Note that the format of the dates included in the array should exactly match the format config.
	 *        <br/> In order to support regular expressions, if you are using a date format that has "." in it, you will 
	 *        <br/> have to escape the dot when restricting dates. For example: ["03\\.08\\.03"].
	 *        <br/> Defaults to null.
	 */
	/**
	 * @cfg {String} disabledDatesText the tooltip text to display when the date falls on a disabled
	 *        date. Defaults to 'Disabled'.
	 */
	/**
	 * @cfg {String} fieldLabel label for the field. Defaults to ''. 
	 */
	/**
	 * @cfg {boolean} hideLabel true to hide the label. Defaults to false.
	 */
	/**
	 * @cfg {String} labelSeparator separates the label text from the component. Defaults to ':'.
	 */
	/**
	 * @cfg {boolean} ufnEnabled true to show the UFN button, false otherwise. Defaults to false.
	 */
	/**
	 * @cfg {Date} value the start value of the component. Defaults to null.
	 */
	/**
	 * @cfg {int} width the width of this component. Defaults to 120px.
	 */
	/**
     * @event change
     * Fires just before the field blurs if the field value has changed.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     * @param {Mixed} newValue the new value.
     * @param {Mixed} oldValue the original value.
     */
    /**
     * @event disable
     * Fires after the component is disabled.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event enable
     * Fires after the component is enabled.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event beforeshow
     * Fires before the component is shown by calling the {@link #show} method.
     * Return false from an event handler to stop the show.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event show
     * Fires after the component is shown when calling the {@link #show} method.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event beforehide
     * Fires before the component is hidden by calling the {@link #hide} method.
     * Return false from an event handler to stop the hide.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event hide
     * Fires after the component is hidden.
     * Fires after the component is hidden when calling the {@link #hide} method.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event beforerender
     * Fires before the component is {@link #rendered}. Return false from an
     * event handler to stop the {@link #render}.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event render
     * Fires after the component markup is {@link #rendered}.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event afterrender
     * <p>Fires after the component rendering is finished.</p>
     * <p>The afterrender event is fired after this Component has been {@link #rendered}, been postprocesed
     * by any afterRender method defined for the Component, and, if {@link #stateful}, after state
     * has been restored.</p>
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
	/**
     * @event focus
     * Fires when this field receives input focus.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
    /**
     * @event valid
     * Fires after the field has been validated with no errors.
     * @param {js.crewweb.warp.jsbase.ui.CWDateField} dateField this date field.
     */
	config.width = config.width ? config.width : js.crewweb.warp.jsbase.Environment.componentWidth;
	config.fieldLabel = js.crewweb.warp.jsbase.util.Localization.translate(config.fieldLabel);
	// Translate any given texts.
	if (config.disabledDaysText) {
		config.disabledDaysText = js.crewweb.warp.jsbase.util.Localization.translate(config.disabledDaysText);
	}
	if (config.disabledDatesText) {
		config.disabledDatesText = js.crewweb.warp.jsbase.util.Localization.translate(config.disabledDatesText);
	}
	config.format = js.crewweb.warp.jsbase.Environment.DATEFORMAT;
	
	this.startField = config.startDateField;
	
	this.addEvents({
		/**
		 * @event cwSelect called when a date has been selected.
		 * @param {CWDateField} cwDateField the date field that fired the event
		 * @param {String} date the date that was selected.
		 */
        'cwSelect': true
    });
    this.on('change', function(dateValue) {
    	this.fireEvent('cwSelect', this, dateValue);
    });
	
	js.crewweb.warp.jsbase.ui.CustomDateField.superclass.constructor.call(this, config);
	
	
};

Ext.extend(js.crewweb.warp.jsbase.ui.CustomDateField, Ext.form.DateField, 
/** @scope js.crewweb.warp.jsbase.ui.CWDateField */
{
	/**
	 * Clear the component. Set it's value to be a specified default value.
	 */
	clear: function() {
		this.setValue(new Date());
	},
	
	/**
	 * Disable this component.
	 */
	disable: function() {
		js.crewweb.warp.jsbase.ui.CustomDateField.superclass.disable.call(this);
	},
	
	/**
	 * Enable this component.
	 */
	enable: function() {
		js.crewweb.warp.jsbase.ui.CustomDateField.superclass.enable.call(this);
	},
	
	/**
	 * Give focus to this component.
	 */
	focus: function() {
		js.crewweb.warp.jsbase.ui.CustomDateField.superclass.focus.call(this, true, false);
	},
	
	/**
	 * Get the value of this component.
	 * 
	 * @return {Date} the value of this component.
	 */
	getValue: function() {
		return js.crewweb.warp.jsbase.ui.CustomDateField.superclass.getValue.call(this);
	},
	
	/**
	 * Set the value of this component to the given value.
	 * @param {Date/String} dateValue the value to set. This can be a date or an ISO 8601 formatted date string.
	 */
	setValue: function(dateValue) {
		if (dateValue && typeof dateValue !== 'string') {
			dateValue = js.crewweb.warp.jsbase.Environment.formatISODate(dateValue);
		}
		js.crewweb.warp.jsbase.ui.CustomDateField.superclass.setValue.call(this, dateValue);
		this.fireEvent('cwSelect', this, dateValue);
	},
	
	
	/*----------------------------------- PRIVATE -----------------------------------------------------*/
	
    /**
     * @private
     * Implements the default empty TriggerField.onTriggerClick function to display the DatePicker
     * EXTOVERRIDE
     */
    onTriggerClick : function(){
	 	if(this.disabled){
	         return;
	     }
	     if(!this.menu){
	    	 this.menu = new js.crewweb.warp.jsbase.ui.CustomDateMenu({
	    		 ufnEnabled: this.ufnEnabled,
		         hideOnClick: false,
		         focusOnSelect: false
	    	 });
	     }
	     this.onFocus();
	     Ext.apply(this.menu.picker,  {
	    	 startDay : Environment.firstDayOfWeek,
	         minDate : this.minValue,
	         maxDate : this.maxValue,
	         disabledDatesRE : this.disabledDatesRE,
	         disabledDatesText : this.disabledDatesText,
	         disabledDays : this.disabledDays,
	         disabledDaysText : this.disabledDaysText,
	         format : this.format,
	         showToday : this.showToday,
	         minText : String.format(this.minText, this.formatDate(this.minValue)),
	         maxText : String.format(this.maxText, this.formatDate(this.maxValue))
	     });
	     
	     var date = new Date();
	     if (this.startField != null) {
	    	 date = this.startField.getValue();
	     }
	     this.menu.picker.setValue(this.getValue() || date);
	     this.menu.show(this.el, "tl-bl?");
	     this.menuEvents('on');
    }
});
Ext.reg('customdatefield', js.crewweb.warp.jsbase.ui.CustomDateField);
