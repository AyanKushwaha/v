<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html"/>

<xsl:template match="RaveProgram">
  <html>
  <head>
    <script>window.resizeTo(500,400);</script>
    <title>Rave Definitions</title>
    <style type="text/css">
      a:active       { color: #0000FF; text-decoration: none}
      a:hover        { color: #0000FF; text-decoration: none}
      a:link         { color: #0000FF; text-decoration: none}
      a:visited      { color: #0000FF; text-decoration: none}
      body           { background-color: #FFFFFF;}
      .pbody         { font-family: Arial, Verdana, Helvetica, sans-serif;
                       font-size: 11pt; font-style: normal;
                       font-variant: normal; font-weight: normal; }
      .psubsection   { color: #990033;
                       font-family: Arial, Verdana, Helvetica, sans-serif;
                       font-size: 16pt; font-style: normal;
                       font-variant: normal; font-weight: bold;
                       margin-top: 22px; margin-bottom: 6px; }
     .psubsubsection { color: #990033;
                       font-family: Arial, Verdana, Helvetica, sans-serif;
                       font-size: 12pt; font-style: normal;
                       font-variant: normal; font-weight: bold;
                       margin-top: 20px; margin-bottom: 3px; }
    </style>
  </head>
  <body>
    <h2 class="psubsection">Rave Definitions</h2>
    <h3 class="psubsubsection"><a name="index"></a>Index</h3>
    <p class="pbody">
    <xsl:apply-templates select="Module/Definition[not(Position[starts-with(@file, 'pac/')])
						   and not(Position[starts-with(@file, 'modules/matador')])
						   and not(Position[starts-with(@file, 'modules/apc_cas')])
						   and not(Remark[starts-with(@text, '#HEADER#')])
						   and Remark[@role='planner']
						   and not (Keyword)]" mode="index">

      <xsl:sort select="@text"/>
    </xsl:apply-templates>
    </p><hr/>
    <xsl:apply-templates select="Module/Definition[not(Position[starts-with(@file, 'pac/')])
						   and not(Position[starts-with(@file, 'modules/matador')])
						   and not(Position[starts-with(@file, 'modules/apc_cas')])
						   and not(Remark[starts-with(@text, '#HEADER#')])
						   and Remark[@role='planner']
						   and not (Keyword)]">
    </xsl:apply-templates>
  </body>
  </html>
</xsl:template>

<xsl:template match="Definition" mode="index">
  <xsl:element name="a">
    <xsl:attribute name="href">#<xsl:value-of select="../@name"/>.<xsl:value-of select="@name"/></xsl:attribute>
    <xsl:apply-templates select="Remark[@role='brief']"/>
  </xsl:element>
  <br/>
</xsl:template>

<xsl:template match="Definition">
  <h2 class="psubsection">
    <xsl:element name="a">
      <xsl:attribute name="name"><xsl:value-of select="../@name"/>.<xsl:value-of select="@name"/></xsl:attribute>
    </xsl:element>
        <xsl:choose>
          <xsl:when test="Remark[@role='brief']">
            <xsl:apply-templates select="Remark[@role='brief']"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="@name"/>
          </xsl:otherwise>
        </xsl:choose>

      </h2>
      <table cellpadding="2" cellspacing="4" border="0">
      <tbody>
      <tr>
        <td><p class="pbody"><b>Name</b></p></td>
        <td><p class="pbody"><xsl:value-of select="@name"/></p></td>
      </tr>
      <xsl:apply-templates select="Variable|Rule|ExternalTable|Set|Level|Iterator|Context|Transform|Keyword|Group"/>
      </tbody></table>
      <xsl:apply-templates select="Remark[@role='planner']"/>
      <p class="pbody"><a href="#index">Index</a></p>
     <hr/>
</xsl:template>

<xsl:template match="Variable">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/> (<xsl:value-of select="@type"/>)</p></td>
  </tr>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="Rule">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/></p></td>
  </tr>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="ExternalTable">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/></p></td>
  </tr>
</xsl:template>

<xsl:template match="Set">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/></p></td>
  </tr>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="Level">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/></p></td>
  </tr>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="Iterator">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/></p></td>
  </tr>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="Context">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/></p></td>
  </tr>
</xsl:template>

<xsl:template match="Transform">
  <p class="pbody"><b>Type: </b><xsl:value-of select="name()"/></p>
</xsl:template>

<xsl:template match="Keyword">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/> (<xsl:value-of select="@type"/>)</p></td>
  </tr>
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="Group">
  <tr>
  <td><p class="pbody"><b>Type</b></p></td>
  <td><p class="pbody"><xsl:value-of select="name()"/></p></td>
  </tr>
</xsl:template>

<xsl:template match="Remark[@role='brief']">
  <xsl:value-of select="@text"/>
</xsl:template>

<xsl:template match="Remark[@role='planner']">
  <h3 class="psubsubsection">Remark</h3>
  <p class="pbody"><xsl:value-of select="@text"/></p>
</xsl:template>

<xsl:template match="Range"/>

<xsl:template match="Parameter">
  <tr>
  <td style="vertical-align: top;"><p class="pbody"><b>Values</b></p></td>
  <td style="vertical-align: top;">
    <table cellpadding="2" cellspacing="0" border="0">
    <tbody>
    <tr>
      <td style="vertical-align: top;"><p class="pbody">Default: </p></td>
      <td style="vertical-align: top;"><p class="pbody"><xsl:value-of select="@defaultValue"/></p></td>
    </tr>
    </tbody>
    </table>
  </td>
  </tr>
</xsl:template>

</xsl:stylesheet>
