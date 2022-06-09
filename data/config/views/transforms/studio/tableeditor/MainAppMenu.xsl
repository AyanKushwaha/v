<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Removes actions that control the client <-> server state. -->
   
  <!-- We always need the identity transform -->
  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- Remove the unwanted menu items -->     
  <xsl:template match="menu-item[@id = 'load_branch']" />
  <xsl:template match="separator[@id = 'above_open_table']" />
  <xsl:template match="separator[@id = 'below_open_table']" />
  <xsl:template match="menu-item[@id = 'open_table']" />
  <!--xsl:template match="menu-item[@id = 'submit']" /-->         <!-- submit modifications to model -->
  <!--xsl:template match="menu-item[@id = 'refresh_client']" /--> <!-- refresh client with changes in model -->
  <xsl:template match="menu-item[@id = 'save']"/>           <!-- save model changes to database -->
  <xsl:template match="menu-item[@id = 'save_with_message']"/>           <!-- save model changes to database -->
  <xsl:template match="menu-item[@id = 'refresh_model']"/>  <!-- refresh model from database -->

  <!-- Dropping entire view menu, as it only contains preferences  -->
  <!-- <xsl:template match="menu-item[@id = 'preferences']" /> --> <!-- preferences dialog -->
  <!-- <xsl:template match="separator[@id = 'above_preferences']" /> -->
  <xsl:template match="menu[@id = 'view_menu']" /> <!-- entire view menu -->

  <!-- BZ 39290 No saving in studio -->
  <xsl:template match="menu-item[@id = 'exit']/on-click">
    <xsl:element name="on-click">
      closeForm();
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>
 
