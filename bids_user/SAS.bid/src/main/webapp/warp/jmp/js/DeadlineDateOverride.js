js.crewweb.warp.widgets.PeriodViewExt = Ext.override(js.crewweb.warp.jmp.period.PeriodView.prototype, {
    getPeriodViewText : function(periodData) {
        var thePeriodData = periodData;
        if (!thePeriodData) {
            thePeriodData = this.periodModel.getPeriodData();
        }
        var selectedAwardingType = this.awardingTypeSelectionModel.selectedRecord;
        var E = js.crewweb.warp.jsbase.Environment;

        if (selectedAwardingType.data.name === thePeriodData.awardingTypeName) {
            var dateFormat = this.localization.translate('bid.period_dates_format');
            var dateTimeFormat = this.localization.translate('bid.window_dates_format');

            var bidWindow = thePeriodData.bidWindow;
            var bidPeriod = thePeriodData.bidPeriod;

            var bidWindowTo = new Date(bidWindow.to);
            var isMidnight = bidWindowTo.getHours() === 0 && bidWindowTo.getMinutes() === 0 && bidWindowTo.getMilliseconds() === 0;

            if (isMidnight) {
                bidWindowTo.setDate(bidWindowTo.getDate() - 1);
            }

            var start = Ext.util.Format.date(E.parseDate(bidPeriod.from), dateFormat);
            var end = Ext.util.Format.date(E.parseDate(bidPeriod.to), dateFormat);
            var open = Ext.util.Format.date(E.parseDate(bidWindow.from), dateTimeFormat);
            var close = Ext.util.Format.date(bidWindowTo, dateTimeFormat);

            var crewTimeZone = thePeriodData.crewTimeZone;

            if (thePeriodData.openForBidding) {
                return this.localization.translate('bid_period_label', [ open, close, start, end, crewTimeZone ]);
            } else {
                return this.localization.translate('bid_period_label_closed_period', [ open, close, start, end,
                    crewTimeZone ]);
            }
        } else {
            return this.localization.translate('no_period_info');
        }
    },
});
