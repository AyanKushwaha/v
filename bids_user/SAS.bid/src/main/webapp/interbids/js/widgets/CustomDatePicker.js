/**
 * @class js.crewweb.warp.jsbase.ui.CWDatePicker
 */
/**
 * Create a new CWDatePicker.
 */
js.crewweb.warp.jsbase.ui.CustomDatePicker = Ext.extend(Ext.DatePicker, {
	ufnText: 'UFN',
    initComponent : function() {
	    js.crewweb.warp.jsbase.ui.CustomDatePicker.superclass.initComponent.call(this);
    },

    // private
    //This is a direct copy of Ext.DatePicker.onRender()
    // Note that the new classes "x-date-bottom-left" and
    // "x-date-bottom-right" is not available in CSS.
    // I have marked the places for the changes from Ext 
    // with "IB4 CHANGED"
    onRender : function(container, position){
        var m = [
             '<table cellspacing="0">',
                '<tr><td class="x-date-left"><a href="#" title="', this.prevText ,'">&#160;</a></td><td class="x-date-middle" align="center"></td><td class="x-date-right"><a href="#" title="', this.nextText ,'">&#160;</a></td></tr>',
                '<tr><td colspan="3"><table class="x-date-inner" cellspacing="0"><thead><tr>'];
        var dn = this.dayNames;
        for (var i = 0; i < 7; i++) {
            var d = this.startDay+i;
            if (d > 6) {
                d = d-7;
            }
            m.push("<th><span>", dn[d].substr(0,1), "</span></th>");
        }
        m[m.length] = "</tr></thead><tbody><tr>";
        for (var j = 0; j < 42; j++) {
            if (j % 7 === 0 && j !== 0) {
                m[m.length] = "</tr><tr>";
            }
            m[m.length] = '<td><a href="#" hidefocus="on" class="x-date-date" tabIndex="1"><em><span></span></em></a></td>';
        }
        //IB4 CHANGED
        m.push('</tr></tbody></table></td></tr><tr>', 
                this.showToday ? '<td colspan="2" class="x-date-bottom-left" align="left"></td>' : '', 
                this.ufnEnabled ? '<td colspan="2" class="x-date-bottom-right" align="right"></td>' : '', 
                '</tr></table><div class="x-date-mp"></div>');

        var el = document.createElement("div");
        el.className = "x-date-picker";
        el.innerHTML = m.join("");

        container.dom.insertBefore(el, position);

        this.el = Ext.get(el);
        this.eventEl = Ext.get(el.firstChild);

        var prevMonthClickRepeater = new Ext.util.ClickRepeater(this.el.child("td.x-date-left a"), {
            handler: this.showPrevMonth,
            scope: this,
            preventDefault:true,
            stopDefault:true
        });

        var nextMonthClickRepeater = new Ext.util.ClickRepeater(this.el.child("td.x-date-right a"), {
            handler: this.showNextMonth,
            scope: this,
            preventDefault:true,
            stopDefault:true
        });

        this.eventEl.on("mousewheel", this.handleMouseWheel,  this);

        this.monthPicker = this.el.down('div.x-date-mp');
        this.monthPicker.enableDisplayMode('block');
        
        var kn = new Ext.KeyNav(this.eventEl, {
            "left" : function(e){
                if (e.ctrlKey) {
					this.showPrevMonth();
				} else {
					this.update(this.activeDate.add("d", -1));
				}
            },

            "right" : function(e){
                if (e.ctrlKey) {
					this.showNextMonth();
				} else {
					this.update(this.activeDate.add("d", 1));
				}
            },

            "up" : function(e){
                if (e.ctrlKey) {
                    this.showNextYear();
				} else {
                    this.update(this.activeDate.add("d", -7));
				}
            },

            "down" : function(e){
                if (e.ctrlKey) {
					this.showPrevYear();
				} else {
					this.update(this.activeDate.add("d", 7));
				}
            },

            "pageUp" : function(e){
                this.showNextMonth();
            },

            "pageDown" : function(e){
                this.showPrevMonth();
            },

            "enter" : function(e){
                e.stopPropagation();
                return true;
            },

            scope : this
        });

        this.eventEl.on("click", this.handleDateClick,  this, {delegate: "a.x-date-date"});

        this.el.unselectable();
        
        this.cells = this.el.select("table.x-date-inner tbody td");
        this.textNodes = this.el.query("table.x-date-inner tbody span");

        this.mbtn = new Ext.Button({
            text: "&#160;",
            tooltip: this.monthYearText,
            renderTo: this.el.child("td.x-date-middle", true)
        });

        this.mbtn.on('click', this.showMonthPicker, this);
        this.mbtn.el.child(this.mbtn.menuClassTarget).addClass("x-btn-with-menu");

        if(this.showToday){
            this.todayKeyListener = this.eventEl.addKeyListener(Ext.EventObject.SPACE, this.selectToday,  this);
            var today = (new Date()).dateFormat(this.format);
            this.todayBtn = new Ext.Button({
                renderTo: this.el.child("td.x-date-bottom-left", true), //IB4 CHANGED
                text: String.format(this.todayText, today),
                tooltip: String.format(this.todayTip, today),
                handler: this.selectToday,
                scope: this
            });
        }
        //IB4 CHANGED
		if (this.ufnEnabled) {
			var S = js.crewweb.warp.jsbase.util.Localization;
	        this.ufnBtn = new Ext.Button({
	            renderTo: this.el.child("td.x-date-bottom-right", true),
	            text: S.translate('UFN'),
	            tooltip: S.translate('until_further_notice'),
	            handler: this.selectUFN,
	            scope: this
	        });
		}

        
        if(Ext.isIE){
            this.el.repaint();
        }
        this.update(this.value);
    },
	selectUFN : function() {
		this.setValue("");
        this.fireEvent("select", this, this.value);
	},
	
    // private
    beforeDestroy : function() {
        if (this.ufnBtn) {
            this.ufnBtn.destroy();
        }
		js.crewweb.warp.jsbase.ui.CustomDatePicker.superclass.beforeDestroy.call();
    },
    
    setValue : function(value){
    	if (value !== "") {
    		this.value = value.clearTime(true);
    		this.update(this.value);
    	} else {
    		this.value = value;
    		this.update(this.value);
    	}
   	},
   	
   	update : function(date, forceRefresh){
   		if(this.rendered){
   			if (date === "") {
   				return;
   			}
   			var vd = this.activeDate, vis = this.isVisible();
   			this.activeDate = date;
   			if(!forceRefresh && vd && this.el){
   				var t = date.getTime();
   				if(vd.getMonth() == date.getMonth() && vd.getFullYear() == date.getFullYear()){
   					this.cells.removeClass('x-date-selected');
   					this.cells.each(function(c){
   						if(c.dom.firstChild.dateValue == t){
   							c.addClass('x-date-selected');
   							if(vis && !this.cancelFocus){
   								Ext.fly(c.dom.firstChild).focus(50);
   							}
   							return false;
   						}
   					}, this);
   					return;
   				}
   			}
   			var days = date.getDaysInMonth(),
   			firstOfMonth = date.getFirstDateOfMonth(),
   			startingPos = firstOfMonth.getDay()-this.startDay;
   			if(startingPos < 0){
   				startingPos += 7;
   			}
   			days += startingPos;
   			var pm = date.add('mo', -1),
   			prevStart = pm.getDaysInMonth()-startingPos,
   			cells = this.cells.elements,
   			textEls = this.textNodes,
   			// convert everything to numbers so it's fast
   			d = (new Date(pm.getFullYear(), pm.getMonth(), prevStart, this.initHour)),
   			today = new Date().clearTime().getTime(),
   			sel = date.clearTime(true).getTime(),
   			min = this.minDate ? this.minDate.clearTime(true) : Number.NEGATIVE_INFINITY,
   					max = this.maxDate ? this.maxDate.clearTime(true) : Number.POSITIVE_INFINITY,
   							ddMatch = this.disabledDatesRE,
   							ddText = this.disabledDatesText,
   							ddays = this.disabledDays ? this.disabledDays.join('') : false,
   									ddaysText = this.disabledDaysText,
   									format = this.format;
   							if(this.showToday){
   								var td = new Date().clearTime(),
   								disable = (td < min || td > max ||
   										(ddMatch && format && ddMatch.test(td.dateFormat(format))) ||
   										(ddays && ddays.indexOf(td.getDay()) != -1));
   								if(!this.disabled){
   									this.todayBtn.setDisabled(disable);
   									this.todayKeyListener[disable ? 'disable' : 'enable']();
   								}
   							}
   							var setCellClass = function(cal, cell){
   								cell.title = '';
   								var t = d.clearTime(true).getTime();
   								cell.firstChild.dateValue = t;
   								if(t == today){
   									cell.className += ' x-date-today';
   									cell.title = cal.todayText;
   								}
   								if(t == sel){
   									cell.className += ' x-date-selected';
   									if(vis){
   										Ext.fly(cell.firstChild).focus(50);
   									}
   								}
   								// disabling
   								if(t < min) {
   									cell.className = ' x-date-disabled';
   									cell.title = cal.minText;
   									return;
   								}
   								if(t > max) {
   									cell.className = ' x-date-disabled';
   									cell.title = cal.maxText;
   									return;
   								}
   								if(ddays){
   									if(ddays.indexOf(d.getDay()) != -1){
   										cell.title = ddaysText;
   										cell.className = ' x-date-disabled';
   									}
   								}
   								if(ddMatch && format){
   									var fvalue = d.dateFormat(format);
   									if(ddMatch.test(fvalue)){
   										cell.title = ddText.replace('%0', fvalue);
   										cell.className = ' x-date-disabled';
   									}
   								}
   							};
   							var i = 0;
   							for(; i < startingPos; i++) {
   								textEls[i].innerHTML = (++prevStart);
   								d.setDate(d.getDate()+1);
   								cells[i].className = 'x-date-prevday';
   								setCellClass(this, cells[i]);
   							}
   							for(; i < days; i++){
   								var intDay = i - startingPos + 1;
   								textEls[i].innerHTML = (intDay);
   								d.setDate(d.getDate()+1);
   								cells[i].className = 'x-date-active';
   								setCellClass(this, cells[i]);
   							}
   							var extraDays = 0;
   							for(; i < 42; i++) {
   								textEls[i].innerHTML = (++extraDays);
   								d.setDate(d.getDate()+1);
   								cells[i].className = 'x-date-nextday';
   								setCellClass(this, cells[i]);
   							}
   							this.mbtn.setText(this.monthNames[date.getMonth()] + ' ' + date.getFullYear());
   							if(!this.internalRender){
   								var main = this.el.dom.firstChild,
   								w = main.offsetWidth;
   								this.el.setWidth(w + this.el.getBorderWidth('lr'));
   								Ext.fly(main).setWidth(w);
   								this.internalRender = true;
   								// opera does not respect the auto grow header center column
   								// then, after it gets a width opera refuses to recalculate
   								// without a second pass
   								if(Ext.isOpera && !this.secondPass){
   									main.rows[0].cells[1].style.width = (w - (main.rows[0].cells[0].offsetWidth+main.rows[0].cells[2].offsetWidth)) + 'px';
   									this.secondPass = true;
   									this.update.defer(10, this, [date]);
   								}
   							}
   		}
   	}

    /**
     * @cfg {String} autoEl @hide
     */
});
Ext.reg('customdatepicker', js.crewweb.warp.jsbase.ui.CustomDatePicker);