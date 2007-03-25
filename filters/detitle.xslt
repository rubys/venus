<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns="http://www.w3.org/1999/xhtml">

  <!-- only retain titles that don't duplicate summary or content -->
  <xsl:template match="atom:title">
    <xsl:copy>
      <xsl:if test="string-length(.) &lt; 30 or
                    ( substring(.,1,string-length(.)-3) !=
                      substring(../atom:content,1,string-length(.)-3) and
                      substring(.,1,string-length(.)-3) !=
                      substring(../atom:summary,1,string-length(.)-3) )">
        <xsl:apply-templates select="@*|node()"/>
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
