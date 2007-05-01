<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <!-- If the first paragraph consists exclusively of "By author-name",
       delete it -->
  <xsl:template match="atom:content/xhtml:div/xhtml:p[1][. =
    concat('By ', ../../../atom:author/atom:name)]"/>

  <!-- pass through everything else -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
