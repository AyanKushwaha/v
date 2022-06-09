/**
 * @class js.crewweb.warp.jsbase.ui.CWDateMenu
 */
/**
 * Create a new CWDateMenu.
 */
js.crewweb.warp.jsbase.ui.CustomDateMenu = function(config){
	js.crewweb.warp.jsbase.ui.CustomDateMenu.superclass.constructor.call(this, config);
};
Ext.extend(js.crewweb.warp.jsbase.ui.CustomDateMenu, Ext.menu.DateMenu, 
/** @scope js.crewweb.warp.jsbase.ui.CWDateMenu */
{
	initComponent : function(){
	    this.on('beforeshow', this.onBeforeShow, this);
	    if(this.strict == (Ext.isIE7 && Ext.isStrict)){
	        this.on('show', this.onShow, this, {single: true, delay: 20});
	    }
	    Ext.apply(this, {
	        plain: true,
	        showSeparator: false,
	        items: this.picker = new js.crewweb.warp.jsbase.ui.CustomDatePicker(Ext.applyIf({
	            internalRender: this.strict || !Ext.isIE,
	            ctCls: 'x-menu-date-item',
	            id: this.pickerId,
	            ufnEnabled: this.ufnEnabled
	        }, this.initialConfig))
	    });
	    this.picker.purgeListeners();
	    Ext.menu.DateMenu.superclass.initComponent.call(this);
	    /**
	     * @event select
	     * Fires when a date is selected from the {@link #picker Ext.DatePicker}
	     * @param {DatePicker} picker The {@link #picker Ext.DatePicker}
	     * @param {Date} date The selected date
	     */
	    this.relayEvents(this.picker, ['select']);
	    this.on('show', this.picker.focus, this.picker);
	    this.on('select', this.menuHide, this);
	    if(this.handler){
	        this.on('select', this.handler, this.scope || this);
	    }
	}
});
