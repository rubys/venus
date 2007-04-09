<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <!-- If the first paragraph consists contains @class="from", delete it -->
  <xsl:template match="atom:content/xhtml:div/xhtml:div[@class='comment']/xhtml:p[1][@class='from']"/>

  <!-- pass through everything else -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
