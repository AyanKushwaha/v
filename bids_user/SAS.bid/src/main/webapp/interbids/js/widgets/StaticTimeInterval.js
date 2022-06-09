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
js.ib.widgets.StaticTimeInterval = function(bidModel, bidProperty, config, dataSourceManager) {

    this.bidModel = bidModel;
    this.bidProperty = bidProperty;
    this.config = config;

    this.labelOff = config.attributes.labelOff;

    var startTime = config.attributes.from;
    var endTime = config.attributes.to;
    
    this._setBidPropertyValues(startTime, endTime);
    
    this.from = new js.ib.ui.CWTextLabel({
    	text: js.crewweb.warp.jsbase.util.Localization.translate(config.attributes.from)
    });
    
    this.to = new js.ib.ui.CWTextLabel({
    	text: js.crewweb.warp.jsbase.util.Localization.translate(config.attributes.to)
    });
    
    var itemList = [
            	    {colspan: 1, item: this.from},
            	    {colspan: 1, item:new js.ib.ui.CWTextLabel({text:js.crewweb.warp.jsbase.util.Localization.translate("-")})},
            	    {colspan: 1, item: this.to}
            	];
    js.crewweb.warp.widgets.StaticTimeInterval.superclass.constructor.call(this, 3, itemList);
};

Ext.extend(js.ib.widgets.StaticTimeInterval, js.ib.ui.CWTablePanel, 
{
    focus: function() {

        /* This widget cannot gain focus. */
    },

    _setBidPropertyValues: function (startTime, endTime) {
        this.bidProperty.set("start_time", startTime, false);
        this.bidProperty.set("end_time", endTime, false);
    },    
    
    isValid: function() {
       return true;
    },

    clear: function() {

         /* This widget cannot be cleared. */
    }
});