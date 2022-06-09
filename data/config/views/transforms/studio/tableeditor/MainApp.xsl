<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Removes parts not applicable to the use case. -->
   
  <!-- We always need the identity transform -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- Remove the "All tables" tab -->     
  <xsl:template match="box[@id = 'all_tables_container']" />

  <!-- BZ 39290 No saving in studio -->
  <xsl:template match="head/on-closing"/>
  
</xsl:stylesheet>
 
