# coding:utf-8
import shutil
import zipfile
import random
import os
from aw.utils.nmeanalysis.LbsLogPrint import DT_FAIL, DT_SUC
from aw.utils.nmeanalysis.html_report.htmlTemplate import htmlTemplate
from aw.utils.nmeanalysis.AresInput import LBSDector
# from aw.utils.nmeanalysis.AnalyzeModule import color_list


class HtmlManager(object):
#     color_list = ['#5cb9ff','#12e78c', '#9aa1f9','#fe8104', '#F4CB29', '#9ad65d', '#5ad4df', '#4B7CF3', 'dd3ee5']
    data_js_name_list = []
    data_js_name_dict = {}

    option_error_all = ''
    mychart_list = ''
    error_static_report_html = []

    def __init__(self, reportpath, config, color_list):
        
        self.config = config
        self.report_path = reportpath
        report_zip_path = os.path.join((os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + ".")), 'html_report.zip')
        res = self.unzip_file(report_zip_path, self.report_path)
        self.color_list = color_list


    def unzip_file(self, zipName, dstPath):

        if not os.path.isfile(zipName) or os.path.splitext(zipName)[1] != '.zip':
            return DT_FAIL, 'Parameter wrong'
        try:
            import zipfile
            file_zip = zipfile.ZipFile(zipName, 'r')
            for file in file_zip.namelist():
                file_zip.extract(file, dstPath)
        except:
            return DT_FAIL, 'ZIP fail'
        finally:
            if None != file_zip:
                file_zip.close()
        return DT_SUC, ''

    def random_str_num(self):
        items = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
                 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        random.shuffle(items)
        return items[0] + items[1] + items[2] + items[3]
    
    @LBSDector(True)
    def write_kpi_error_curve_js(self, curve_name_list, error_data_tuples, kpi_error, start_time, end_time, error_kpi_list, js_file_name):
        """写曲线js数据"""
        kpi_data_name_list = []
        for index in range(len(curve_name_list)):
            ll = self.write_device_curve_data(curve_name_list[index], error_data_tuples[0][index], kpi_error)
            kpi_data_name_list.append(ll)

        self.mychart_list += '              myChart_%s.resize();' % kpi_error
        self.mychart_list += '\n'
        self.data_js_name_dict[kpi_error] = kpi_data_name_list
        self.option_error_all += self.write_kpi_error_zoom(curve_name_list, kpi_error, js_file_name) + '\n' + '\n'
        try:
            if kpi_error == error_kpi_list[len(error_kpi_list)-1]:

                line = htmlTemplate.html_js_start_line.format(starttime=start_time, endtime=end_time)
                end = htmlTemplate.html_js_end_line.format(mychart=self.mychart_list)

                path = os.path.join(self.report_path, 'dist', 'page',js_file_name)
                if not os.path.exists(path):
                    f = open(path, 'w', encoding='utf8')
                    f.write(line + "\n"+ self.option_error_all + end)
                    f.close()
                else:
                    lines = ''
                    f = open(path, 'r', encoding='utf8')
                    for line in f:
                        if 'window.addEventListener("resize", function ()' in line:
                            lines += self.option_error_all
                            lines += end
                            break
                        lines += line
                    f.close()
                    data_file = open(path, 'w', encoding='utf8')
                    data_file.write(lines)
                    data_file.close()
        except Exception as e:
            print('8888',lines, e)


        self.error_static_report_html.append(htmlTemplate.html_kpi_error.format(kpi_name=kpi_error))  # 写html
        if kpi_error in ['position_error', 'heading_error', 'speed_error', 'alt_error', 'overshoot_error', 'undershoot_error', "along_error", "across_error"]:
            self.error_static_report_html.append(htmlTemplate.html_cdf_img.format(kpi_name=kpi_error, CDF_PNG=kpi_error + '_CDF.png'))
    
    @LBSDector(True)
    def write_single_kpi_error_curve_js(self, curve_name_list, error_data_tuples, kpi_error, total_num_list, single_error_list, js_file_name):
        """写曲线js数据"""
        kpi_data_name_list = []
        for index in range(len(curve_name_list)):
            ll = self.write_device_curve_data(curve_name_list[index], error_data_tuples[0][index][0], kpi_error)
            kpi_data_name_list.append(ll)

        self.mychart_list += '              myChart_%s.resize();' % kpi_error
        self.mychart_list += '\n'
        self.data_js_name_dict[kpi_error] = kpi_data_name_list
        self.option_error_all += self.write_kpi_error_zoom(curve_name_list, kpi_error, js_file_name, type='bar', total_num_list=total_num_list) + '\n' + '\n'
        try:
            if kpi_error == single_error_list[len(single_error_list)-1]:

                line = htmlTemplate.html_js_single_start_line
                end = htmlTemplate.html_js_end_line.format(mychart=self.mychart_list)

                path = os.path.join(self.report_path, 'dist', 'page',js_file_name)
                if not os.path.exists(path):
                    f = open(path, 'w', encoding='utf8')
                    f.write(line + "\n"+ self.option_error_all + end)
                    f.close()
                else:
                    lines = ''
                    f = open(path, 'r', encoding='utf8')
                    for line in f:
                        if 'window.addEventListener("resize", function ()' in line:
                            lines += self.option_error_all
                            lines += end
                            break
                        lines += line
                    f.close()
                    data_file = open(path, 'w', encoding='utf8')
                    data_file.write(lines)
                    data_file.close()
        except Exception as e:
            print('8888',lines, e)


        self.error_static_report_html.append(htmlTemplate.html_kpi_error.format(kpi_name=kpi_error))  
