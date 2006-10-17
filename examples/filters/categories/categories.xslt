<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
<!ENTITY categoryTerm "WebSemantique">
]>
<!-- 

  This transformation is released under the same licence as Python
  see http://www.intertwingly.net/code/venus/LICENCE.

  Author: Eric van der Vlist <vdv@dyomedea.com>
  
  This transformation is meant to be used as a filter that determines if
  Atom entries are relevant to a specific topic and adds the corresonding
  <category/> element when it is the case.
  
  This is done by a simple keyword matching mechanism.
  
  To customize this filter to your needs:
  
    1) Replace WebSemantique by your own category name in the definition of
        the categoryTerm entity above.
    2) Review the "upper" and "lower" variables that are used to convert text
        nodes to lower case and replace common ponctuation signs into spaces
        to check that they meet your needs.
    3) Define your own list of keywords in <d:keyword/> elements. Note that 
        the leading and trailing spaces are significant: "> rdf <" will match rdf
        as en entier word while ">rdf<" would match the substring "rdf" and
        "> rdf<" would match words starting by rdf. Also note that the test is done
        after conversion to lowercase.

  To use it with venus, just add this filter to the list of filters, for instance:
  
filters= categories.xslt guess_language.py
  
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom" xmlns="http://www.w3.org/2005/Atom"
  xmlns:d="http://ns.websemantique.org/data/" exclude-result-prefixes="d atom" version="1.0">
  <xsl:variable name="upper"
    >,.;AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZzÀàÁáÂâÃãÄäÅåÆæÇçÈèÉéÊêËëÌìÍíÎîÏïÐðÑñÒòÓóÔôÕõÖöØøÙùÚúÛûÜüÝýÞþ</xsl:variable>
  <xsl:variable name="lower"
    >   aabbccddeeffgghhiijjkkllmmnnooppqqrrssttuuvvwwxxyyzzaaaaaaaaaaaaææcceeeeeeeeiiiiiiiiððnnooooooooooøøuuuuuuuuyyþþ</xsl:variable>
  <d:keywords>
    <d:keyword> wiki semantique </d:keyword>
    <d:keyword> wikis semantiques </d:keyword>
    <d:keyword> web semantique </d:keyword>
    <d:keyword> websemantique </d:keyword>
    <d:keyword> semantic web</d:keyword>
    <d:keyword> semweb</d:keyword>
    <d:keyword> rdf</d:keyword>
    <d:keyword> owl </d:keyword>
    <d:keyword> sparql </d:keyword>
    <d:keyword> topic map</d:keyword>
    <d:keyword> doap </d:keyword>
    <d:keyword> foaf </d:keyword>
    <d:keyword> sioc </d:keyword>
    <d:keyword> ontology </d:keyword>
    <d:keyword> ontologie</d:keyword>
    <d:keyword> dublin core </d:keyword>
  </d:keywords>
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>
  <xsl:template match="atom:entry/atom:updated">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
    <xsl:variable name="concatenatedText">
      <xsl:for-each select="../atom:title|../atom:summary|../atom:content|../atom:category/@term">
        <xsl:text> </xsl:text>
        <xsl:value-of select="translate(., $upper, $lower)"/>
      </xsl:for-each>
      <xsl:text> </xsl:text>
    </xsl:variable>
    <xsl:if test="document('')/*/d:keywords/d:keyword[contains($concatenatedText, .)]">
      <category term="WebSemantique"/>
    </xsl:if>
  </xsl:template>
  <xsl:template match="atom:category[@term='&categoryTerm;']"/>
</xsl:stylesheet>
