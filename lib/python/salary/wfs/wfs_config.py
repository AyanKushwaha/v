PAYCODE_FROM_EVENT = {
            'VA_NO'             :   'SAS_NO_CMS_VA_PERFORMED', 
            'VA1_NO'            :   'SAS_NO_CMS_VA1_PERFORMED',
            'SOLD_NO_CC'        :   'SAS_NO_CMS_SOLD_CC',
            'SOLD_NO_FC'        :   'SAS_NO_CMS_SOLD_FC',
            'BOUGHT_FORCED_NO'  :   'SAS_NO_CMS_BOUGHT_FORCED',
            'BOUGHT_NO_FC'      :   'SAS_NO_CMS_BOUGHT_FC',
            'BOUGHT_NO_CC'      :   'SAS_NO_CMS_BOUGHT_CC',
            'BOUGHT_8_NO_FC'    :   'SAS_NO_CMS_BOUGHT_8_FC',
            'BOUGHT_8_NO_CC'    :   'SAS_NO_CMS_BOUGHT_8_CC',
            'F7S_NO_CC'         :   'SAS_NO_CMS_F7S_CC',
            'F0_F3_NO_FC'       :   'SAS_NO_CMS_F0_F3_FC',
            'F0_F3_NO_CC'       :   'SAS_NO_CMS_F0_F3_CC',
            'F31_F33_NO'        :   'SAS_NO_CMS_F31_F33',
            'BOUGHT_BL_NO'      :   'SAS_NO_CMS_BOUGHT_BL',
            'BOUGHT_FORCED_DK'  :   'SAS_DK_CMS_BOUGHT_FORCED',
            'BOUGHT_DK_CC'      :   'SAS_DK_CMS_BOUGHT_CC',
            'BOUGHT_DK_FC'      :   'SAS_DK_CMS_BOUGHT_FC',
            'BOUGHT_8_DK_CC'    :   'SAS_DK_CMS_BOUGHT_8_CC',
            'BOUGHT_8_DK_FC'    :   'SAS_DK_CMS_BOUGHT_8_FC',
            'SOLD_DK_FC'        :   'SAS_DK_CMS_SOLD_FC',
            'SOLD_DK_CC'        :   'SAS_DK_CMS_SOLD_CC',
            'F0_F3_DK_FC'       :   'SAS_DK_CMS_F0_F3_FC',
            'F0_F3_DK_CC'       :   'SAS_DK_CMS_F0_F3_CC',
            'F7S_DK_CC'         :   'SAS_DK_CMS_F7S_CC',
            'VA_DK'             :   'SAS_DK_VACATION_D',
            'VA1_DK'            :   'SAS_DK_VACATION_UNPAID_D',
            'BOUGHT_BL_DK'      :   'SAS_DK_CMS_BOUGHT_BL',
            'BOUGHT_SE'         :   'SAS_SE_CMS_BOUGHT',
            'BOUGHT_8_SE'       :   'SAS_SE_CMS_BOUGHT_8',
            'BOUGHT_FORCED_SE'  :   'SAS_SE_CMS_BOUGHT_FORCED',
            'BOUGHT_BL_SE'      :   'SAS_SE_CMS_BOUGHT_BL',
            'F7_F31_FC'         :   'SAS_SE_CMS_ERS_F7_F31_FLIGHT',
            'F7_F31_CC'         :   'SAS_SE_CMS_ERS_F7_F31_CABIN',
            'F7S_SE'            :   'SAS_SE_CMS_F7S',
            'F0_F3_SE'          :   'SAS_SE_CMS_F0_F3',
            'SOLD_SE'           :   'SAS_SE_CMS_SOLD',
            'VA_SE_CC'          :   'SAS_SE_CMS_CC_VA_PERFORMED',
            'VA_SE_FC'          :   'SAS_SE_CMS_FD_VA_PERFORMED', # Kept FC in event for consistency (FD==FC=TRUE)
            'VA1_SE'            :   'SAS_SE_CMS_UNPAID_VACATION',
            'OT_DK_CC'          :   'SAS_DK_CMS_OT',
            'OT_DK_FC'          :   'SAS_DK_CMS_OTFC',
            'OT_LATE_CO_DK_FC'  :   'SAS_DK_CMS_OT_CO_LATE_FC',
            'TEMP_DK'           :   'SAS_DK_CMS_TEMP_CREW_HOURS',
            'OT_NO_CC'          :   'SAS_NO_CMS_OT',
            'OT_NO_FC'          :   'SAS_NO_CMS_OTFC',
            'OT_LATE_CO_NO_FC'  :   'SAS_NO_CMS_OT_CO_LATE_FC',
            'TEMP_NO'           :   'SAS_NO_CMS_TEMPCREW',
            'OT_SE_FC'          :   'SAS_SE_CMS_CALM_OTFC',
            'OT_LATE_CO_SE_FC'  :   'SAS_SE_CMS_OT_CO_LATE_FC',
            'TEMP_SE'           :   'SAS_SE_CMS_TEMPCREW',
            'OT_SE_CC'          :   'SAS_SE_CMS_OVERTIME',
            'CNLN_OT_45_50_DK'  :   'SAS_DK_CNLN_OT_45_50',
            'CNLN_OT_50_PLUS_DK':   'SAS_DK_CNLN_OT_50_PLUS',
            'CNLN_OT_45_50_NO'  :   'SAS_NO_CNLN_OT_45_50',
            'CNLN_OT_50_PLUS_NO':   'SAS_NO_CNLN_OT_50_PLUS',
            'F7_NO_FC'          :   'SAS_NO_CMS_F7D_3_29',
            'F7_NO_CC'          :   'SAS_NO_F7_VA_DAGER_3_29',
            'F7_SE_CC'          :   'SAS_SE_CMS_ERS_F7_F31_CABIN',
            'F7_SE_FC'          :   'SAS_SE_CMS_ERS_F7_F31_FLIGHT',
            'F7_DK_FC'          :   'SAS_DK_FD_F7',
            'F7_DK_CC'          :   'SAS_DK_CMS_F7S_CC',
            'CNLN_LAND_DAY_OFF_DK': 'SAS_DK_CNLN_LAND_DAY_OFF',
            'CNLN_LAND_DAY_OFF_NO': 'SAS_NO_CNLN_LAND_DAY_OFF',
            'CNLN_SOLD_DK'      :   'SAS_DK_CNLN_SOLD_DAYOFF',
            'CNLN_SOLD_NO'      :   'SAS_NO_CNLN_SOLD_DAYOFF',
            'CNLN_PROD_WEEKDAY_DK': 'SAS_DK_CNLN_PROD_WEEKDAY',
            'CNLN_PROD_WEEKEND_DK':   'SAS_DK_CNLN_PROD_WEEKEND_HOLIDAY',
            'CNLN_PROD_SICK_DK' :   'SAS_DK_CNLN_PROD_SICK',
            'CNLN_PROD_WEEKDAY_NO': 'SAS_NO_CNLN_PROD_WEEKDAY',
            'CNLN_PROD_WEEKEND_NO':   'SAS_NO_CNLN_PROD_WEEKEND_HOLIDAY',
            'CNLN_PROD_SICK_NO' :   'SAS_NO_CNLN_PROD_SICK',
            'ABS_F7_DAG_CABIN_3_1_D_SE' :  'SAS_SE_ABS_F7_DAG_CABIN_3_1_D'
        }

