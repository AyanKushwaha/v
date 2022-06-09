/* @class js.ib.customization.standard.CreateRequestConfirmationFormatter Example on how to write a formatter
 *    responsible to create a message for the create request confirmation dialog.
 */
/**
 * Constructor.
 */

Ext.namespace('requests.formatter');

js.ib.widgets.RequestConfirmationFormatterFS_SKD_SKS_SKN_FD = function() {
};

js.ib.widgets.RequestConfirmationFormatterFS_SKD_SKS_SKN_FD.prototype = {

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

		var message = [ S.MSGR('request_confirmation_message', typeName) ];

		var startDate = request.params["start"];
		var endDate = request.params["end"];

		var startDateTimeObj = Date.parseDate(startDate, "Y-m-d h:i");

		var startDateFormatted = startDateTimeObj.format("dMy H:i");

		if (startDate) {
			// Only print end date if it exists and is not equal to start date
			if (endDate && endDate != startDate) {
				var endDateTimeObj = Date.parseDate(endDate, "Y-m-d h:i");
				var endDateFormatted = endDateTimeObj.format("dMy H:i");

				message[message.length] = ' (' + startDateFormatted + ' - '
						+ endDateFormatted + ')';

				// Each message is printed on a new line
			} else {
				message[message.length] = '(' + startDateFormatted + ')';
			}
		}

		var messageConfig = {
			message : message,
			width : 320
		};

		return messageConfig;
	}

};
