Ext.namespace('js.vacation.widgets');
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
js.crewweb.warp.widgets.NoVacationComment = function(bidModel, bidProperty, config, dataSourceManager) {

    this.bidModel = bidModel;
    this.bidProperty = bidProperty;
    this.config = config;

    this.labelOff = config.attributes.labelOff;

    
    this.label = new js.crewweb.warp.jsbase.ui.CWTextLabel({
        style: 'font-style: italic;',
    	html: js.crewweb.warp.jsbase.util.Localization.translate(config.attributes.text)
    });
    
    //FIXME: Remove when issue with the protocol has been solved and we no longer required to send a value.
    this.bidProperty.set(config.attributes.name, 0);
    
    return js.crewweb.warp.widgets.NoVacationComment.superclass.constructor.call(this, 1, [
        {
            colspan: 1,
            item: this.label
        }
    ]);
};

Ext.extend(js.crewweb.warp.widgets.NoVacationComment, js.crewweb.warp.jsbase.ui.CWTablePanel, 
{
    focus: function() {

        /* This widget cannot gain focus. */
    },
    
    getFocusComponentId : function() {
    	
    },

    isValid: function() {
       return true;
    },

    clear: function() {

         /* This widget cannot be cleared. */
    }
});