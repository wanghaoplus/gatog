# coding:utf-8

class htmlTemplate(object):



    html_kpi_error = '''
        <div class="row">
            <div class="col-lg-12.0">
            <div class="box box_content">
                <div class="box-header box_borderbox">
                  <h3 class="box-title box_titlesmall" style="font-size:16px;position:relative; width:100%" ><a href="">{kpi_name}</a>
                  
                  </h3>

                  <div class="box-tools pull-right">
                    <button type="button" class="btn btn-box-tool" data-widget="collapse" callback="clickOpenEchart(option_{kpi_name},'{kpi_name}',this)"><i class="fa fa-minus"></i>
                    </button>
                  </div>
                </div>
                <div class="box-body no-padding">
                    <div id="main_{kpi_name}" style="height:288px;padding-top:15px;"></div>
                </div>
            </div>
            </div>
        </div>
    '''
    html_kpi_table = """
        <div class="row">
            <div class="col-lg-12.0">
            <div class="box box_content">
                <div class="box-header box_borderbox">
                  <h3 class="box-title box_titlesmall" style="font-size:16px" ><a href="">{kpi_name}_table</a></h3>

                  <div class="box-tools pull-right">
                    <button type="button" class="btn btn-box-tool" data-widget="collapse"><i class="fa fa-minus"></i>
                    </button>
                  </div>
                </div>
                <div class="box-body no-padding">
                <div id="{tab}_div" style="height:350px; padding-top:15px;width:100% ">
                   
<table id='{tab}'  style="width:100%;height:330px" data-options="fitColumns:true ,singleSelect:true,autoRowHeight:false,pagination:true,pageSize:10"></table>
 
                </div></div>
            </div>
        <script>
        if({tab_name}.total>10){{
			$("#{tab}").css("height","455px");
			$("#{tab}_div").css("height","465px");
		}}else{{
			let table_height=parseInt({tab_name}.total*35)+105;
			let div_height=table_height+20;
			$("#{tab}").css("height",table_height);
			$("#{tab}_div").css("height",div_height);
		}}

        $(function(){{
		    $('#{tab}').resizable({{
            }});
            function getData(){{
            var rows = [];
            return rows;
        }}
         function pagerFilter({tab_name}){{
            
            var dg = $(this);
            var opts = dg.datagrid('options');
            var pager = dg.datagrid('getPager');
            pager.pagination({{
                onSelectPage:function(pageNum, pageSize){{
                    opts.pageNumber = pageNum;
                    opts.pageSize = pageSize;
                    pager.pagination('refresh',{{
                        pageNumber:pageNum,
                        pageSize:pageSize
                    }});
                    dg.datagrid('loadData',{tab_name});
                }}
            }});
            
            return {tab_name};
        }}
        $('#{tab}').datagrid({{loadFilter:pagerFilter}}).datagrid('loadData', getData());
        $('#{tab}').datagrid({{

                iconCls:'icon-ok',
                //fitColumns:true,
                //width:520,
                //height:250,
                //fit:ture,
                singleSelect:true,
                remoteSort:false,
                columns:[[
                   
       
        

        {tab_col}


                ]]
            }}).datagrid('loadData', {tab_name});
        
            $('#{tab}').datagrid('enableFilter', [

            ]);
        }});
    </script>

          </div>
        </div>
    """
    html_kpi_col ="""
        {{
        
         width: 100,

        field:'{tab_filed}',
        sortable:true,
        title:'{tab_filed}',
         
        align:'center',
        
        formatter: function(value, row, index){{
			if (value instanceof Array) {{
				var result="";
				if(value[2]==undefined){{
				    value[2]=""
				}}
				if(value[1]!=undefined && value[1]!=null && value[1]!=""){{
					result+='<a class="easyui-tooltip" href="'+value[1]+'" target="_blank" title="'+value[2]+'">'+value[0]+'</a>';
				}}else{{
					result='<span class="easyui-tooltip" title="'+value[2]+'">'+value[0]+'</span>';
				}}
				return result;
			}}
			else {{
				return value;
			}}
		}}
        }},"""
    html_single_js_template = '''{{
    backgroundColor: '#323a5e',
     tooltip: {{
         trigger: 'axis',
         axisPointer: {{ 
             type: 'shadow' 
         }}
     }},
     grid: {{
         left: '2%',
         right: '4%',
         bottom: '14%',
         top: '16%',
         containLabel: true
     }},
     legend: {{
         data: {data_name},
         right: 10,
         top: 12,
         textStyle: {{
             color: "#fff"
         }},
         itemWidth: 12,
         itemHeight: 10,
         // itemGap: 35
     }},
     color:{color},
     xAxis: {{
         type: 'category',
         data: {data},
         axisLine: {{
             lineStyle: {{
                 color: 'white'

             }}
         }},
         axisLabel: {{
             // interval: 0,
             // rotate: 40,
             textStyle: {{
                 fontFamily: 'Microsoft YaHei'
             }}
         }},
     }},

     yAxis: {{
         type: 'value',
         //max: '1200',
         axisLine: {{
             show: false,
             lineStyle: {{
                 color: 'white'
             }}
         }},
         splitLine: {{
             show: true,
             lineStyle: {{
                 color: 'rgba(255,255,255,0.3)'
            }}
         }},
         axisLabel: {{}}
     }},
     "dataZoom": [{{
         "show": true,
         "height": 12,
         "xAxisIndex": [
             0
         ],
         bottom: '8%',
         "start": 0,
         "end": 50,
         handleIcon: 'path://M306.1,413c0,2.2-1.8,4-4,4h-59.8c-2.2,0-4-1.8-4-4V200.8c0-2.2,1.8-4,4-4h59.8c2.2,0,4,1.8,4,4V413z',
         handleSize: '110%',
         handleStyle: {{
             color: "#d3dee5",

         }},
         textStyle: {{
             color: "#fff"
         }},
         borderColor: "#90979c"
     }}, {{
         "type": "inside",
         "show": true,
         "height": 15,
         "start": 1,
         "end": 35
     }}],
     series: [
     {series}
     ]
 }};

 var app = {{
     currentIndex: -1,
 }};
 setInterval(function() {{
     var dataLen = option_{kpi_name}.series[0].data.length;
     myChart.dispatchAction({{
         type: 'downplay',
         seriesIndex: 0,
         dataIndex: app.currentIndex
     }});
     app.currentIndex = (app.currentIndex + 1) % dataLen;
     
     myChart.dispatchAction({{
         type: 'highlight',
         seriesIndex: 0,
         dataIndex: app.currentIndex,
     }});
     
     myChart.dispatchAction({{
         type: 'showTip',
         seriesIndex: 0,
         dataIndex: app.currentIndex
     }});


 }}, 1000);
 
 myChart_{kpi_name} = echarts.init(document.getElementById('main_{kpi_name}'));
          myChart_{kpi_name}.setOption(option_{kpi_name});
          myChart_{kpi_name}.on('click', function (params){{
             if(params.data.url)
              window.open('../detail/'+params.data.url);
            }});'''

    html_js_template = '''{{
          legend : {{
                data : {data_name},
                icon: 'circle',
                tooltip:{{
                    show: true,
                    formatter: function (params)
                    {{
                        console.log(params.name);
                        if ([][params.name] != undefined){{
                           items =  [][params.name]
                            return "IEName："+items[0] +"<br>IESource："+items[1]+"<br>IESpan："+items[2]+"<br>IEDescriptor："+items[3];
                        }}
                    }},
                }},
        }},
        color:{color},
        grid:{{
            x: 130,
            y: 40,
            x2: 70,
            y2: 80,
            borderWidth:1
            }},
        
        tooltip: {{
                    trigger: 'axis',
                    show:true,
                    
         formatter: function (params) {{
            var result = "";
            for(i=0;i<params.length;i++){{
                var dataName ;
                var data ;
                if(typeof params[i].data=="undefined"){{
                    dataName = params[i].seriesName;
                    data = "";
                }}else{{
                    dataName = params[i].seriesName;
                    data = params[i].data[0] +' - '+ params[i].data[1];
                }}
                result +=  dataName + ' : ' + data + '<br>';
            }}
            return result;
         }},
        axisPointer: {{
            animation: false
        }}
        

                }},
        
        dataZoom : [{{
            show : true,
            //realtime: true,
            start : 0,
            end : 20
        }},
        {{
            type: 'inside',
            xAxisIndex: 0,
            filterMode: 'empty'
        }},
        {{
            fillerColor: 'rgba(31,159,255,0.2)',
            backgroundColor:'#fff',
            dataBackground:{{

                lineStyle:{{
                    //opacity:0.4,

                }},
                areaStyle:{{
                    //opacity:0.4,
                    //color: '#000',

                }},
            }},
        handleStyle: {{
        color: '#fff',
        borderColor:'#1F9FFF',
         //opacity:0.4
        }}
    }}],
        xAxis: [{{
                
         type: 'time',

                min : starttime,
                max : endtime,
                splitNumber:10,
                axisLine: {{
                          show: true,
                          lineStyle: {{
                          color: '#666'
                           }}
                }},
                splitLine: {{
                          show: true,
                          lineStyle: {{
                          color: '#eee'
                           }}
                }},
                axisLabel: {{
			    formatter: function (value, index) {{
						var date = new Date(value);
						var texts = [date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds() + '.' + date.getMilliseconds()];
						return texts;
                }}}}
            }}],
        yAxis: [{{
                type : 'value',
                axisLine: {{
                      show: true,
                      lineStyle: {{
                      color: '#666'
                       }}
            }},
            splitLine: {{
                      show: true,
                      lineStyle: {{
                      type: 'dashed'
                       }}
            }},
            
        }}],
      series: [
             {series}
        
       ]
    }};

          myChart_{kpi_name} = echarts.init(document.getElementById('main_{kpi_name}'));
          myChart_{kpi_name}.setOption(option_{kpi_name});
          myChart_{kpi_name}.on('click', function (params){{
             if(params.data.url)
              window.open('../detail/'+params.data.url);
            }});'''

    html_js_series = r'''
            {{
                type: '{type}',
                data: {js_data},
                
                name:"{js_name}",
                
            }}'''

    html_js_start_line = '''var hideEchartList=[]
                      $(function(){{

                    var starttime = new Date("{starttime}")
                    var endtime = new Date("{endtime}")
                    '''
    html_js_single_start_line = '''var hideEchartList=[]
                      $(function(){
                    '''
                    
    html_js_end_line = '''
        window.addEventListener("resize", function () {{

    {mychart}
        }});

    }})'''

    html_cdf_img = """<div class="row">
            <div class="col-lg-12.0">
            <div class="box box_content">
                <div class="box-header box_borderbox">
                  <h3 class="box-title box_titlesmall" style="font-size:16px;position:relative; width:100%" ><a href="">{kpi_name}_CDF</a>
                  </h3>
                  <div class="box-tools pull-right";>
                  </div>
                </div>
                <div class="box-body no-padding">
                    <div id="main_{kpi_name}" style="height:500px;">
                    	<img src="../dist/img/{CDF_PNG}" />
                    </div>
                </div>
            </div>
            </div>
        </div>
        """


if __name__ == '__main__':
    hT = htmlTemplate()
    print(hT.html_js_series.format(js_data='sss', js_name='sssdata'))
