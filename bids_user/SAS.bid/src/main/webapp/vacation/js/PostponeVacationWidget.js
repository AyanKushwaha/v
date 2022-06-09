Ext.namespace('js.vacation.widgets');
/**
 * @class js.ib.widgets.NumberField
 * @extends js.ib.ui.CWTablePanel
 */
/**
 * @constructor called when a bid dialog containing this widget is created.
 * @param {js.ib.bid.dialog.BidModel}
 *            bidModel holds information about the current bid's values and
 *            properties. {@link js.ib.bid.dialog.BidModel}
 * @param {js.ib.bid.dialog.BidProperty}
 *            bidProperty the current bid property.
 *            {@link js.ib.bid.dialog.BidProperty}
 * @param {Object}
 *            config contains certain configuration. The attributes from the bid
 *            property xml are found in config.attributes.
 */

js.crewweb.warp.widgets.PostponeVacationWidget = function(bidModel, bidProperty, config) {
//js.vacation.widgets.PostponeVacationWidget = function(bidModel, bidProperty, config) {
	
	var attr = config.attributes;
	var name = attr.name;

	this.bidProperty = bidProperty;
	this.name = name;
	this.minValue = attr.minValue ? parseInt(attr.minValue) : 0;
	this.maxValue = attr.maxValue ? parseInt(attr.maxValue) : null;
	this.inValidText = attr.invalidText ? attr.invalidText
			: 'value_is_not_a_number';
	this.blankText = attr.blankText ? attr.blankText
			: 'mandatory_needs_to_be_a_number';

	this.emptyText = attr.emptyText ? js.crewweb.warp.jsbase.util.Localization.translate(attr.emptyText) : '';
	js.crewweb.warp.jsbase.util.Localization.translate(config.label)
	// Localize the error messages, if the customized error message defines a
	// min and max value
	// in the localization file they will be referred to
	var Loc = js.crewweb.warp.jsbase.util.Localization;
	this.inValidText = Loc.translate(this.inValidText, [ this.minValue,
			this.maxValue ]);
	this.blankText = Loc.translate(this.blankText, [ this.minValue,
			this.maxValue ]);

	var value = this.bidProperty.get(this.name);
	var isMax = false;
	if (value === 'max') {
		isMax = true;
	}
	
	var textField = new js.crewweb.warp.jsbase.ui.CWTextField({
		fieldLabel : js.crewweb.warp.jsbase.util.Localization
				.translate(config.label),
		hideLabel : true,
		value : bidProperty.get(name),
//		digitOnly : true,
		maxLength : attr.maxLength || 32,
		allowBlank : attr.allowBlank == 'true',
		invalidText : this.invalidText,
		blankText : this.blankText,
		emptyText: this.emptyText
	});

	textField.on('change', this._setValue, this);
	textField.on('blur', this.isValid, this);

	this.textField = textField;
	
	this.comment = new js.crewweb.warp.jsbase.ui.CWTextLabel({
    	text: js.crewweb.warp.jsbase.util.Localization.translate(config.attributes.comment)
    });
	
	this.maxCheckBox = new js.crewweb.warp.jsbase.ui.CWCheckBox({
		hideLabel: true,
		width: 25,
		cls: 'maxCheckBox'
	});
	
	this.maxCheckBox.on('check', this._handleMaxCheckBox, this);
	
	this.maxComment = new js.crewweb.warp.jsbase.ui.CWTextLabel({
    	text: js.crewweb.warp.jsbase.util.Localization.translate(config.attributes.maxComment),
    	cls: 'maxComment'
    });
	
	var panelConfig = {
			layout: 'auto'
	};
	
	var daysPanel = new js.crewweb.warp.jsbase.ui.CWTablePanel(2, [{
		colspan: 1,
		item: this.textField
	}, {
		colspan: 1,
		item: this.comment
	}]);
	
	var maxPanel = new js.crewweb.warp.jsbase.ui.CWTablePanel(2, [{
		colspan: 1,
		item: this.maxCheckBox
	}, {
		colspan: 1,
		item: this.maxComment
	}], {
		defaults: {
			cls: 'maxPanel'
		}
	});
	
	
	js.crewweb.warp.widgets.PostponeVacationWidget.superclass.constructor.call(this, 2, 
			[{colspan : 1, item : this.textField},
			 {colspan : 1, item : this.comment},
			 {colspan : 2, item : maxPanel}], config = {
				 cls: 'test'
			 });


	this.on('afterlayout', this.isValid, this);
};

Ext.extend(js.crewweb.warp.widgets.PostponeVacationWidget, js.crewweb.warp.jsbase.ui.CWTablePanel, {

	_setValue : function(fieldCmp, newValue) {
		this.bidProperty.set(this.name, newValue);
	},

	clear : function() {
		this.textField.clear();
	},

	getFocusComponentId : function() {
		return this.textField.id;
	},

	focus : function() {
		Ext.getCmp(this.getFocusComponentId()).focus(
		/* shouldSelectText */true);
	},

	//Checks that the number doesn't contain a decimal sign (not done by is NaN)
	_isValidValue : function(number) {
		if (number != null) {
			var validChars = "0123456789";
			var isValidValue = true;
			var char;

			for (i = 0; i < number.length && isValidValue == true; i++) {
				char = number.charAt(i);
				// indexOf returns the position of character i in validChars,
				// and -1 if it doesn't exist
				if (validChars.indexOf(char) == -1) {
					isValidValue = false;
				}
				
				if (number.toLowerCase() === 'max') {
					isValidValue = true;
				}
			}
			
			if (number.toLowerCase() === 'max') {
				isValidValue = true;
			}
			return isValidValue;
		}
	},

	isValid : function() {
		var textField = this.textField;
		var currentValue = textField.getValue();
		if (!textField.isValid()) {
			return false;
		}
		if (!this._isValidValue(currentValue)) {
			textField.markInvalid(this.inValidText);
			return false;
		} else if ((parseInt(currentValue) > this.maxValue)
				&& this.maxValue != null) {
			textField.markInvalid(this.inValidText);
			return false;
		}

		return true;
	},
	
	_handleMaxCheckBox: function () {
		var checked = this.maxCheckBox.getValue();
		if (checked) {
			this.textField.setValue(js.crewweb.warp.jsbase.util.Localization.translate('Max'));
			this._setValue(this.textField, 'max');
		} else {
			this.textField.clear();
			this._setValue(this.textField, '');
		}
	}

});