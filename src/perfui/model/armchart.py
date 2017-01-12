# -*- coding: UTF-8 -*-
import json
import string

serial_chart_category_field_tag = 'ResponseTime'
serial_chart_graph_value_field_tag = 'Client'
serial_chart_graph_color_field_tag = 'color'

serial_chart_category_axis_title = 'Response Time Distribution'
serial_chart_value_axis_titile = 'Client Number'

class AmSerialChartColumn():
    def __init__(self, category_field_value, graph_value_field_vlaue, graph_color_field_value=''):
        self.chart_column_dict = {serial_chart_category_field_tag: category_field_value,
                                  serial_chart_graph_value_field_tag: graph_value_field_vlaue,
                                  serial_chart_graph_color_field_tag: graph_color_field_value,
                                  }
    
    def __repr__(self):
        return str(self.chart_column_dict)

class AmSerialchartModel(object):
    def __init__(self):
        self.amchart_column_list = []
    
    def add_armchart_column(self, amchart_column, index=None):
        if index is not None:
            self.amchart_column_list.insert(index, amchart_column.chart_column_dict)
        else:
            self.amchart_column_list.append(amchart_column.chart_column_dict)
    
    def generate_armchart_column_json(self):
        return json.dumps(self.amchart_column_list)
    
    def get_am_chart_defination(self, tag=None):
        am_chart_defination = {'serial_chart_category_field':serial_chart_category_field_tag,
                               'serial_chart_graph_value_field':serial_chart_graph_value_field_tag,
                               'serial_chart_graph_color_field': serial_chart_graph_color_field_tag,
                               'serial_chart_value_axis_titile':serial_chart_value_axis_titile,
                               }
        
        if tag is not None and tag != '':
            am_chart_defination[string.lower(tag) + '_serial_chart_category_axis_title'] = tag + ' ' + serial_chart_category_axis_title
        else:
            am_chart_defination['serial_chart_category_axis_title'] = serial_chart_category_axis_title
        
        return am_chart_defination

class VEXAmSerialchartModel(AmSerialchartModel):
    def __init__(self):
        super(VEXAmSerialchartModel, self).__init__()
        self.color_list = []
    
    def _sort(self):
        armchart_column_dict = {}
        armchart_column_keys = []
        #armchart_colors = ['#FF0F00', '#FF6600', '#FF9E01', '#FCD202', '#F8FF01', '#B0DE09', '#04D215', '#0D8ECF', '#0D52D1', '#2A0CD0', '#8A0CCF']
        armchart_colors = ['#04D215', '#B0DE09', '#F8FF01', '#FCD202', '#FF9E01', '#FF6600', '#FF0F00', '#FF6600', '#FCD202', '#0D8ECF', '#0D52D1', '#2A0CD0', '#8A0CCF']
        
        for amchart_column in self.amchart_column_list:
            vex_time_distribution = amchart_column.get(serial_chart_category_field_tag)
            time_distribute_key = int(vex_time_distribution.split('-')[0].strip())
            armchart_column_dict[time_distribute_key] = amchart_column
            armchart_column_keys.append(time_distribute_key)
        
        armchart_column_keys.sort()
        
        tmp_list = []
        for i, key in enumerate(armchart_column_keys):
            armchart_column = armchart_column_dict.get(key)
            if armchart_column is None:
                continue
            
            if armchart_column.get(serial_chart_graph_color_field_tag) =='':
                armchart_column[serial_chart_graph_color_field_tag] = armchart_colors[i%len(armchart_colors)]
            tmp_list.append(armchart_column)
        self.amchart_column_list = tmp_list
    
    def generate_armchart_column_json(self):
        self._sort()
        return json.dumps(self.amchart_column_list)

def generate_vex_am_serial_chart_info(time_distribution_list, tag=None):
    vex_chart = VEXAmSerialchartModel()
    for time_distribution in time_distribution_list:
        vex_chart.add_armchart_column(AmSerialChartColumn(time_distribution[0], time_distribution[1]))
    
    return vex_chart.generate_armchart_column_json(), vex_chart.get_am_chart_defination(tag)

    
        