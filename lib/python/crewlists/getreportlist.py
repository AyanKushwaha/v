
# changelog
# [acosta:07/078@14:01] First version
# [acosta:07/129@13:25] Restructured, moved.

"""
Interface R1.
Returns a list of available reports.

For details, see spec for interface R1
"""

###############################################################################
#  Note! This report is hard-coded.  It is very important to follow the       #
#  syntax described in the interface specification.                           # 
#                                                                             #
#  Note also that the parameter 'optional' has to it's meaning reversed!      #
#  optional = true means that the parameter is MANDATORY!                     #
###############################################################################
collection = """response to GetReportList, 0
<?xml version="1.0" encoding="UTF-8"?>
<replyBody version="1.0">
    <requestName>GetReportList</requestName>
    <statusCode>0</statusCode>
    <statusText>Ok</statusText>
    <getReportListReply>
        <empno>%s</empno>
        <reportCollection>
            <report>
                <reportId>DUTYCALC</reportId>
                <parameters>
                    <parameter>
                        <type>DATE</type>
                        <optional>false</optional>
                        <leadingText>Start Date</leadingText>
                    </parameter>
                    <parameter>
                        <type>DATE</type>
                        <optional>false</optional>
                        <leadingText>End Date</leadingText>
                    </parameter>
                </parameters>
                <shortName>Duty Calculation</shortName>
                <reportInfo>This report displays Crew Overtime and Allowances</reportInfo>
            </report>
            <report>
                <reportId>DUTYOVERTIME</reportId>
                <parameters>
                    <parameter>
                        <type>MONTH</type>
                        <optional>false</optional>
                        <leadingText>Salary Month</leadingText>
                    </parameter>
                    <parameter>
                        <type>YEAR</type>
                        <optional>false</optional>
                        <leadingText>Salary Year</leadingText>
                    </parameter>
                </parameters>
                <shortName>Duty Overtime</shortName>
                <reportInfo>This report displays Crew Overtime and Allowances</reportInfo>
            </report>
            <report>
                <reportId>CREWSLIP</reportId>
                <parameters>
                    <parameter>
                        <type>MONTH</type>
                        <optional>false</optional>
                        <leadingText>Month</leadingText>
                    </parameter>
                    <parameter>
                        <type>YEAR</type>
                        <optional>false</optional>
                        <leadingText>Year</leadingText>
                    </parameter>
                </parameters>
                <shortName>Crew Slip (Monthly Roster)</shortName>
                <reportInfo>This report displays a Crew Slip (Monthly Roster) for the given year and month.</reportInfo>
            </report>
            <report>
                <reportId>VACATION</reportId>
                <parameters>
                    <parameter>
                        <type>TYPE</type>
                        <optional>false</optional>
                        <leadingText>Type</leadingText>
                        <paramValues>
                          <value>F7</value> 
                          <value>VA1</value> 
                          <value>VA</value> 
                          <value>VA_SAVED1</value> 
                        </paramValues>
                    </parameter>
                    <parameter>
                        <type>YEAR</type>
                        <optional>false</optional>
                        <leadingText>Year</leadingText>
                    </parameter>
                </parameters>
                <shortName>Vacation and Balances</shortName>
                <reportInfo>This report displays Vacation and F7 days, balances and postings.</reportInfo>
            </report>
            <report>
                <reportId>COMPDAYS</reportId>
                <parameters>
                    <parameter>
                        <type>TYPE</type>
                        <optional>false</optional>
                        <leadingText>Type</leadingText>
                        <paramValues>
                          <value>F7S</value> 
                          <value>F0</value> 
                          <value>F15</value>
                          <value>F16</value>
                          <value>F3</value>
                          <value>F3S</value>
                          <value>F31</value>
                          <value>F32</value>
                          <value>F33</value> 
                          <value>F35</value> 
                          <value>F38</value>
			  <value>F89</value> 
                          <value>F9</value>
                        </paramValues>
                    </parameter>
                    <parameter>
                        <type>YEAR</type>
                        <optional>false</optional>
                        <leadingText>Year</leadingText>
                    </parameter>
                </parameters>
                <shortName>Compensation Days</shortName>
                <reportInfo>This report displays Compensation days, balances and postings.</reportInfo>
            </report>
            <report>
                <reportId>BOUGHTDAYS</reportId>
                <parameters>
                    <parameter>
                        <type>TYPE</type>
                        <optional>false</optional>
                        <leadingText>Type</leadingText>
                        <paramValues>
                          <value>Bought&gt;6 hrs</value> 
                          <value>Bought BL</value>
                          <value>Bought+F3</value>
                          <value>Bought&lt;=6 hrs</value>
                          <value>Bought=F3S</value>
                        </paramValues>
                    </parameter>
                    <parameter>
                        <type>YEAR</type>
                        <optional>false</optional>
                        <leadingText>Year</leadingText>
                    </parameter>
                </parameters>
                <shortName>Bought Days</shortName>
                <reportInfo>This report displays bought days, balances and postings.</reportInfo>
            </report>
            <report>
                <reportId>PILOTLOGCREW</reportId>
                <parameters>
                    <parameter>
                        <type>MONTH</type>
                        <optional>false</optional>
                        <leadingText>Month</leadingText>
                    </parameter>
                    <parameter>
                        <type>YEAR</type>
                        <optional>false</optional>
                        <leadingText>Year</leadingText>
                    </parameter>
                </parameters>
                <shortName>Pilot Log - Flight Activities</shortName>
                <reportInfo>This report displays flight activites.</reportInfo>
            </report>
            <report>
                <reportId>PILOTLOGFLIGHT</reportId>
                <parameters>
                    <parameter>
                        <type>TEXT</type>
                        <optional>false</optional>
                        <leadingText>Flight</leadingText>
                    </parameter>
                    <parameter>
                        <type>DATE</type>
                        <optional>false</optional>
                        <leadingText>Date</leadingText>
                    </parameter>
                </parameters>
                <shortName>Pilot Log - Flight</shortName>
                <reportInfo>This report displays log entries for a specific flight.</reportInfo>
            </report>
            <report>
                <reportId>PILOTLOGSIM</reportId>
                <parameters>
                    <parameter>
                        <type>MONTH</type>
                        <optional>false</optional>
                        <leadingText>Month</leadingText>
                    </parameter>
                    <parameter>
                        <type>YEAR</type>
                        <optional>false</optional>
                        <leadingText>Year</leadingText>
                    </parameter>
                </parameters>
                <shortName>Pilot Log - Simulator</shortName>
                <reportInfo>This report displays simulator activies.</reportInfo>
            </report>
            <report>
                <reportId>PILOTLOGACCUM</reportId>
                <parameters>
                </parameters>
                <shortName>Pilot Log - Accumulated</shortName>
                <reportInfo>This report displays accumulated pilot log information.</reportInfo>
            </report>
        </reportCollection>
    </getReportListReply>
</replyBody>"""


# report
def report(requestName='GetReportList', empno=""):
    """ 
    Will return a list of available reports.
    """
    try:
        return collection % (empno,)
    except:
        # If this fails, then... :-)
        raise


# main
# For basic tests
if __name__ == '__main__':
    print report()
