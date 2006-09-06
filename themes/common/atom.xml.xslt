<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:indexing="urn:atom-extension:indexing"
                xmlns:planet="http://planet.intertwingly.net/"
                xmlns="http://www.w3.org/1999/xhtml">

  <!-- strip planet elements and attributes -->
  <xsl:template match="planet:*|@planet:*"/>

  <!-- strip obsolete link relationships -->
  <xsl:template match="atom:link[@rel='service.edit']"/>
  <xsl:template match="atom:link[@rel='service.post']"/>

  <!-- add Google/LiveJournal-esque noindex directive -->
  <xsl:template match="atom:feed">
    <xsl:copy>
      <xsl:attribute name="indexing:index">no</xsl:attribute>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- indent atom elements -->
  <xsl:template match="atom:*">
    <!-- double space before atom:entries -->
    <xsl:if test="self::atom:entry">
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
