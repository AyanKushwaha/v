/* @class js.ib.customization.standard.CreateRequestConfirmationFormatter Example on how to write a formatter
 *    responsible to create a message for the create request confirmation dialog.
 */
/**
 * Constructor.
 */

Ext.namespace('requests.formatter');

js.ib.widgets.RequestConfirmationFormatter = function() {
};

js.ib.widgets.RequestConfirmationFormatter.prototype = {

	/**
	 * @param {Object}
	 *            request the representation of the request to be created. The
	 *            request object contains a type {String} and a params {Object}.
	 * 
	 * @return {Object} object with the message (as a string or array of
	 *         strings), width and height members. Height and width is optional.
	 *         Ex:
	 * 
	 * <pre>
	 *  {
	 * message Free days:  ['Create this X request?', '(startdate - enddate)'] ,
	 * message Flight Requests: ['Create this Flight Request?', '(startdate - enddate)', 'Carrier code: carrierCode', 'Flight Number: flightNumber', 'Destination: destination' ] ,	
	 * height: 300,
	 * 	width: 200
	 * };
	 * </pre>
	 */
	createMessageConfig : function(request) {
		var S = js.crewweb.warp.jsbase.util.I18N;
		var typeName = S.MSGR(request.type);

		var startDate = request.params["startDate"];
		var nrOfDays = request.params["nr_of_days"];
		
		var startDateObj = Date.parseDate(startDate, "Y-m-d");
		var startDateFormatted = startDateObj.format("dMy");
		
		var endDateObj = new Date(startDateObj);
		endDateObj.setDate(endDateObj.getDate() + (nrOfDays - 1));
		var endDateFormatted = endDateObj.format("dMy");
		
		var date = "";
		if (startDate) {
			// Only print end date if it exists and is not equal to start date
			if (endDateFormatted != startDateFormatted) {
				date = "from " + startDateFormatted + ' to ' + endDateFormatted;
			
			//Each message is printed on a new line
			} else {
				date = "on " + startDateFormatted;
			}
		}
		
		var message = [S.MSGR('request_confirmation_message', [typeName, date])];
		
		message = message + [S.MSGR('new_line')] + [S.MSGR('new_line')];
		if (request.type == 'FS1') {
		  message = message + [S.MSGR('request_confirmation_message_extra_different_types', [typeName, "FS"])];

		} else if (request.type == 'F3S') {
		    message = message + [S.MSGR('request_confirmation_message_extra_removable', typeName)];
		} else {
    		message = message + [S.MSGR('request_confirmation_message_extra', typeName)];
    }

		var messageConfig = {
			message : message,
			width : 430
		};

		
		
		return messageConfig;
	}

};
