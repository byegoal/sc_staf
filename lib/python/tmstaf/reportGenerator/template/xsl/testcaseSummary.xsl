<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/testsuite">
<html>
	<head>
		<title><xsl:value-of select="name" /></title>
		<link href="../word.css" rel="stylesheet" type="text/css"/>
	</head>
	<body bgcolor="#ffffff">
		<A HREF="javascript:javascript:history.go(-1)">Back</A>&#160;&#160;<a href="../main.html">Home</a>
		<br/><br/>
		<strong class="word">Testsuite Summary:</strong><br/>
		<table border="1" cellpadding="0" cellspacing="0" width="70%">
		<tr>
			<td class="forTitleTDWithoutHand"><span class="forTitleFont">Name</span></td>
			<td class="forTitleTDWithoutHand"><span class="forTitleFont">Number Of TestCase</span></td>
			<td class="forTitleTDWithoutHand"><span class="forTitleFont">Starts</span></td>
			<td class="forTitleTDWithoutHand"><span class="forTitleFont">Passes</span></td>
			<td class="forTitleTDWithoutHand"><span class="forTitleFont">Fails</span></td>
			<td class="forTitleTDWithoutHand"><span class="forTitleFont">Crashes</span></td>
			<td class="forTitleTDWithoutHand"><span class="forTitleFont">Elapsed Time</span></td>
		</tr>
		<tr>
			<td width="15%" class="forFieldTD">	<xsl:value-of select="suiteName" /></td>
			<td width="25%" class="forFieldTD">	<xsl:value-of select="count" /></td>
			<td width="10%" class="forFieldTD">	<xsl:value-of select="starts"/></td>
			<td width="10%" class="forFieldTD">	<xsl:value-of select="passes"/></td>
			<td width="10%" class="forFieldTD">	<xsl:value-of select="fails"/></td>
			<td width="10%" class="forFieldTD">	<xsl:value-of select="crashes"/></td>
			<td width="20%" class="forFieldTD">	<xsl:value-of select="elapsedTime"/></td>
		</tr>
		</table>
		<br/>
		<table cellpadding="2" border="0">
			<tr valign="middle">
				<td width="5%" nowrap="1"><strong class="word">Test Case List:</strong></td><td width="20%"></td>
				<td width="2%" nowrap="1">Pass:</td>
				<td width="10%"><img height="16" width="16" src="../icon/pass.jpg" /></td>
				<td width="2%" nowrap="1">Fail:</td>
				<td width="10%"><img height="16" width="16" src="../icon/fail.jpg" /></td>
				<td width="2%" nowrap="1">Crash:</td>
				<td><img height="16" width="16" src="../icon/crash.jpg" /></td>
			</tr>
		</table>
		<table border="1" cellpadding="0" cellspacing="0" width="100%">
		<tr>
			<td class="forTitleTDWithoutHand" nowrap="1"><span class="forTitleFont">#</span></td>
			<td class="forTitleTDWithoutHand" nowrap="1"><span class="forTitleFont">Result</span></td>
			<td class="forTitleTDWithoutHand" nowrap="1"><span class="forTitleFont">Name</span></td>
			<td class="forTitleTDWithoutHand" nowrap="1"><span class="forTitleFont">Scenario</span></td>
			<td class="forTitleTDWithoutHand" nowrap="1"><span class="forTitleFont">Elapsed Time</span></td>
			<td class="forTitleTDWithoutHand" nowrap="1"><span class="forTitleFont">Title</span></td>
		</tr>
		<xsl:for-each select="testResult">
		<xsl:sort select="name" data-type="text" order="ascending"/>
		<tr>
			<td width="2%" class="forFieldTD"><xsl:value-of select="position()" /></td>
			<td width="5%" align="center" valign="middle" class="forFieldTD">
				<xsl:if test="passes=1">
					<img alt="-" height="16" width="16" src="../icon/pass.jpg" />
				</xsl:if>
				<xsl:if test="fails=1">
						<img alt="-" height="16" width="16" src="../icon/fail.jpg" />
				</xsl:if>
				<xsl:if test="crashes=1">
						<img alt="-" height="16" width="16" src="../icon/crash.jpg" />
				</xsl:if>
				<xsl:if test="starts=0">
						N/A
				</xsl:if>
			</td>			
			<td width="10%" nowrap="1" class="forFieldTD">
				<span class="smallWord">
				<a>
				<xsl:attribute name="href"><xsl:value-of select="url" /></xsl:attribute>
				<xsl:attribute name="target"><xsl:text>right</xsl:text></xsl:attribute>
				<xsl:value-of select="name" />
				</a>
				</span>
			</td>
			<td width="15%" nowrap="1" class="forFieldTD">
			<span class="smallWord">
				<xsl:if test="scenario!=''">
				<xsl:value-of select="scenario" />
				</xsl:if>
				<xsl:if test="scenario=''">
				.
				</xsl:if>
			</span>
			</td>			
			<td width="10%" class="forFieldTD">
				<span class="smallWord">
				<xsl:value-of select="elapsedTime" />
				</span>
			</td>
			<td nowrap="1" class="forFieldTD">
				<span class="smallWord">
				<xsl:value-of select="title" />
				</span>
			</td>
		</tr>
		</xsl:for-each>
	</table>
	<br/>
	<A HREF="javascript:javascript:history.go(-1)">Back</A>&#160;&#160;<a href="../main.html">Home</a>
	</body>
</html>
</xsl:template>
</xsl:stylesheet>