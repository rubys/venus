<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:indexing="urn:atom-extension:indexing"
                xmlns:planet="http://planet.intertwingly.net/"
                xmlns="http://www.w3.org/1999/xhtml">

  <!-- strip planet elements and attributes -->
  <xsl:template match="planet:*"/>

  <!-- add Google/LiveJournal-esque noindex directive -->
  <xsl:template match="atom:feed">
    <xsl:copy>
      <xsl:attribute name="indexing:index">no</xsl:attribute>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- pass through everything else -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
