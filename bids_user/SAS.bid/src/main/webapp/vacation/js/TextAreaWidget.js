/**
 * @class js.ib.widgets.Comment
 * @extends js.ib.ui.CWTablePanel {@link js.ib.ui.CWTablePanel}
 */
/**
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
js.crewweb.warp.widgets.TextAreaWidget = function(bidModel, bidProperty, config, dataSourceManager) {

    this.bidModel = bidModel;
    this.bidProperty = bidProperty;
    this.config = config;
    

    this.labelOff = config.attributes.labelOff;
    
    var defaultText = this._trimValueFromQuote(this.bidProperty.get(config.attributes.name) ? this.bidProperty.get(config.attributes.name) : ''); 

    this.commentMaxLength = 195;
    
    this.textArea = new Ext.form.TextArea({
    	name: config.attributes.name,
    	width: 200,
    	hideLabel: true,
    	value: defaultText,
    	maxLength: this.commentMaxLength,
    	enableKeyEvents: true
    });
    
    this.textArea.on('blur', this._setValue, this);
    this.textArea.on('keyup', this._updateCharCountLabel, this);
    
    this._setValue();
    
    this.charCountLabel = new js.crewweb.warp.jsbase.ui.CWTextLabel({
    	id: 'charCountLabel',
        style: 'font-style: italic;',
        html: this._trimValueFromQuote(this.textArea.getValue()).length + "/" + this.commentMaxLength,
    	cls: 'text_area_word_count'
    });
    
    
    this.label = new js.crewweb.warp.jsbase.ui.CWTextLabel({
        style: 'font-style: italic;',
        html: js.crewweb.warp.jsbase.util.Localization.translate(config.attributes.comment)
    });
    
    var items = [];
    items.push({colspan: 1, item: this.textArea});
    items.push({colspan: 1, item: this.charCountLabel});
    
    // Only show label for EXTRAVACATION
    if (bidModel.bid.type === 'EXTRAVACATION') {
    	items.push({colspan: 2, item: this.label});
    }
    
    return js.crewweb.warp.widgets.TextAreaWidget.superclass.constructor.call(this, 2, items);
    
};

Ext.extend(js.crewweb.warp.widgets.TextAreaWidget, js.crewweb.warp.jsbase.ui.CWTablePanel, 
{
    _setValue: function () {
    	var value = this.textArea.getValue();
    	if (value && value.length > 0) {
    		this.bidProperty.set(this.textArea.name, this._setValueWithinQuote(this.textArea.getValue()));
    	} else {
    		this.bidProperty.remove(this.textArea.name);
    	}
    },
    
    _setValueWithinQuote: function (str) {
    	return '"' + str + '"';
    },
    
    _trimValueFromQuote: function (valueWithQuote) {
    	if (valueWithQuote && valueWithQuote.length > 0) {
    		if (valueWithQuote.charAt(0) === '"' && valueWithQuote.charAt(valueWithQuote.length-1) === '"') {
    			return valueWithQuote.substr(1, valueWithQuote.length-2);
    		}
    	}
    	return valueWithQuote;
    },
    
	focus: function() {

        /* This widget cannot gain focus. */
    },
    
    getFocusComponentId : function() {
    	
    },

    isValid: function() {
       return this.textArea.isValid();
    },

    clear: function() {

         /* This widget cannot be cleared. */
    },
    
    _updateCharCountLabel: function () {
    	var text = this._trimValueFromQuote(this.textArea.getValue()); 
    	this.charCountLabel.setText(text.length + "/" + this.commentMaxLength);
    },
    
    _keyFilter: function (comp, e) {
    	var k = e.getKey();
    	if (k == e.ENTER) {
    		e.stopEvent();
    	}
    }
});