EVENT_FROM_PAYCODE = {
            'SAS_NO_CMS_VA_PERFORMED'       : 'VA', 
            'SAS_NO_CMS_VA1_PERFORMED'      : 'VA1',
            'SAS_NO_CMS_SOLD_CC'            : 'SOLD',
            'SAS_NO_CMS_SOLD_FC'            : 'SOLD',
            'SAS_NO_CMS_BOUGHT_FORCED'      : 'BOUGHT_FORCED',
            'SAS_NO_CMS_BOUGHT_FC'          : 'BOUGHT',
            'SAS_NO_CMS_BOUGHT_CC'          : 'BOUGHT',
            'SAS_NO_CMS_BOUGHT_8_FC'        : 'BOUGHT_8',
            'SAS_NO_CMS_BOUGHT_8_CC'        : 'BOUGHT_8',
            'SAS_NO_CMS_BOUGHT_BL'          : 'BOUGHT_BL',
            'SAS_DK_CMS_BOUGHT_FORCED'      : 'BOUGHT_FORCED',
            'SAS_DK_CMS_BOUGHT_CC'          : 'BOUGHT',
            'SAS_DK_CMS_BOUGHT_FC'          : 'BOUGHT',
            'SAS_DK_CMS_BOUGHT_8_CC'        : 'BOUGHT_8',
            'SAS_DK_CMS_BOUGHT_8_FC'        : 'BOUGHT_8',
            'SAS_DK_CMS_SOLD_FC'            : 'SOLD',
            'SAS_DK_CMS_SOLD_CC'            : 'SOLD',
            'SAS_DK_VACATION_D'             : 'VA',
            'SAS_DK_VACATION_UNPAID_D'      : 'VA1',
            'SAS_DK_CMS_BOUGHT_BL'          : 'BOUGHT_BL',
            'SAS_SE_CMS_BOUGHT'             : 'BOUGHT',
            'SAS_SE_CMS_BOUGHT_8'           : 'BOUGHT_8',
            'SAS_SE_CMS_BOUGHT_FORCED'      : 'BOUGHT_FORCED',
            'SAS_SE_CMS_BOUGHT_BL'          : 'BOUGHT_BL',
            'SAS_SE_CMS_SOLD'               : 'SOLD',
            'SAS_SE_CMS_CC_VA_PERFORMED'    : 'VA',
            'SAS_SE_CMS_FD_VA_PERFORMED'    : 'VA',
            'SAS_SE_CMS_VA_PERFORMED'       : 'VA', 
            'SAS_SE_CMS_UNPAID_VACATION'    : 'VA1',
            'SAS_DK_CMS_OT'                 : 'OT',
            'SAS_DK_CMS_OTFC'               : 'OT',
            'SAS_DK_CMS_OT_CO_LATE_FC'      : 'OT_LATE_CO',
            'SAS_DK_CMS_TEMP_CREW_HOURS'    : 'TEMP',
            'SAS_NO_CMS_OT'                 : 'OT',
            'SAS_NO_CMS_OTFC'               : 'OT',
            'SAS_NO_CMS_OT_CO_LATE_FC'      : 'OT_LATE_CO',
            'SAS_NO_CMS_TEMPCREW'           : 'TEMP',
            'SAS_SE_CMS_CALM_OTFC'          : 'OT',
            'SAS_SE_CMS_OT_CO_LATE_FC'      : 'OT_LATE_CO',
            'SAS_SE_CMS_TEMPCREW'           : 'TEMP',
            'SAS_SE_CMS_OVERTIME'           : 'OT',
            'SAS_SE_CMS_F0_F3'              : 'F3',
            'SAS_DK_CMS_F0_F3_FC'           : 'F3',
            'SAS_DK_CMS_F0_F3_CC'           : 'F3',
            'SAS_NO_CMS_F0_F3_FC'           : 'F3',
            'SAS_NO_CMS_F0_F3_CC'           : 'F3',
            'SAS_DK_CNLN_OT_45_50'          : 'CNLN_OT_45_50' ,
            'SAS_DK_CNLN_OT_50_Plus'        : 'CNLN_OT_50_Plus', 
            'SAS_DK_CNLN_OT_50_PLUS'        : 'CNLN_OT_50_PLUS',
            'SAS_NO_CNLN_OT_45_50'          : 'CNLN_OT_45_50',
            'SAS_NO_CNLN_OT_50_Plus'        : 'CNLN_OT_50_Plus', 
            'SAS_NO_CNLN_OT_50_PLUS'        : 'CNLN_OT_50_PLUS',
            'SAS_NO_CMS_F7D_3_29'			: 'F7',
            'SAS_NO_F7_VA_DAGER_3_29'		: 'F7',
            'SAS_SE_CMS_ERS_F7_F31_CABIN'   : 'F7',
            'SAS_SE_CMS_ERS_F7_F31_FLIGHT'  : 'F7',
            'SAS_DK_FD_F7' 			        : 'F7',
            'SAS_DK_CMS_F7S_CC'             : 'F7',
            'SAS_DK_CNLN_LAND_DAY_OFF'     : 'CNLN_LAND_DAY_OFF',
            'SAS_NO_CNLN_LAND_DAY_OFF'      : 'CNLN_LAND_DAY_OFF',
            'SAS_DK_CNLN_SOLD_FDAY'         : 'SOLD',
            'SAS_DK_CNLN_SOLD_DAYOFF'       : 'SOLD',
            'SAS_NO_CNLN_SOLD_FDAY'         : 'SOLD',
            'SAS_NO_CNLN_SOLD_DAYOFF'       : 'SOLD',
            'SAS_DK_CNLN_Sold_Fhour_Duty_Co': 'SOLD',
            'SAS_DK_CNLN_Sold_FDay'         : 'SOLD',
            'SAS_DK_CNLN_OT_50+'            : 'CNLN_OT_50_Plus',
            'SAS_DK_CNLN_PROD_WEEKDAY'      : 'CNLN_PROD_WEEKDAY',
            'SAS_DK_CNLN_PROD_WEEKEND_HOLIDAY': 'CNLN_PROD_WEEKEND', 
            'SAS_DK_CNLN_PROD_SICK'         :'CNLN_PROD_SICK',
            'SAS_NO_CNLN_PROD_WEEKDAY'      :'CNLN_PROD_WEEKDAY',
            'SAS_NO_CNLN_PROD_WEEKEND_HOLIDAY':'CNLN_PROD_WEEKEND',
            'SAS_NO_CNLN_PROD_SICK'         :'CNLN_PROD_SICK',
            'SAS_SE_ABS_F7_DAG_CABIN_3_1_D' : 'F7' 
}

