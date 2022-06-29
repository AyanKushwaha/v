/** 
 * Function
 * @param {js.crewweb.warp.jmp.bid.ConfigurationModel.js}
 *                configModel to be used as source.
 * @param {String} bidGroup id.
 * @param {Rows} a list of rows and its data for the rendering group list                
 */
career.js.MyBidGroupTableViewHeader = function(bidGroupId, rows, configModel, localizationManager) {
    var bidTypes = configModel.getAvailableBidTypesForBidGroup(bidGroupId);
    if (bidTypes) {
        var result = "";
        bidTypes.each(function(bidType) {
            result += ", " + localizationManager.translate(bidType);
        });
        return localizationManager.translate('bid_types') + ": " + result.substring(2);
    } else {
        return localizationManager.translate('empty');
    }
};