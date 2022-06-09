/**
 * @constructor Default constructor.
 * 
 */
js.ib.widgets.RadioAndComboBoxes = function(bidModel, bidProperty, config, dataSourceManager, view, periodModel) {

	this.bidProperty = bidProperty;
    this.config = config;
	this.name = config.attributes.name;
	this.id = config.id;
	this.label = config.label;
	this.parentId = config.id;
    this.dataStores = [];
    this.dataStoresMap = [];
	// to keep the names of the bid properties, any, less...
	this.names =[];	
    this.valueField = config.attributes.valueField ? config.attributes.valueField : 'value';
    this.displayField = config.attributes.displayField ? config.attributes.displayField : 'value';
    
    this.emptyText = config.attributes.empty_text ? config.attributes.empty_text : '-Select-';

	 // set allow blank
    this.allowBlank = false; 
    if (config.attributes.allowBlank) {
        this.allowBlank = 'false' !== config.attributes.allowBlank;
    }   
    this.defaultValue = config.attributes.defaultValue || 'any';
    // set defaultValue to the bid property value of avoidTime, if it has a
	// value
    if (this.bidProperty.get(this.name)) {
        this.defaultValue = this.bidProperty.get(this.name);
    }
    this.bidProperty.set(this.name, this.defaultValue);  
    this.radioButtons = [];
    this.labels = [];
    this.startTimeFields = [];
    this.endTimeFields = [];
	var startValue = '';
	var endValue = '';	
    var layoutConstructors = [];
    var counter = 0;
    
    this.optionList = config.attributes.options;
    this.propertyID = config.attributes.propertyID ? config.attributes.propertyID : 'id';
     
    // create "and" label
    this.inBetweenLabel = config.attributes.inBetweenLabel || 'and';
	this.btwLabel = new js.ib.ui.CWTextLabel({
        text: js.ib.util.I18N.MSGR(this.inBetweenLabel)
    });
 
    config.attributes.options.each(function(option) {   
    	if (this.defaultValue == option.value) {
    		if (option.comboboxes == 2) {
    			startValue = this.bidProperty.get(option.firstBox);
    			endValue = this.bidProperty.get(option.secondBox);
    		} else if (option.comboboxes == 1) {
    			startValue = this.bidProperty.get(option.firstBox);
    		}
    	}
        
        // create label
        this.labels[counter] = new js.ib.ui.CWTextLabel({
             text: js.ib.util.I18N.MSGR(option.label)
        });
        
        // create radio button
        this.radioButtons[counter] = new js.ib.ui.CWRadioButton({
            hideLabel: true,
            autoWidth: true,
            name: this.parentId + '_radio',
            id: this.propertyID + "_" + this.name + '_' + option.value, 
            inputValue: option.value,
            scope: this,
            checked: (this.defaultValue === option.value)
        });
        
        // add the value to the right place in the names list
        this.names[counter]=option.value;
        this.radioButtons[counter].on('check', this._checkRadioValue, this);
        
        // create data store range
        this.dataStores[counter] = this._createStoreRange(parseInt(option.optionMinRange, 10), parseInt(option.optionMaxRange, 10), option.store, option.optionType, this.allowBlank);

        var dataStore;
        if (config.dataSources && config.dataSources[option.options]) {
            dataStore = dataSourceManager.getGenericStore(config.dataSources[option.options]);
            dataStore.on('load', this._setInitialValueOnLoad, this, {single: true});
            dataStore.on('load', function() {
                if (this.allowBlank) {
                    dataStore.insert(0, new Ext.data.Record({
                        name: '',
                        value: ''
                    }));
                }
            }, this);
        } else {
            dataStore = this.dataStores[counter];
        }
        
        this.dataStoresMap[counter] = dataStore;

        // set option default value
        var optionValue = option.optionDefaultValue;
        var optionId = option.value;
        
        this.startTimeFields[counter] = new js.ib.ui.CWComboBox({
        	id: this.propertyID + "_" + this.name + "_" + optionId + '_start_time',
            valueField: this.valueField,
            displayField: this.displayField,
            store: dataStore,
            name: 'start_time',
            value: startValue,
            hideLabel: true,
            emptyText: js.ib.util.I18N.MSGR(this.emptyText),
            allowBlank: this.allowBlank,
            blankText: js.ib.util.I18N.MSGR('blank_field_warning'),
            valueNotFoundText: js.ib.util.I18N.MSGR(this.emptyText),
            width: 80
        }); 
        
        this.startTimeFields[counter].on('blur', this._setModelValue, this);
        this.startTimeFields[counter].on('select', this._setModelValue, this);
        this.startTimeFields[counter].on('select', this.isValid, this);
        this.startTimeFields[counter].on('render', this.isValid, this);
            
        this.endTimeFields[counter] = new js.ib.ui.CWComboBox({
        	id: this.propertyID + "_" + this.name + "_" + optionId + '_end_time',
            valueField: this.valueField,
            displayField: this.displayField,
            store: dataStore,
            name: 'end_time',
            value: endValue,
            hideLabel: true,
            emptyText: js.ib.util.I18N.MSGR(this.emptyText),
            allowBlank: false,
            blankText: js.ib.util.I18N.MSGR('blank_field_warning'),
            valueNotFoundText: js.ib.util.I18N.MSGR(this.emptyText),
            width: 80
        });

        this.endTimeFields[counter].on('blur', this._setModelValue, this);
    	this.endTimeFields[counter].on('select', this._setModelValue, this);
    	this.endTimeFields[counter].on('select', this.isValid, this);
    	this.endTimeFields[counter].on('blur', this.isValid, this);
		

    	// set disable if not checked
    	if (this.radioButtons[counter].checked == false) {
    		this.startTimeFields[counter].allowBlank = false;
    		this.startTimeFields[counter].setValue('');
    		this.startTimeFields[counter].disable();
    		this.endTimeFields[counter].allowBlank = false;
    		this.endTimeFields[counter].setValue('');
    		this.endTimeFields[counter].disable();
    	}
     
    	var labelText = config.attributes.unitLabel ? config.attributes.unitLabel : ''; 
     
    	this.unitLabel = new js.ib.ui.CWTextLabel({
    		text: js.crewweb.warp.jsbase.util.Localization.translate(labelText)
    	}); 
       
    	if (option.comboboxes == 2){
    		layoutConstructors.push({ colspan: 1, item: this.labels[counter] });
    		layoutConstructors.push({ colspan: 1, item: this.radioButtons[counter] });
    		layoutConstructors.push({ colspan: 1, item: this.startTimeFields[counter]});
    		layoutConstructors.push({ colspan: 1, item: this.btwLabel});
    		layoutConstructors.push({ colspan: 1, item: this.endTimeFields[counter]});
    		layoutConstructors.push({ colspan: 1, item: this.unitLabel});
    	} else if (option.comboboxes == 0){
    		layoutConstructors.push({ colspan: 1, item: this.labels[counter] });
    		layoutConstructors.push({ colspan: 4, item: this.radioButtons[counter] });
    	} else {
    		layoutConstructors.push({ colspan: 1, item: this.labels[counter] });
    		layoutConstructors.push({ colspan: 1, item: this.radioButtons[counter] });
    		layoutConstructors.push({ colspan: 1, item: this.startTimeFields[counter]});
    		layoutConstructors.push({ colspan: 3, item: this.unitLabel});
    	}
        
    	counter++;
    },this);
    
    this._initComboBoxValues();
    
    js.ib.widgets.RadioAndComboBoxes.superclass.constructor.call(this, 6, layoutConstructors);
};