ACCOUNT_PAYCODES = (
    'SAS_NO_CMS_VA_PERFORMED', 
    'SAS_NO_CMS_VA1_PERFORMED',
    'SAS_NO_CMS_SOLD_CC',
    'SAS_NO_CMS_SOLD_FC',
    'SAS_NO_CMS_BOUGHT_FORCED',
    'SAS_NO_CMS_BOUGHT_FC',
    'SAS_NO_CMS_BOUGHT_FC',
    'SAS_NO_CMS_BOUGHT_8_FC',
    'SAS_NO_CMS_BOUGHT_8_CC',
    'SAS_NO_CMS_BOUGHT_BL',
    'SAS_DK_CMS_BOUGHT_FORCED',
    'SAS_DK_CMS_BOUGHT_CC',
    'SAS_DK_CMS_BOUGHT_FC',
    'SAS_DK_CMS_BOUGHT_8_CC',
    'SAS_DK_CMS_BOUGHT_8_FC',
    'SAS_DK_CMS_SOLD_FC',
    'SAS_DK_CMS_SOLD_CC',
    'SAS_DK_VACATION_D',
    'SAS_DK_VACATION_UNPAID_D',
    'SAS_DK_CMS_BOUGHT_BL',
    'SAS_SE_CMS_BOUGHT',
    'SAS_SE_CMS_BOUGHT_8',
    'SAS_SE_CMS_BOUGHT_FORCED',
    'SAS_SE_CMS_BOUGHT_BL',
    'SAS_SE_CMS_SOLD',
    'SAS_SE_CMS_CC_VA_PERFORMED',
    'SAS_SE_CMS_FD_VA_PERFORMED',
    'SAS_SE_CMS_UNPAID_VACATION',
    'SAS_DK_CNLN_SOLD_DAYOFF',   
    'SAS_NO_CNLN_SOLD_DAYOFF',
    'SAS_SE_ABS_F7_DAG_CABIN_3_1_D'
)