#         self.error_static_report_html.append(htmlTemplate.html_cdf_img.format(kpi_name=kpi_error, CDF_PNG=kpi_error + '_CDF.png'))

    def write_kpi_error_zoom(self, name_list, kpi_error, js_file_name, type='line', total_num_list=None):
        error_option = 'option_' + kpi_error + '='
        series = ''
        for index in range(len(name_list)):
            series += htmlTemplate.html_js_series.format(js_data=self.data_js_name_dict[kpi_error][index][1], js_name=name_list[index], type=type)
            if index < len(name_list)-1:
                series += ','
        if type == 'bar' and total_num_list:
            error_option += htmlTemplate.html_single_js_template.format(data_name=name_list, color=self.color_list[0:len(name_list)], series=series, kpi_name=kpi_error, data=total_num_list)
        else:
            error_option += htmlTemplate.html_js_template.format(data_name=name_list, color=self.color_list[0:len(name_list)], series=series, kpi_name=kpi_error)
        return error_option


    def export_kpi_error_js(self, col_datas, devices_list,  kpi_name_data, error_name, device_name='table'):
        '''写统计表格数据'''

        data_dict = {}
        data_dict["total"] = len(col_datas)
        kpi_name_data.insert(0, "LBS_KPI_Final_HE")
        if self.config['satelliteInfo']:
            kpi_name_data.insert(0, 'serialInfo')
        rows_list = []
        for index, temp in enumerate(devices_list):
            rows_list.append(dict(zip(kpi_name_data, col_datas[index])))
        data_dict["rows"] = rows_list
        random_str = self.random_str_num()
        file_path = os.path.join(self.report_path, 'data', device_name + '_' + random_str + ".js")
        self.data_js_name_list.append(file_path)
        data_js_name = device_name + '_' + random_str
        line = 'var' + ' ' + data_js_name + 'data' + '=' + ' ' + str(data_dict).replace("'", '"') + ';'
        data_file = open(file_path, 'w')
        data_file.write(line)
        data_file.close()
        tab_col = ''

        for num in range(len(kpi_name_data)):
            tab_col += htmlTemplate.html_kpi_col.format(kpi_name=error_name, tab_filed=kpi_name_data[num]) + '\n'
        self.error_static_report_html.append(htmlTemplate.html_kpi_table.format(kpi_name=error_name,
                                                                                tab_name= data_js_name + 'data',
                                                                                tab='tab'+error_name, tab_col=tab_col))   # 添加数据到html


    def write_html_report(self, html_file_name='ErrorStatisticsRelatedReports.html'):
        file_path = os.path.join(self.report_path, 'html', html_file_name)
        lines = ''
        rd = open(file_path, "r")
        a = 0
        for line in rd:
            if 'ErrorStatisticsRelatedReports.js' in line or "ErrorSingleRelatedReports.js" in line:
                if a < 10:
                    print('***', line)
                    a += 1
                file_list = os.listdir(os.path.join(self.report_path, 'data'))
                lines += line
                for temp in file_list:
                    temp = '    <script src = "..\data\%s"></script>' % temp
                    lines += temp + '\n'
                continue

            if 'SatelliteStatisticsRelatedReports.js' in line:
                if a < 10:
                    print('***', line)
                    a += 1
                file_list = os.listdir(os.path.join(self.report_path, 'data'))
                lines += line
                for temp in file_list:
                    temp = '    <script src = "..\data\%s"></script>' % temp
                    lines += temp + '\n'
                continue

            if '<section class="content">' in line:
                lines += line
                for temp in self.error_static_report_html:
                    lines += temp
                continue
            lines += line
        rd.close()

        f = open(file_path, "w")
        f.write(lines)
        f.close()
        self.error_static_report_html = []
        self.data_js_name_dict = {}
        self.data_js_name_list = []
        self.option_error_all = ''
        self.data_js_name_dict ={}
        self.mychart_list = ''

    def write_device_curve_data(self, device_name, data, kpi_error):

        random_str = self.random_str_num()
        file_path = os.path.join(self.report_path, 'data', device_name + '_' + random_str + ".js")
        self.data_js_name_list.append(file_path)
        data_js_name = device_name + '_' + random_str
        line ='var' + ' ' + data_js_name + 'data' + '=' + ' ' + str(data)
        data_file = open(file_path, 'w')
        data_file.write(line)
        data_file.close()
        return [data_js_name, data_js_name + 'data']
    
   


if __name__ == '__main__':

    # HT = HtmlManager(r'D:\report31')
    #
    # data = [['68% CEP', '1.75', '1.84'], ['95% CEP', '13.84', '14.15'], ['MAX', '179.56', '115.04'], ['MEAN', '4.91', '3.30'], ['Position Yield', '30.57', '33.65']]
    # HT.write_device_curve_data('Broadcom',data)
    # print(str(data))
    bb  = [1,2,3,4]
    c = bb[0:2]

    print(c)