Ext.extend(js.ib.widgets.RadioAndComboBoxes, js.ib.ui.CWTablePanel, 
/** @scope js.ib.widgets.ValidityPeriod */
{
    /**
	 * Clear the components in this widget.
	 */
    clear: function() {
        this.radioGroup.clear();
        this.bidProperty.set(this.name, "");

        this.startTimeFields.each(function(startTimeField) {
            startTimeField.setValue('');
            startTimeField.validate();
        }, this);
        
        this.endTimeFields.each(function(endTimeField) {
            endTimeField.setValue('');
            endTimeField.validate();
        }, this);
    },
    
    //Create the range for the datastore
    _createStoreRange: function(min, max, stores, type, allowBlank) {
        var optionArray = [];
        if (allowBlank) {
            optionArray[optionArray.length] = ['', ''];
        }
    
        var count = min;
        stores.each(function(store) {
        	var count = parseInt(store.start);
        	var end = parseInt(store.end);
        	var increment = parseInt(store.increment);
        	for (count; count<= end; count = count+increment) {
        		if (type == 'hours') {
        			var value = this.formatSecondsAsTime(count*60, "hh:mm");
        			optionArray[optionArray.length] = [value, value];
        		} else {
        			optionArray[optionArray.length] = [count, count];
        		}
        	}
        }, this);
        
        
        return new Ext.data.SimpleStore({
            id: 0,
            fields: [this.valueField, this.displayField],
            data: optionArray
        });
    },
    
    formatSecondsAsTime: function (secs, format) {
    	var hr  = Math.floor(secs / 3600);
    	var min = Math.floor((secs - (hr * 3600))/60);
    	var sec = Math.floor(secs - (hr * 3600) -  (min * 60));

    	if (hr < 10)   { hr    = "0" + hr; }
    	if (min < 10) { min = "0" + min; }
    	if (sec < 10)  { sec  = "0" + sec; }

    	if (format != null) {
    		var formatted_time = format.replace('hh', hr);
    		formatted_time = formatted_time.replace('h', hr*1+""); // check for single hour formatting
    		formatted_time = formatted_time.replace('mm', min);
    		formatted_time = formatted_time.replace('m', min*1+""); // check for single minute formatting
    		formatted_time = formatted_time.replace('ss', sec);
    		formatted_time = formatted_time.replace('s', sec*1+""); // check for single second formatting
    		return formatted_time;
    	} else {
    		return hr + ':' + min;
    	}
    },


    /**
	 * Returns the id of this widget's component that should receive focus.
	 * 
	 * @return an id string.
	 */
    getFocusComponentId: function(){
    	return this.startTimeFields[0].id;
    },
	
    
    /**
	 * Set focus on this widget.
	 */
    focus: function() {
    	Ext.getCmp(this.getFocusComponentId()).focus(/* shouldSelectText */true);
    },
    
    isValid: function() {
        var result = true;
        
        for (var i = 0; i < this.optionList.length; i++) {
    		if (this.radioButtons[i].checked) {
    			var option = this.optionList[i];
    			
    			if (option.comboboxes == 2) {
    				if (!this.startTimeFields[i].isValid() || !this.endTimeFields[i].isValid()) {
    					result = false;
    				} else if (!this._startEndValidation(this.startTimeFields[i].getValue(), this.endTimeFields[i].getValue(), option.optionType)) {
    					result = false;
    				}
    				
    				if (!result) {
    					var invalidText = 'You must select a valid range';
    					this.startTimeFields[i].markInvalid(invalidText);
    					this.endTimeFields[i].markInvalid(invalidText);
    				}
    			} else if (option.comboboxes == 1) {
    				if (!this.startTimeFields[i].isValid()) {
    					result = false;
    					this.startTimeFields[i].markInvalid();
    				}
    			}
    			
    			if (result) {
    	        	this.startTimeFields[i].clearInvalid();
    	        	this.endTimeFields[i].clearInvalid();
    	        }
    		}
    	}
        
        return result;
    },
    
    _startEndValidation: function (start, end, type) {
    	if (type == 'hours') {
    		start = Date.parseDate(start, 'H:i');
    		if (end === '100:00') {
    			end = Date.parseDate('99:00', 'H:i');
    			end = end.add(Date.HOUR, 1);
    		} else {
    			end = Date.parseDate(end, 'H:i');
    		}
    		
    		return !(start > end);
    	} else {
    		var start = parseInt(start);
    		var end = parseInt(end);
    		
    		return !(start > end);
    	}
    },

    _checkRadioValue: function(fieldCmp, newValue, oldValue) {
        if (newValue === true) {
            index = 0;
            var counter = 0; 
            for (counter; counter < this.radioButtons.length; counter++) {
                if (this.radioButtons[counter].id === fieldCmp.id) {
                	index = counter;
                    this.bidProperty.set(this.name, this.radioButtons[counter].inputValue);
                    break;
                }
            }           
            var fieldCounter = 0;
            for (fieldCounter; fieldCounter < this.radioButtons.length; fieldCounter++) {
            	// enables the selected radio button
                if (fieldCounter === index) {           	
                    this.startTimeFields[fieldCounter].allowBlank = this.allowBlank;
                    this.startTimeFields[fieldCounter].enable();
                    this.endTimeFields[fieldCounter].allowBlank = this.allowBlank;
                    this.endTimeFields[fieldCounter].enable();
                }
                // disables the unselected radio buttons
                else {
                	//  re-set value for deselected fields here
                    this.startTimeFields[fieldCounter].allowBlank = true;
                    this.startTimeFields[fieldCounter].setValue('');
                    this.startTimeFields[fieldCounter].disable();
                    this.endTimeFields[fieldCounter].allowBlank = true;
                    this.endTimeFields[fieldCounter].setValue('');
                    this.endTimeFields[fieldCounter].disable();
                }
                this.startTimeFields[fieldCounter].validate();
                this.endTimeFields[fieldCounter].validate();
            }
            
        }
    },
    
    _setInitialValueOnLoad: function(ds, data) {
    	var count = 0;
        for (count; count < this.dataStoresMap.length; count++) {
              if (ds.storeId === this.dataStoresMap[count].storeId) {
                    var needReLoad = false;
                    if (this.rendered && !this.dataStoresMap[count].isEmpty()) {
                        if (this.allowBlank === true && data.length <= 1) {
                            needReLoad = true;
                        }
                        this.startTimeFields[count].setValue(this.bidProperty.get(this.startTimeFields[count].id));
                        this.endTimeFields[count].setValue(this.bidProperty.get(this.endTimeFields[count].id));
                    }
                    else {
                        needReLoad = true;
                    }
                    if (needReLoad === true) {
                        this.startTimeFields[count].store = this.dataStores[count];
                        this.startTimeFields[count].bindStore(this.dataStores[count]);
                        this.endTimeFields[count].store = this.dataStores[count];
                        this.endTimeFields[count].bindStore(this.dataStores[count]);
                    }
                    this.startTimeFields[count].validate();
                    this.endTimeFields[count].validate();
              }
          }
      },
  
    _setModelValue: function(comp) {
    	this.optionList.each(function(option) {
    		var name = this.propertyID + "_" + this.name + "_" + option.value + '_' + comp.name;
    		
    		if (name == comp.id) {
    			if (option.comboboxes == 1) {
    				var value = comp.getValue();
    				this.bidProperty.set(option.firstBox, comp.getValue());
    				this.bidProperty.set(option.secondBox, null);
    			} else if (option.comboboxes == 2) {
    				if (comp.name == 'start_time') {
    					var value = comp.getValue();
    					this.bidProperty.set(option.firstBox, comp.getValue());
    				} else if (comp.name == 'end_time') {
    					var value = comp.getValue();
    					this.bidProperty.set(option.secondBox, comp.getValue());
    				}
    			}
    		}
    	}, this);
    },
    
    _initComboBoxValues: function(){
    	for (var i = 0; i < this.optionList.length; i++) {
    		if (this.radioButtons[i].checked) {
    			var option = this.optionList[i];
    			
    			if (option.comboboxes == 2) {
    				var value1 = this.bidProperty.get(option.firstBox);
    				var value2 = this.bidProperty.get(option.secondBox)
    				
    				this.startTimeFields[i].setValue(this.bidProperty.get(option.firstBox));
    				this.endTimeFields[i].setValue(this.bidProperty.get(option.secondBox));
    			} else if (option.comboboxes == 1) {
    				var value1 = this.bidProperty.get(option.firstBox);
    				
    				this.startTimeFields[i].setValue(this.bidProperty.get(option.firstBox));
    			}
    		}
    	}
    	
    }
    
});