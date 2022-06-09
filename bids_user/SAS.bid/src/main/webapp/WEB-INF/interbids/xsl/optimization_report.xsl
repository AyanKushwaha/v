<?xml version='1.0' encoding='iso-8859-1'?>
<xsl:stylesheet version='1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
    <xsl:output method='html' encoding='ISO-8859-1' indent='no'/>
    <xsl:template match='/'>
        <xsl:apply-templates select='//failed'/>
        <xsl:apply-templates select='//request'/>
        <xsl:apply-templates select='//requestData'/>
        <xsl:apply-templates select='//referenceData'/>
        <xsl:apply-templates select='//response'/>
    </xsl:template>

    <xsl:template match='failed'>
        <b>Unable to process the optimization request:</b> <xsl:value-of select="."/><p/>
    </xsl:template>
    
    <xsl:template match='request'>
        <b>Optimization Request Report</b><p/>
    </xsl:template>
    
    <xsl:template match='requestData'>
    	<b>ETAB</b><br/>
		<pre>
        <xsl:value-of select="."/>
		</pre>
    </xsl:template>

    <xsl:template match='referenceData'>
        <b>REF DATA</b><br/>
        <pre>
        <xsl:value-of select="."/>
        </pre>
    </xsl:template>
    
    <xsl:template match='response'>
        <table>
            <tr>
                <td colspan='2'>
                    <b>
                        Max Roster Summary
                    </b>
                </td>
            </tr>
            <tr>
                <td>
                    Block Time:
                </td>
                <td>
                    <xsl:value-of select='//ROSTERS/ROSTER/@blocktime'/>
                </td>
            </tr>
            <tr>
                <td>
                    Duty Time:
                </td>
                <td>
                    <xsl:value-of select='//ROSTERS/ROSTER/@dutytime'/>
                </td>
            </tr>
            <tr>
                <td>
                    Start:
                </td>
                <td>
                    <xsl:value-of select='//ROSTERS/ROSTER/@periodstartdate'/>
                </td>
            </tr>
            <tr>
                <td>
                    End:
                </td>
                <td>
                    <xsl:value-of select='//ROSTERS/ROSTER/@periodenddate'/>
                </td>
            </tr>
        </table>
		
		<p/>
		<table border='1'>
            <tr>
                <td colspan='6'>
                    <b>
                        Max Roster Details
                    </b>
                </td>
            </tr>
            <tr>
                <th style="text-align:left;padding-right:20px;">Type</th>
                <th style="text-align:left;margin-right:20px;">CRR ID</th>
                <th style="text-align:left;margin-right:20px;">Start</th>
                <th style="text-align:left;padding-right:20px;">End</th>
                <th style="text-align:left;margin-right:20px;">Duty</th>
                <th style="text-align:left;margin-right:20px;">Block</th>
            </tr>
			
			<xsl:apply-templates select="//ROSTERS/ROSTER/CRR" /> 

	   </table>
			
		<!--CRR type='flight' crrid='3262' startdate='18Oct2004' starttime='09:20' enddate='21Oct2004' endtime='23:05' dutytime='39:25' blocktime='24:25'/-->

		
    </xsl:template>
	
	<xsl:template match="CRR">
		<tr>
			<td><xsl:value-of select='@type'/></td>
            <td><xsl:value-of select='@crrid'/></td>
            <td><xsl:value-of select='@startdate'/><xsl:text> </xsl:text><xsl:value-of select='@starttime'/></td>
            <td><xsl:value-of select='@enddate'/><xsl:text> </xsl:text><xsl:value-of select='@endtime'/></td>
            <td><xsl:value-of select='@dutytime'/></td>
            <td><xsl:value-of select='@blocktime'/></td>
	   </tr>
    </xsl:template>
</xsl:stylesheet>
