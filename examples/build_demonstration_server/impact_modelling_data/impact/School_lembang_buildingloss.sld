<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0" 
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
    xmlns="http://www.opengis.net/sld" 
    xmlns:ogc="http://www.opengis.net/ogc" 
    xmlns:xlink="http://www.w3.org/1999/xlink" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>Attribute-based point</Name>
    <UserStyle>
      <Title>Lembang building loss: Attribute-based point</Title>
      <FeatureTypeStyle>
        <Rule>
          <Name>2%</Name>
          <Title>0 to 2.0</Title>
          <ogc:Filter>
            <ogc:PropertyIsLessThan>
              <ogc:PropertyName>PERCENTAGE</ogc:PropertyName>
              <ogc:Literal>2.0</ogc:Literal>
            </ogc:PropertyIsLessThan>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>square</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#FFFFBE</CssParameter>
                </Fill>
                <Stroke>
               		<CssParameter name="stroke">#000000</CssParameter>
               		<CssParameter name="stroke-width">2</CssParameter>
             	  </Stroke>
              </Mark>
              <Size>10</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        <Rule>
          <Name>10%</Name>
          <Title>2.1 to 10</Title>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThanOrEqualTo>
                <ogc:PropertyName>PERCENTAGE</ogc:PropertyName>
                <ogc:Literal>2.0</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>PERCENTAGE</ogc:PropertyName>
                <ogc:Literal>10</ogc:Literal>
              </ogc:PropertyIsLessThan>
            </ogc:And>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>SQUARE</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#F5B800</CssParameter>
                </Fill>
                <Stroke>
               		<CssParameter name="stroke">#000000</CssParameter>
               		<CssParameter name="stroke-width">2</CssParameter>
             	  </Stroke>
              </Mark>
              <Size>10</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        <Rule>
          <Name>25%</Name>
          <Title>10.1 to 25</Title>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThanOrEqualTo>
                <ogc:PropertyName>PERCENTAGE</ogc:PropertyName>
                <ogc:Literal>10.0</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>PERCENTAGE</ogc:PropertyName>
                <ogc:Literal>25</ogc:Literal>
              </ogc:PropertyIsLessThan>
            </ogc:And>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>SQUARE</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#F57A00</CssParameter>
                </Fill>
                <Stroke>
               		<CssParameter name="stroke">#000000</CssParameter>
               		<CssParameter name="stroke-width">2</CssParameter>
             	  </Stroke>
              </Mark>
              <Size>10</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        <Rule>
          <Name>50%</Name>
          <Title>25.1 to 50</Title>
          <ogc:Filter>
            <ogc:And>
              <ogc:PropertyIsGreaterThanOrEqualTo>
                <ogc:PropertyName>PERCENTAGE</ogc:PropertyName>
                <ogc:Literal>25.0</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>PERCENTAGE</ogc:PropertyName>
                <ogc:Literal>50</ogc:Literal>
              </ogc:PropertyIsLessThan>
            </ogc:And>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>SQUARE</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#F53D00</CssParameter>
                </Fill>
                <Stroke>
               		<CssParameter name="stroke">#000000</CssParameter>
               		<CssParameter name="stroke-width">2</CssParameter>
             	  </Stroke>
              </Mark>
              <Size>10</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        <Rule>
          <Name>ABOVE50%</Name>
          <Title>Greater than 50</Title>
          <ogc:Filter>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>PERCENTAGE</ogc:PropertyName>
              <ogc:Literal>50</ogc:Literal>
            </ogc:PropertyIsGreaterThanOrEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>SQUARE</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#A80000</CssParameter>
                </Fill>
                <Stroke>
               		<CssParameter name="stroke">#000000</CssParameter>
               		<CssParameter name="stroke-width">2</CssParameter>
             	  </Stroke>
              </Mark>
              <Size>10</Size>
            </Graphic>
          </PointSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>