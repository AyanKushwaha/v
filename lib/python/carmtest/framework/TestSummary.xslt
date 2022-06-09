<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" indent="yes"/> 
 
  <xsl:template match="/TestRun">
    <html>
      <head>
        <title>Test report</title>
        <style type="text/css">
        body {font-family: Tahoma, Sans;}
        h1 {font-size: 12pt; margin-left: 0px;}
        h2 {font-size: 10pt; margin-left: 10px;}
        h3 {font-size: 8pt; margin-left: 20px;}
        p, div {font-size: 8pt; margin-left: 30px;}
        .skip {border: 1px solid #909000;
        background-color: #ffffc0;
        color: #909000}
        .error {border: 1px solid red;
        background-color: #ffc0c0;
        color: #900000}
        .dataError {border: 1px solid #c09000;
        background-color: #ffd0c0;
        color: #c09000}
        .sevInfo {color: #909090}
        .sevWarn {color: #c09000}
        .sevError {color: #c00000}
        .sevSkip {color: #c0c000}
        .sevOk {color: #00c000}
        </style>
      </head>
      <body>
      	<h1>Test run for <xsl:value-of select="@filterString" /></h1>
      	<p>Tests started <xsl:value-of select="@date" /></p>
        <xsl:apply-templates select="TestFixture"/>
      </body> 
    </html>
  </xsl:template>
 
  <xsl:template match="TestFixture">
    <h2><xsl:value-of select="@category" /> / <xsl:value-of select="@module" /> / <xsl:value-of select="@name" /> : 
    	<xsl:choose>
    		<xsl:when test="Prerequisites/Error[@type='skip']">
    		<span class="sevSkip">Skipped</span>
    		</xsl:when>
    		<xsl:when test="Prerequisites/Error">
    		<span class="sevError">Errors</span>
    		</xsl:when>
    		<xsl:when test="TestCase/Test/Result[text()='Failure']">
    		<span class="sevError">Errors</span>
    		</xsl:when>
    		<xsl:when test="TestCase/Test/Result[text()='Success']">
    		<span class="sevOk">Success</span>
    		</xsl:when>
    		<xsl:otherwise>
    		<span class="sevSkip">No tests</span>
    		</xsl:otherwise>
    	</xsl:choose>
    	</h2>
        <xsl:apply-templates select="Prerequisites"/>
        <xsl:apply-templates select="TestCase"/>
  </xsl:template>
 
  <xsl:template match="TestCase">
    <h3><xsl:value-of select="@name" /> : 
	<xsl:choose>
    	<xsl:when test="Test/Result[text()='Failure']">
    		<span class="sevError">Failure</span>
    	</xsl:when>
    	<xsl:when test="Test/Result[text()='Success']">
    		<span class="sevOk">Success</span>
    	</xsl:when>
    	<xsl:otherwise>
    		<span class="sevSkip">No result</span>
    	</xsl:otherwise>
    </xsl:choose>
    </h3>
    <xsl:apply-templates match="SetUp|Test|TearDown"/>
  </xsl:template>
 
  <xsl:template match="Prerequisites">
    <xsl:apply-templates/>
  </xsl:template>
 
  <xsl:template match="SetUp">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="Result"/>
 
  <xsl:template match="Log"/>
 
  <xsl:template match="Error"/>
  
  <xsl:template match="Measurements"/>
 
</xsl:stylesheet>