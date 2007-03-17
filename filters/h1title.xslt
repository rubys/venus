<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <!-- Replace title with value of h1, if present -->
  <xsl:template match="atom:title">
    <xsl:apply-templates select="@*"/>
    <xsl:copy>
      <xsl:choose>
        <xsl:when test="count(//xhtml:h1) = 1">
          <xsl:value-of select="normalize-space(//xhtml:h1)"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates select="node()"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>

  <!-- Remove all h1s -->
  <xsl:template match="xhtml:h1"/>

  <!-- pass through everything else -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
