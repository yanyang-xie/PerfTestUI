function getStatus(url) {
    $.ajax({  
        url: url,  
        type: 'Get',            
        success: function (data) {  
        	for(var o in data){
        		//alert("id:"+data[o].id+" status:"+data[o].status );  
        		if (data[o].status == 0){
        			$("#op_status_" + data[o].id).html("Running");
        			$("#btn_start_" + data[o].id).hide();
        			$("#btn_stop_" + data[o].id).show();
        		}else if (data[o].status == 1){
        			$("#btn_stop_" + data[o].id).hide();
        			$("#btn_start_" + data[o].id).show();
        			$("#op_status_" + data[o].id).html("Stopped");
        		}else{
        		}
            } 
        }  
    });  
}  

function ucfirst(str) {
	var str = str.toLowerCase();
	str = str.replace(/\b\w+\b/g, function(word){
	  return word.substring(0,1).toUpperCase()+word.substring(1);
	});
	return str;
}

function operation(op_tag, op_id, btn_id, is_vex_operation, test_type, update_status_message){
	var timeout = 300000;
	var btn = $("#" + btn_id);
	btn.button('loading');
	
	$.ajax({ 
           type: "get", 
           url: "/op/execute?op_tag=" + op_tag + "&op_id=" + op_id + "&vex_op=" + is_vex_operation,
           dataType: "json",
           timeout:timeout,
           success: function (data) { 
        	   if(data["status_code"] == 200){
        		   if (op_tag == "result"){
        			    window.location = "/result/" + test_type;
        		   }else{
	   					bootbox.alert({
	   						title: "<p><strong class='text-info'>" + ucfirst(op_tag) + " Succeed</p>",
	   						message: "<p><strong class='text-success'>" + data["message"] + "</p>",
	   					    size: 'large'
	   					});
	   					btn.button('reset');
	   					
	   					if(op_tag=="start" && update_status_message=="true"){
	   						$("#op_status_" + op_id).html("Running");
	   						$("#btn_start_" + op_id).hide();
	   						$("#btn_stop_" + op_id).show();
	   						
	   						try{ 
	   							$('#warm_up_minute').editable('toggleDisabled');
	   						}catch (e) { 
	   						}
	   					}
	   					
	   					if(op_tag=="stop" && update_status_message=="true"){
	   						$("#op_status_" + op_id).html("Stopped");
	   						$("#btn_start_" + op_id).show();
	   						$("#btn_stop_" + op_id).hide();
	   						
	   						try{ 
	   							$('#warm_up_minute').editable('toggleDisabled');
	   						}catch (e) { 
	   						}
	   					}
	   					
	   					getBasicCompontentStatus();
        	        }
   				}else{
   					bootbox.alert({
   						title: "<p><strong class='text-info'>" + ucfirst(op_tag) + " Failure</p>",
   						message: "<p><strong class='text-danger'>" + data["message"] + "</p>",
   					    size: 'large'
   					});
   					btn.button('reset');
   				}
           },
           error: function(){
        	   bootbox.alert({
   					title: "<p><strong class='text-info'>" + ucfirst(op_tag) + " Failure</p>",
   					message: "<p><strong class='text-danger'>Operation timeout. Please check status manually.</p>",
   				    size: 'large'
   				});
   				btn.button('reset');
           }
   });
}

function drawAmCharts(chartID, columDatas, category_field, category_axis_title, value_axis_titile, graph_color_field, graph_value_field) {
    var chart;
    
    // SERIAL CHART
    chart = new AmCharts.AmSerialChart();
    chart.dataProvider = columDatas;
    chart.categoryField = category_field;
    chart.startDuration = 1;

    // AXES
    // category
    var categoryAxis = chart.categoryAxis;
    categoryAxis.labelRotation = 60; // this line makes category values to be rotated
    categoryAxis.gridAlpha = 0;
    categoryAxis.fillAlpha = 1;
    categoryAxis.fillColor = "#FAFAFA";
    categoryAxis.gridPosition = "start";
    categoryAxis.title = category_axis_title;

    // value
    var valueAxis = new AmCharts.ValueAxis();
    valueAxis.dashLength = 5;
    valueAxis.title = value_axis_titile;
    valueAxis.axisAlpha = 0;
    chart.addValueAxis(valueAxis);

    // GRAPH
    var graph = new AmCharts.AmGraph();
    graph.valueField = graph_value_field;
    graph.colorField = graph_color_field;
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