ROSTER_PAYCODES = (
    'SAS_DK_CMS_OT',
    'SAS_DK_CMS_OTFC',
    'SAS_DK_CMS_OT_CO_LATE_FC',
    'SAS_DK_CMS_TEMP_CREW_HOURS',
    'SAS_NO_CMS_OT',
    'SAS_NO_CMS_OTFC',
    'SAS_NO_CMS_OT_CO_LATE_FC',
    'SAS_NO_CMS_TEMPCREW',
    'SAS_SE_CMS_CALM_OTFC',
    'SAS_SE_CMS_OT_CO_LATE_FC',
    'SAS_SE_CMS_TEMPCREW',
    'SAS_SE_CMS_OVERTIME',
    'SAS_DK_CNLN_OT_45_50',
    'SAS_DK_CNLN_OT_50_PLUS',
    'SAS_NO_CNLN_OT_45_50',
    'SAS_DK_CNLN_LAND_DAY_OFF',
    'SAS_NO_CNLN_LAND_DAY_OFF',
    'SAS_NO_CNLN_OT_50_PLUS',
    'SAS_DK_CNLN_PROD_WEEKDAY',
    'SAS_DK_CNLN_PROD_WEEKEND_HOLIDAY',
    'SAS_DK_CNLN_PROD_SICK',
    'SAS_NO_CNLN_PROD_WEEKDAY',
    'SAS_NO_CNLN_PROD_WEEKEND_HOLIDAY',
    'SAS_NO_CNLN_PROD_SICK'

)

