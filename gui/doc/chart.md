Displays data sets in a chart or a group of charts.

The chart control is based on the [plotly.js](https://plotly.com/javascript/)
graphs library.

Plotly is a graphing library that provides a vast number of visual
representations of datasets with all sorts of customization capabilities. Taipy
exposes the Plotly components through the `chart` control and heavily depends on
the underlying implementation.

The core principles of how to create charts in Taipy are explained in the
[Basic concepts](charts/basics.md) section.

# Chart types catalog

Because there are so many different ways of representing data, we have sorted
the chart types supported by Taipy by application category:

<style>
.h3 {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.h3 a {
  font-weight: 400;
  font-size: 16px;
  line-height: 24px;
  display: flex;
  align-items: center;
}
.h3 a svg {
    fill: #FE462B;
    max-height: 100%;
    width: 1.125em;
    margin-right: 10px;
}
.md-typeset .list {
    margin-left: 0;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: flex-start;
    list-style: none;
    gap: 16px;
    padding: 0;
}
.list li {
    margin: 0 !important;
    padding: 0;
    width: 171px;
}
.list a {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px;
    gap: 16px;
    border-radius: 4px;
    color: var(--md-default-fg-color);
    background: var(--md-paper-bg-color);
}
.list a>img {
    border: 2px solid currentColor;
    border-radius: 4px;
}
.list span {
    line-height: 17px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    font-size: 16px;
}
.list a svg {
    fill: var(--md-typeset-a-color);
    max-height: 100%;
    width: 1.125em;
    margin-left: 10px;
}
</style>
<svg xmlns="http://www.w3.org/2000/svg" display="none">
    <symbol id="rarrow" viewBox="0 0 24 24">
        <path d="M4 11v2h12l-5.5 5.5 1.42 1.42L19.84 12l-7.92-7.92L10.5 5.5 16 11H4z"></path>
    </symbol>
</svg>

<h3 class="h3">Basic charts</h3>
<ul class="list">
    <li><a href="../charts/line">
        <span>Line charts<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-line-d.png"  class="visible-dark" />
        <img src="../charts/home-line-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/scatter">
        <span>Scatter plots<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-scatter-d.png"  class="visible-dark" />
        <img src="../charts/home-scatter-l.png"  class="visible-light" />
        </a></li>
    <li><a href="../charts/bar">
        <span>Bar charts<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-bar-d.png"  class="visible-dark" />
        <img src="../charts/home-bar-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/bubble">
        <span>Bubble charts<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-bubble-d.png"  class="visible-dark" />
        <img src="../charts/home-bubble-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/filled-area">
        <span>Filled areas<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-filled-area-d.png"  class="visible-dark" />
        <img src="../charts/home-filled-area-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/pie">
        <span>Pie charts<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-pie-d.png"  class="visible-dark" />
        <img src="../charts/home-pie-l.png"  class="visible-light" />
      </a></li>
    <!-- Sunburst charts - sunburst -->
    <!-- Sankey diagram  - sankey   -->
</ul>

<h3 class="h3">Statistical charts</h3>
<ul class="list">
    <li><a href="../charts/histogram">
        <span>Histograms<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-histogram-d.png"  class="visible-dark" />
        <img src="../charts/home-histogram-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/heatmap">
        <span>Heatmaps<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-heatmap-d.png"  class="visible-dark" />
        <img src="../charts/home-heatmap-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/error-bar">
        <span>Error bars<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-error-bar-d.png"  class="visible-dark" />
        <img src="../charts/home-error-bar-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/continuous-error">
        <span>Continuous error<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-continuous-error-d.png"  class="visible-dark" />
        <img src="../charts/home-continuous-error-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/box-plot">
        <span>Box plots<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-box-plot-d.png"  class="visible-dark" />
        <img src="../charts/home-box-plot-l.png"  class="visible-light" />
      </a></li>
    <!-- Violin plots - violin -->
    <!-- 2D histograms - 2d-histogram -->
    <!-- 2d density plot - 2d-density-->
    <!-- Contour plots - contour -->
</ul>

<h3 class="h3">Scientific charts</h3>
<ul class="list">
    <li><a href="../charts/polar">
        <span>Polar charts<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-polar-d.png"  class="visible-dark" />
        <img src="../charts/home-polar-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/radar">
        <span>Radar charts<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-radar-d.png"  class="visible-dark" />
        <img src="../charts/home-radar-l.png"  class="visible-light" />
      </a></li>
</ul>

<h3 class="h3">Financial charts</h3>
<ul class="list">
    <li><a href="../charts/candlestick">
        <span>Candlestick charts<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-candlestick-d.png"  class="visible-dark" />
        <img src="../charts/home-candlestick-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/funnel">
        <span>Funnel charts<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-funnel-d.png"  class="visible-dark" />
        <img src="../charts/home-funnel-l.png"  class="visible-light" />
      </a></li>
</ul>

<h3 class="h3">Maps</h3>
<ul class="list">
    <li><a href="../charts/chart-map">
        <span>Charts on maps<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-chart-map-d.png"  class="visible-dark" />
        <img src="../charts/home-chart-map-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/area-map">
        <span>Areas on maps<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-area-map-d.png"  class="visible-dark" />
        <img src="../charts/home-area-map-l.png"  class="visible-light" />
      </a></li>
    <li><a href="../charts/density-map">
        <span>Density maps<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><use xlink:href="#rarrow"/></svg></span>
        <img src="../charts/home-density-map-d.png"  class="visible-dark" />
        <img src="../charts/home-density-map-l.png"  class="visible-light" />
      </a></li>
    <!-- Choropleth maps - choropleth-map -->
</ul>

# Description

A chart control can hold several traces, that can display individual data sets.<br/>
To indicate properties for a given trace, you will use the indexed properties
(using the *property_name[index]* syntax, with the indices starting at index 1) to
specify which trace you target.

Indexed properties can have a default value (using the *property_name* syntax with
no index) which is overridden by any specified indexed property:<br/>
if `indexed_property` is an indexed property, you can set it to a value, that is
then applied to all the traces. If you later reference that property with an index, the
value will apply only for the indicated trace.
```
general_value = <some_value>
specific_value = <some_other_value>

page = "<|...|chart|...|index_property={general_value}|index_property[2]={specific_value}|...|>"
```
creates a chart where *general_value* is used for all the traces, except for the one with index 2.

An indexed property can also be assigned an array. Then each array value is set to the appropriate
index, in sequence:
```
values = [
    value1,
    value2,
    value3
]
    
page = "<|...|chart|...|index_property={values}|...|>"
```
is equivalent to
```
page = "<|...|chart|...|index_property[1]={value1}|index_property[2]={value2}|index_property[3]={value3}|...|>"
```

or even shorter:
```
page = "<|...|chart|...|index_property={value1}|index_property[2]={value2}|index_property[3]={value3}|...|>"
```

Supported types for the *data* property types are:

- A Pandas DataFrame;
- A Dictionary: converted into a Pandas DataFrame where each key/value pair is converted
  to a column named *key* and the associated value;
- A list of lists;
- A Numpy series;
- A list of Pandas DataFrames;
- A list of dictionaries, which is converted to a list of Pandas DataFrames.


## Usage

Here is a list of several sub-sections that you can check to get more details on a specific
areas covered by the chart control:

- [Basic concepts](charts/basics.md)
- [Line charts](charts/line.md)
- [Scatter charts](charts/scatter.md)
- [Bar charts](charts/bar.md)
- [Bubble charts](charts/bubble.md)
- [Filled areas](charts/filled-area.md)
- [Pie charts](charts/pie.md)
- [Histograms](charts/histogram.md)
- [Heatmaps](charts/heatmap.md)
- [Error bars](charts/error-bar.md)
- [Continuous error](charts/continuous-error.md)
- [Box plots](charts/box-plot.md)
- [Polar charts](charts/polar.md)
- [Radar charts](charts/radar.md)
- [Candlestick charts](charts/candlestick.md)
- [Funnel charts](charts/funnel.md)
- [Charts on maps](charts/map.md)
- [Areas on maps](charts/map.md)
- [Density maps](charts/map.md)
- [Gantt charts](charts/gantt.md)
- [Other chart types](charts/others.md)
