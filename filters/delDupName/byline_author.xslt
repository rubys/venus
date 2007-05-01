<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xhtml="http://www.w3.org/1999/xhtml">

  <!-- Replace atom:author/atom:name with the byline author -->
  <xsl:template match="atom:entry/atom:author[../atom:content/xhtml:div/xhtml:span[@class='byline-author' and substring(.,1,10)='Posted by ']]">
    <xsl:copy>
      <atom:name>
       <xsl:value-of select="substring(../atom:content/xhtml:div/xhtml:span[@class='byline-author'],11)"/>
      </atom:name>
      <xsl:apply-templates select="*[not(self::atom:name)]"/>
    </xsl:copy>
  </xsl:template>

  <!-- Remove byline author -->
  <xsl:template match="xhtml:div/xhtml:span[@class='byline-author' and substring(.,1,10)='Posted by ']"/>

  <!-- Remove two line breaks following byline author -->
  <xsl:template match="xhtml:br[preceding-sibling::*[1][@class='byline-author' and substring(.,1,10)='Posted by ']]"/>
  <xsl:template match="xhtml:br[preceding-sibling::*[2][@class='byline-author' and substring(.,1,10)='Posted by ']]"/>

  <!-- pass through everything else -->
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