EVENT_FROM_ARTICLE_PAYCODES = {
	'OTRESCHED'		  :   'OT',
	'OTPT'            :   'OT',
	'OT_FC_CJ'        :   'OT',
	'OTFC'            :   'OT',
	'CALM_OTFC'       :   'OT',
	'OT'              :   'OT',
	'OTPTC'           :   'OT',
	'OT_FP_CJ'        :   'OT',
	'OT_CC_QA'        :   'OT',
	'OT_CO_LATE_FC'   :   'OT_LATE_CO',
	'VA_REMAINING'    :	  'VA',
	'VA_PERFORMED'	  :	  'VA',
	'VA_REMAINING_YR' :	  'VA',
	'VA1_PERFORMED'   :	  'VA1',
	'TEMPCREW'		  :		'TEMP',
	'TEMPDAY'         :		'TEMP',
	'ILLTEMPCREW'     :		'TEMP',
	'TEMP_CC_QA'      :		'TEMP',
	'TEMPCREWOT'      :		'TEMP',
	'BOUGHT_FORCED'   :		'BOUGHT_FORCED',
    'BOUGHT_BL'		  :		'BOUGHT_BL',
	'BOUGHT_8_CC'		:	'BOUGHT_8',
	'BOUGHT_8'			:	'BOUGHT_8',
	'BOUGHT_8_FC'		:	'BOUGHT_8',
	'BOUGHT_COMP'		:	'BOUGHT',
	'BOUGHT_QA_FC_COMP'	:   'BOUGHT',
	'BOUGHT_CC'         :   'BOUGHT',
	'BOUGHT_FC'         :   'BOUGHT',
	'BOUGHT'            :   'BOUGHT',
	'BOUGHT_CC_QA'      :   'BOUGHT',
	'BOUGHT_QA_FP_COMP' :   'BOUGHT',
	'SOLD_FC'			:	'SOLD',
	'SOLD_CC_QA'		:	'SOLD',
	'SOLD'				:	'SOLD',
	'SOLD_CC'			:	'SOLD',
	'F7S_CC'			:	'F7s',
	'F7S_FC'			:	'F7s',
	'F7S'				:	'F7s',
	'F0_F3_FC'			:	'F3',
	'F0_F3_CC'          :	'F3',
	'F0_F3'             :	'F3',
    'CNLN_OT_45_50'     :   'CNLN_OT_45_50',
    'CNLN_LAND_DAY_OFF' :   'CNLN_LAND_DAY_OFF',
    'CNLN_OT_50_PLUS'   :   'CNLN_OT_50_PLUS',
    'CNLN_PROD_WEEKDAY' :   'CNLN_PROD_WEEKDAY',
    'CNLN_PROD_WEEKEND': 'CNLN_PROD_WEEKEND',
    'CNLN_PROD_SICK'    :   'CNLN_PROD_SICK',
    'ABS_F7_DAG_CABIN_3_1' : 'ABS_F7_DAG_CABIN_3_1_D'
	}


