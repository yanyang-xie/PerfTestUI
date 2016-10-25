
function drawAmCharts(columDatas, chartID) {
    var chart;
    
    // SERIAL CHART
    chart = new AmCharts.AmSerialChart();
    chart.dataProvider = columDatas;
    chart.categoryField = "ResponseTime";
    chart.startDuration = 1;

    // AXES
    // category
    var categoryAxis = chart.categoryAxis;
    categoryAxis.labelRotation = 60; // this line makes category values to be rotated
    categoryAxis.gridAlpha = 0;
    categoryAxis.fillAlpha = 1;
    categoryAxis.fillColor = "#FAFAFA";
    categoryAxis.gridPosition = "start";
    categoryAxis.title = "client response time distribution"

    // value
    var valueAxis = new AmCharts.ValueAxis();
    valueAxis.dashLength = 5;
    valueAxis.title = "client number of response time";
    valueAxis.axisAlpha = 0;
    chart.addValueAxis(valueAxis);

    // GRAPH
    var graph = new AmCharts.AmGraph();
    graph.valueField = "Client";
    graph.colorField = "color";
    graph.balloonText = "<b>[[category]]: [[value]]</b>";
    graph.type = "column";
    graph.lineAlpha = 0;
    graph.fillAlphas = 1;
    chart.addGraph(graph);

    // CURSOR
    var chartCursor = new AmCharts.ChartCursor();
    chartCursor.cursorAlpha = 0;
    chartCursor.zoomable = false;
    chartCursor.categoryBalloonEnabled = false;
    chart.addChartCursor(chartCursor);

    chart.creditsPosition = "top-right";

    // WRITE
    chart.write(chartID);
}