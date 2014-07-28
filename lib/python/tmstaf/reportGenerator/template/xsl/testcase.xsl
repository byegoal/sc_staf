<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/testcase">
<html>
    <head>
        <title><xsl:value-of select="@name" /></title>
        <link href="../word.css" rel="stylesheet" type="text/css"/>
    </head>
    <body style="background-color:#ffffff">
			<A HREF="javascript:javascript:history.go(-1)">Back</A>
			<table border="1" cellpadding="0" cellspacing="0" width="100%">
			<tr>
			<td colspan="2" class="forFirstTitleTD"><span class="forFirstTitleFont">TestCase : <xsl:value-of select="@name"/></span></td>
			</tr>
			
			<xsl:for-each select="testcaseAttr">
			<tr>
			<td width="10%" class="forTitleTDWithoutHand"><xsl:value-of select="@name" /></td>
			<td class="forFieldTD">
			<span class="smallWord">
			<xsl:if test=".=''">&#160;</xsl:if>
			<xsl:if test=".">
				<xsl:if test="@link=1">
				<a>
				  <xsl:attribute name="href"><xsl:value-of select="." /></xsl:attribute>
				  <xsl:attribute name="target"><xsl:text>_blank</xsl:text></xsl:attribute>
				  <xsl:value-of select="."/>
				</a>			
				</xsl:if>
				<xsl:if test="not(@link)">
				<xsl:value-of select="."/>
				</xsl:if>
			</xsl:if>
			</span>
			</td>
			</tr>
			</xsl:for-each>
			<tr>
			<td width="10%" class="forTitleTDWithoutHand">OutputFile</td>
			<td class="forFieldTD">
			<span class="smallWord">
				<xsl:for-each select="fileList/file">
					<xsl:sort select="." data-type="text" order="ascending"/>
					<a>
					<xsl:attribute name="href"><xsl:value-of select="@url"/></xsl:attribute>
					<xsl:attribute name="target"><xsl:text>_blank</xsl:text></xsl:attribute>
					<xsl:value-of select="."/>
					</a><xsl:text>  </xsl:text>
				</xsl:for-each>
			</span>
			</td>
			</tr>
			</table>
        <xsl:for-each select="stepList ">
	        <br/>
	        <strong class="word"><xsl:value-of select="@type" /> Steps:&#160;&#160;&#160;&#160;&#160;&#160;</strong>
	        <xsl:if test="not(step)">
	        <br/><span class="mediumWord">&#160;N/A</span><br/>
	        </xsl:if>
	        <xsl:if test="step">
	        	<span class="mediumWord">
						Pass:&#160;<img height="16" width="16" src="../icon/pass.jpg" />&#160;&#160;&#160;
						Fail:&#160;<img height="16" width="16" src="../icon/fail.jpg" />&#160;&#160;&#160;
						Crash:&#160;<img height="16" width="16" src="../icon/crash.jpg" />
						</span>
						<br/>
		        <table border="1" cellpadding="0" cellspacing="0" width="100%">
			        <tr>
		            <td class="forTitleTDWithoutHand"><span class="forTitleFont">#</span></td>
		            <td class="forTitleTDWithoutHand"><span class="forTitleFont">Result</span></td>
		            <xsl:for-each select="step[1]/stepAttr">
		            	<td class="forTitleTDWithoutHand"><span class="forTitleFont"><xsl:value-of select="@name"/></span></td>
		            </xsl:for-each>
			        </tr>
							<xsl:for-each select="step">
								<tr style="background-color:#FFFFFF">
									<xsl:if test="@result='fail'">
											<xsl:attribute name="style">color:red</xsl:attribute>
									</xsl:if>
									<xsl:if test="@result='-'">
										<xsl:attribute name="style">color:#c8c8c8</xsl:attribute>
									</xsl:if>
							    <td width="2%" class="forFieldTD"><xsl:value-of select="position()"/></td>
	
									<td width="5%" align="center" valign="middle" class="forFieldTD">
										<xsl:if test="@result='pass'">
											<img alt="-" height="16" width="16" src="../icon/pass.jpg" />
										</xsl:if>
										<xsl:if test="@result='fail'">
												<img alt="-" height="16" width="16" src="../icon/fail.jpg" />
										</xsl:if>
										<xsl:if test="@result='crash'">
												<img alt="-" height="16" width="16" src="../icon/crash.jpg" />
										</xsl:if>
										<xsl:if test="@result='-'">
												<xsl:value-of select="@result"/>
										</xsl:if>
									</td>
	
							    <xsl:for-each select="stepAttr">
							       <td class="forFieldTD"><span class="smallWord"><xsl:value-of select="."/></span></td>
							    </xsl:for-each>
								</tr>
							</xsl:for-each>
				    </table>
					</xsl:if>
	</xsl:for-each>
	<br/>
	<A HREF="javascript:javascript:history.go(-1)">Back</A>
    </body>
</html>
</xsl:template>
</xsl:stylesheet>