class PaycodeHandler:

    def _run_tests(self):
        print('Running tests ...')
        ot_dk_cc = self.paycode_from_event('OT', '12345', 'DK', 'CC')
        assert ot_dk_cc == 'SAS_DK_CMS_OT', 'Paycode should be SAS_DK_CMS_OT, was {0}'.format(ot_dk_cc)
        print('Asserted that self.paycode_from_event(OT, 12345, DK, CC) == {0}'.format(ot_dk_cc))
        ot_no_fc = self.paycode_from_event('OT', '12345', 'NO', 'FC')
        assert ot_no_fc == 'SAS_NO_CMS_OTFC','Paycode should be SAS_NO_CMS_OTFC, was {0}'.format(ot_no_fc)
        print('Asserted that self.paycode_from_event(OT, 12345, NO, FC) == {0}'.format(ot_no_fc)) 
        ot_se_lateco_fc = self.paycode_from_event('OT_LATE_CO', '12345', 'SE', 'FC')
        assert ot_se_lateco_fc == 'SAS_SE_CMS_OT_CO_LATE_FC', 'Paycode should be SAS_SE_CMS_OT_CO_LATE_FC, was {0}'.format(ot_no_fc)
        print('Asserted that self.paycode_from_event(OT_LATE_CO, 12345, SE, FC) == {0}'.format(ot_se_lateco_fc))
        va_se_fc = self.paycode_from_event('VA', '12345', 'SE', 'FC')
        assert va_se_fc == 'SAS_SE_CMS_FD_VA_PERFORMED', 'Paycode should be SAS_SE_CMS_FD_VA_PERFORMED, was {0}'.format(va_se_fc)
        print('Asserted that self.paycode_from_event(VA, 12345, SE, FC) == {0}'.format(va_se_fc))
        va_se_cc = self.paycode_from_event('VA', '12345', 'SE', 'CC')
        assert va_se_cc == 'SAS_SE_CMS_CC_VA_PERFORMED', 'Paycode should be SAS_SE_CMS_CC_VA_PERFORMED, was {0}'.format(va_se_cc)
        print('Asserted that self.paycode_from_event(VA, 12345, SE, CC) == {0}'.format(va_se_cc))
        print('All tests ran OK')
   
    def paycode_from_event(self, event_type, crew_id, country, rank):
        
        if event_type in ('OT', 'OT_LATE_CO') or (event_type == 'VA' and country == 'SE'):
            return PAYCODE_FROM_EVENT['{e}_{c}_{r}'.format(e=event_type, c=country, r=rank)]
        elif event_type in ('VA', 'VA1', 'TEMP', 'BOUGHT_FORCED', 'BOUGHT_BL'):
            return PAYCODE_FROM_EVENT['{e}_{c}'.format(e=event_type, c=country)]
        elif event_type in ('BOUGHT', 'BOUGHT_8', 'F7S', 'SOLD'):
            rank = '_{r}'.format(r=rank) if country in ('NO', 'DK') else ''
            return PAYCODE_FROM_EVENT['{e}_{c}{r}'.format(e=event_type, c=country, r=rank)]
        elif event_type in ('CNLN_SOLD'):
            return PAYCODE_FROM_EVENT['{e}_{c}'.format(e=event_type, c=country)]
        elif event_type in ('F3',):
            rank = '_{r}'.format(r=rank) if country in ('NO', 'DK') else ''
            return PAYCODE_FROM_EVENT['F0_{e}_{c}{r}'.format(e=event_type, c=country, r=rank)]
        elif event_type in ('CNLN_OT_45_50', 'CNLN_OT_50_PLUS', 'CNLN_LAND_DAY_OFF','CNLN_PROD_WEEKEND','CNLN_PROD_WEEKDAY','CNLN_PROD_SICK'):
            return PAYCODE_FROM_EVENT['{e}_{c}'.format(e=event_type, c=country)]
        elif event_type in ('F7',):
            rank = '_{r}'.format(r=rank) if country in ('NO', 'DK', 'SE') else ''
            return PAYCODE_FROM_EVENT['{e}_{c}{r}'.format(e=event_type, c=country, r=rank)]
        elif event_type in ('ABS_F7_DAG_CABIN_3_1_D') and country in ('SE') and rank in ('CC'):
            return PAYCODE_FROM_EVENT['{e}_{c}'.format(e=event_type, c=country)]
        else:
            return ''

    def event_from_paycode(self, paycode):
        return EVENT_FROM_PAYCODE[paycode]

    def is_account_paycode(self, paycode):
        return paycode in ACCOUNT_PAYCODES

    
    def event_from_article_paycode(self,paycode):
        if paycode in EVENT_FROM_ARTICLE_PAYCODES.keys():
            return EVENT_FROM_ARTICLE_PAYCODES[paycode]
        else:
            return ''


if __name__ == '__main__':
    ph = PaycodeHandler()
    ph._run_tests()        
