<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:param name="in"/>
  <xsl:param name="out"/>

  <!-- translate $in characters to $out in attribute values -->
  <xsl:template match="@*">
    <xsl:attribute name="{name()}">
      <xsl:value-of select="translate(.,$in,$out)"/>
    </xsl:attribute>
  </xsl:template>

  <!-- pass through everything else -->
  <xsl:template match="node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>

