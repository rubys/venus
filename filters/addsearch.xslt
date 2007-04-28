<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns="http://www.w3.org/1999/xhtml">

  <!-- insert search form -->
  <xsl:template match="xhtml:div[@id='sidebar']">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <h2>Search</h2>
      <form><input name="q"/></form>
    </xsl:copy>
  </xsl:template>

  <!-- function to return baseuri of a given string -->
  <xsl:template name="baseuri">
    <xsl:param name="string" />
    <xsl:if test="contains($string, '/')">
      <xsl:value-of select="substring-before($string, '/')"/>
      <xsl:text>/</xsl:text>
      <xsl:call-template name="baseuri">
        <xsl:with-param name="string">
          <xsl:value-of select="substring-after($string, '/')"/>
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!-- insert opensearch autodiscovery link -->
  <xsl:template match="xhtml:head">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <link rel="search" type="application/opensearchdescription+xml" title="{xhtml:link[@rel='alternate']/@title} search">
        <xsl:attribute name="href">
          <xsl:call-template name="baseuri">
            <xsl:with-param name="string">
              <xsl:value-of select="xhtml:link[@rel='alternate']/@href"/>
            </xsl:with-param>
          </xsl:call-template>
          <xsl:text>opensearchdescription.xml</xsl:text>
        </xsl:attribute>
      </link>
    </xsl:copy>
  </xsl:template>

  <!-- ensure that scripts don't use empty tag syntax -->
  <xsl:template match="xhtml:script">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
      <xsl:if test="not(node())">
         <xsl:comment><!--HTML Compatibility--></xsl:comment>
      </xsl:if>
    </xsl:copy>
  </xsl:template>

  <!-- add HTML5 doctype -->
  <xsl:template match="/xhtml:html">
    <xsl:text disable-output-escaping="yes">&lt;!DOCTYPE html&gt;</xsl:text>
    <xsl:copy>
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
