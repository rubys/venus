<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:planet="http://planet.intertwingly.net/"
                exclude-result-prefixes="atom planet">
 
  <xsl:output indent="yes" method="xml"/>

  <xsl:template match="atom:feed">
    <opml version="1.1">
      <head>
        <title><xsl:value-of select="atom:title"/></title>
        <dateModified><xsl:value-of select="atom:updated/@planet:format"/></dateModified>
        <ownerName><xsl:value-of select="atom:author/atom:name"/></ownerName>
        <ownerEmail><xsl:value-of select="atom:author/atom:email"/></ownerEmail>
      </head>

      <body>
        <xsl:for-each select="planet:source">
          <outline type="rss" text="{planet:name}" title="{atom:title}"
            xmlUrl="{atom:link[@rel='self']/@href}"/>
        </xsl:for-each>
      </body>
    </opml>
  </xsl:template>
</xsl:stylesheet>
