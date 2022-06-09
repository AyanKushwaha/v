<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Removes actions that control the client <-> server state. -->
   
  <!-- We always need the identity transform -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- Remove the unwanted buttons -->     
  <xsl:template match="button[@id = 'load_branch']" />
  <!--xsl:template match="separator[@id = 'before_client_controls']" /-->
  <!--xsl:template match="button[@id = 'submit']" /-->              <!-- submit modifications to model -->
  <!--xsl:template match="button[@id = 'refresh_client']" /--> <!-- refresh client with changes in model -->
  <xsl:template match="button[@id = 'save']" />                <!-- save model changes to database -->
  <xsl:template match="button[@id = 'refresh_model']" />       <!-- refresh model from database -->

</xsl:stylesheet>
 
