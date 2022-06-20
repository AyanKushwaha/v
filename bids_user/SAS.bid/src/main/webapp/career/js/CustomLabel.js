/**
 * @class js.crewweb.warp.widgets.Label
 * A simple label
 * @extends js.crewweb.warp.jsbase.ui.CWTablePanel
 * 
 * @cfg {boolean} attributes.labelOff removes the label in front of this bid property
 * @cfg {String} attributes.text this is a key that will be translated (if present in interbids_en.properties)
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
js.crewweb.warp.widgets.CustomLabel = function(bidModel, bidProperty, config, dataSourceManager) {
    this.bidModel = bidModel;
    this.bidProperty = bidProperty;
    this.config = config;

    this.labelOff = config.attributes.labelOff;
    this.label = new Ext.form.Label({
    	text: js.crewweb.warp.jsbase.util.Localization.translate(config.attributes.text)
    });
    
    this.bidProperty.set(config.attributes.name, 0);

    return js.crewweb.warp.widgets.CustomLabel.superclass.constructor.call(this, 1, [
        {
            colspan: 1,
            item: this.label
        }
    ]);
};

Ext.extend(js.crewweb.warp.widgets.CustomLabel, js.crewweb.warp.jsbase.ui.CWTablePanel, 
{
    focus: function() {
        /* This widget cannot gain focus. */
    },

    isValid: function() {
       return true;
    },

    clear: function() {
         /* This widget cannot be cleared. */
    },
    
    getFocusComponentId: function() {
    	return;
    }
});