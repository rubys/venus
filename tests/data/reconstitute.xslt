<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:planet="http://planet.intertwingly.net/"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns="http://www.w3.org/1999/xhtml">

  <!-- indent atom and planet elements -->
  <xsl:template match="atom:*|planet:*">
    <!-- double space before atom:entries and planet:source -->
    <xsl:if test="self::atom:entry | self::planet:source">
      <xsl:text>&#10;</xsl:text>
    </xsl:if>

    <!-- indent start tag -->
    <xsl:text>&#10;</xsl:text>
    <xsl:for-each select="ancestor::*">
      <xsl:text>  </xsl:text>
    </xsl:for-each>

    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
 
      <!-- indent end tag if there are element children -->
      <xsl:if test="*">
        <xsl:text>&#10;</xsl:text>
        <xsl:for-each select="ancestor::*">
          <xsl:text>  </xsl:text>
        </xsl:for-each>
      </xsl:if>
    </xsl:copy>
  </xsl:template>

  <!-- pass through everything else -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
