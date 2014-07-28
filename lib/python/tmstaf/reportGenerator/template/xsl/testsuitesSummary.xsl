<html xsl:version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" lang="en">
    <head>
			<title>List of testsuits</title>
			<link href="word.css" rel="stylesheet" type="text/css"/>
    </head>
    <body bgcolor="#ffffff">
		
		<table border="0" cellpadding="3" cellspacing="1">
			<tr>
				<td><b class="smallWord">Testsuite</b></td><td class="smallWord">(fail/start)</td>
			</tr>
			<xsl:for-each select="summary/testsuiteList/testsuite">
				<tr>
					<td nowrap="1">
		            <a>
		              <xsl:attribute name="href">
		              <xsl:value-of select="url" /> 
		              </xsl:attribute>
		              <xsl:attribute name="target">
		              <xsl:text>right</xsl:text>
		              </xsl:attribute>
		              <span class="smallWord">
		              <xsl:value-of select="name" /> 
		              </span>
		            </a>
		       	</td>
					<td>
					<span class="smallWord">
					(<font class="smallWord">
					<xsl:if test="starts &gt; passes">
					<xsl:attribute name="color">red</xsl:attribute>
					</xsl:if>
					<xsl:value-of select="totalFails"/>
					</font>/<xsl:value-of select="starts"/>)
					</span>
					</td>
				</tr>
			</xsl:for-each>
		</table>
		<br/>
		<b class="smallWord">Elapsed Time:</b><br/>
		<span class="smallWord">
		<xsl:value-of select="summary/totalElapsedTime" /></span> <br/>
		<br/>
		<b class="smallWord">Failed TestCases:</b><br/>
		<table border="0" cellpadding="1" cellspacing="0">
			<xsl:for-each select="summary/testCasesFailed/testcase">
			<xsl:sort select="testcase" data-type="text" order="ascending"/>
				<tr>
					<td nowrap="1">
		            <a>
		              <xsl:attribute name="href">
		              <xsl:value-of select="@url" /> 
		              </xsl:attribute>
		              <xsl:attribute name="target">
		              <xsl:text>right</xsl:text>
		              </xsl:attribute>
		              <span class="smallWord">
		              <xsl:value-of select="." />
		              </span>
						</a>
		       	</td>
				</tr>
			</xsl:for-each>
		</table>		
    </body>
</html>