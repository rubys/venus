<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:planet="http://planet.intertwingly.net/"
                xmlns="http://www.w3.org/1999/xhtml">
 
  <xsl:template match="atom:feed">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <link rel="stylesheet" href="planet.css" type="text/css" />
        <title><xsl:value-of select="atom:title"/></title>
      </head>
      <body>
        <h1><xsl:value-of select="atom:title"/></h1>

        <xsl:apply-templates select="atom:entry"/>

        <div class="sidebar">
          <img src="images/logo.png" width="136" height="136" alt=""/>

          <h2>Subscriptions</h2>
          <ul>
            <xsl:for-each select="planet:source">
              <xsl:sort select="planet:name"/>
              <li>
                <a href="{atom:link[@rel='self']/@href}" title="subscribe">
                  <img src="images/feed-icon-10x10.png" alt="(feed)"/>
                </a>
                <a href="{atom:link[@rel='alternate']/@href}">
                  <xsl:value-of select="planet:name"/>
                </a>
              </li>
            </xsl:for-each>
          </ul>
        </div>
      </body>
    </html>
  </xsl:template>
 
  <xsl:template match="atom:entry">
    <xsl:variable name="date" select="substring(atom:updated,1,10)"/>
    <xsl:if test="not(preceding-sibling::atom:entry
      [substring(atom:updated,1,10) = $date])">
      <h2 class="date"><xsl:value-of select="$date"/></h2>
    </xsl:if>

    <h3>
      <a href="{atom:source/atom:link[@rel='alternate']/@href}">
        <xsl:value-of select="atom:source/planet:name"/>
      </a>
        &#x2014;
      <a href="{atom:link[@rel='alternate']/@href}">
        <xsl:value-of select="atom:title"/>
      </a>
    </h3>

    <div class="content">
      <xsl:choose>
        <xsl:when test="atom:content">
          <xsl:copy-of select="atom:content/*"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy-of select="atom:summary/*"/>
        </xsl:otherwise>
      </xsl:choose>
    </div>
  </xsl:template>
</xsl:stylesheet>
