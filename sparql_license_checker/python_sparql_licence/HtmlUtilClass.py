#  SPARQL License Checker
#  Copyright (C) 2017 DISIT Lab http://www.disit.org - University of Florence
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re


class HtmlUtilClass:

    def __init__(self):
        pass

    @staticmethod
    def get_div_header(div_class, div_id=None):
        return '<div ' + ('id="'+div_id+'"' if div_id is not None else ' ') +' class="'+div_class+'" >'

    @staticmethod
    def get_div(div_class, div_content, div_id=''):
        return HtmlUtilClass.get_div_header(div_class, div_id) + div_content + '</div>'

    @staticmethod
    def get_titled_div(title, div_content, div_class):
        return HtmlUtilClass.get_div_header(div_class)+\
               HtmlUtilClass.print_title(title,3) +\
               HtmlUtilClass.print_br()+\
               div_content + '</div>'

    #@staticmethod
    #def get_collapsible_div(button_caption, div_content, div_id=''):
    #    return HtmlUtilClass.get_button('collapse', div_id, button_caption) + \
    #           HtmlUtilClass.get_div('collapse', div_content, div_id)

    @staticmethod
    def get_check_or_cross(elem):
        result = '<p style="'
        result += 'color:green;	text-align:center;" >&#10004;' if elem > 0 else 'color:red;	text-align:center;" > &#10008'
        result += '</p>'
        return result

    @staticmethod
    def get_table_footer():
        return '''     </tbody>
                   </table>
                  '''

    @staticmethod
    def get_licenses_table_header(tab_id, license_permissions, categories):
        #graph_header = ['Dataset / Sub-query', 'license'  , 'reference link'] #LINK--
        graph_header = ['Dataset / Sub-query', 'license'  ]#, 'reference link'] #LINK--


        result = HtmlUtilClass.print_legend()

        result += '''<table id='''+tab_id+''' border=1px>
                        <thead>
                            <tr>
                 '''

        for elem in graph_header:
            result += '<th rowspan="2" class="license_table_header_element"><b>'+elem+'</b></th>'

        result += '<th colspan="'+str(len(license_permissions)) + '" class="license_table_header_element" ><b>conditions</b></th>'
        result += '<th colspan="'+str(len(categories)) + '" class="license_table_header_element"><b>user categories</b></th>'

        result += '</tr>'

        result += '<tr>'

        count = 0
        for elem in sorted(license_permissions.keys()):
            result += '<th class=" '
            result += ' duty ' if license_permissions[elem].is_duty() else ' permission '
            result += ' table_header_exterior_left_element"' if count == 0 else \
                      ' table_header_exterior_right_element"' if count == len(license_permissions)-1 else ' table_header_interior_element"'
            result += '"><b><div class="prova"><span> '+str(elem)+'</span></div></b></td>'
            count += 1

        count = 0
        for elem in sorted(categories):
            result += '<th class='
            result += '"table_header_exterior_left_element"' if count == 0 else \
                      '"table_header_exterior_right_element"' if count == len(categories)-1 else '"table_header_interior_element"'
            result += '"><b><div class="prova"><span> '+str(elem)+'</span></div></b></td>'
            count+=1

        result += '</tr >'
        result += '''
                        </thead>
                    <tbody>
                 '''

        return result

    @staticmethod
    def get_list_element(elem, link=None, isBold = False, class_name=None):
        result = '<li>'
        result += '<b>'+str(elem)+': </b>' if isBold else str(elem)
        result += '<a href=="'+link+'">'+link+'</a></li>'if link else ''
        return result


    @staticmethod
    def get_list_element_for_tab(elem, class_name, data_tab):
        result = '<li '
        result += ' class="'+class_name+'"' if class_name is not None else ''
        result += ' data-tab="'+data_tab+'"' if data_tab is not None else ''
        result += '>'
        result += str(elem)

        return  result


    #*********************************************************************************************************
    #**************************************  MANAGE TABLE  ***************************************************
    #*********************************************************************************************************
    @staticmethod
    def get_table_header(tab_id, col_headers):
        result = '''<table id='''+tab_id+ ''' border=1px>
                        <thead>
                 '''

        for elem in col_headers:
               result += '<td><b>'+elem+'</b></td>'

        result += '''
                        </thead>
                    <tbody>
                 '''
        return result

    @staticmethod
    def get_query_results_title(sub_query):
        result = '<h1>'
        if sub_query:
            result += 'SUB-'
        result += 'QUERY '
        result += 'RESULTS</h2>'
        return result

    @staticmethod
    def pretty_print_query_string(sparql_query, name, enriched=False):
        sparql_query = sparql_query.replace('<', '&lt;')
        sparql_query = sparql_query.replace('>', '&gt;')
        sparql_query = sparql_query.replace('\n', '<br/>')
        for keyword in HtmlUtilClass.get_sparql_keywords():
            sparql_query = sparql_query.replace(keyword, "<b>"+keyword+"</b>")

        title = 'Input query:' if not enriched else 'Enriched query:'

        result = HtmlUtilClass.print_br()
        result += HtmlUtilClass.print_title(title, 3, False, False, 'query_title')
        result += HtmlUtilClass.get_div_header('query', name )
        result += sparql_query
        result += '</div> '
        return result

    @staticmethod
    def get_table(tab_id, col_headers, elem_list):
        result = HtmlUtilClass.get_table_header(tab_id, col_headers)
        for elem in elem_list:
            result += '<tr>'
            result += '<td>'+elem+'</td>'
            result += '</tr>'
        result += HtmlUtilClass.get_table_footer()

        return result


    @staticmethod
    def get_vars_table(tab_id, col_header, elem_list):
        headers = [col_header , 'dataset']
        result = HtmlUtilClass.get_table_header(tab_id, headers)
        already_added_elements = set()
        for elem in elem_list:
            if not HtmlUtilClass.contains_ignore_case(already_added_elements, elem):
                result += '<tr>'
                result += '<td>'+elem+'</td>'
                result += '<td>'+elem[elem.rfind('/')+1:len(elem)]+'</td>'
                result += '</tr>'

            already_added_elements.add(elem)
        result += HtmlUtilClass.get_table_footer()

        return result


    #*********************************************************************************************************
    #**********************************  PRETTY PRINT LICENSE  ***********************************************
    #*********************************************************************************************************
    @staticmethod
    def print_single_license_row(graph, license_structure, license_permissions, final_license=False):
        result  = '<tr '
        result += ('class="' + ('invalid_license' if not license_structure.valid else 'valid_license') + '"') if final_license else ''
        result +=' >'
        result += '<td class="table_exterior_left_element" ><p>'+graph+'</td>'
        result += '<td class="table_exterior_left_element" ><p>'+license_structure.lic_desc+'</td>'
        #result += '<td class="table_exterior_left_element" ><p><a href="'+license_structure.lic_link+'">'+license_structure.lic_link+'</a></td>' #LINK--

        count = 0
        for permission in sorted(license_structure.perm.keys()):
            result += '<td class="'
            result += '' if final_license else \
                         'duty ' if license_permissions[permission].is_duty() else \
                         'permission '
            result += ' table_exterior_left_element">' if count == 0 else ' table_interior_element">'
            result += HtmlUtilClass.get_check_or_cross(license_structure.perm[permission])
            result += '</td>'
            count += 1

        count = 0
        for category in sorted(license_structure.cat.keys()):
            result += '<td class='
            result += '"table_exterior_left_element">' if count == 0 else '"table_exterior_right_element">' \
                      if count == len(license_structure.cat)-1 else '"table_interior_element">'
            result += HtmlUtilClass.get_check_or_cross(license_structure.cat[category])
            result += '</td>'
            count += 1

        result += '</tr>'

        return result


    @staticmethod
    def print_legend():
        result ='<ul>'
        result = '<li class="duty"> Condition is a Duty </li>'
        result += '<li class="permission"> Condition is a Right</li>'
        result +='</ul>'
        return HtmlUtilClass.get_titled_div('Legend:', result, 'legend result')


    @staticmethod
    def print_connection_graph_row(graph, category_array, permissions):
        result  = '<tr>'
        result += '<td class="table_exterior_left_element" ><p>'+graph+'</td>'
        result += '<td class="table_exterior_left_element" ><p></td>'
        #result += '<td class="table_exterior_left_element" ><p></td>' #LINK--

        count = 0
        for elem in sorted(permissions.keys()):
            result += '<td class="'
            result += ' duty ' if permissions[elem].is_duty() else ' permission '
            result += ' table_exterior_left_element">' if count == 0 else ' table_interior_element">'
            result += '</td>'
            count += 1


        count = 0
        for category in sorted(category_array.keys()):
            result += '<td class='
            result += '"table_exterior_left_element">' if count == 0 else '"table_exterior_right_element">' \
                      if count == len(category_array)-1 else '"table_interior_element">'
            result += HtmlUtilClass.get_check_or_cross(category_array[category])
            result += '</td>'
            count += 1

        result += '</tr>'

        return result

    @staticmethod
    def print_title(title, title_level, break_row=False, hr=False, class_name=None):
        result = '<br/>' if break_row else ''
        result += '<h'+str(title_level)+ ' class="' +\
                  (class_name if class_name is not None else '') +\
                  '">'+title+'</h'+str(title_level)+'>'
        return result

    @staticmethod
    def get_stylesheet_link(stylesheet_name):
        return '<head><LINK href="'+stylesheet_name+'" rel="stylesheet" type="text/css">'


    @staticmethod
    def get_button(class_name, id, name):
        return '<br/><button class="expand" data-toggle="'+class_name+'" data-target="#'+id+'">'+name+'</button>'


    @staticmethod
    def pretty_print_single_license_category_table(tab_id, license_name, list, title_array):
        result = HtmlUtilClass.get_table_header(tab_id, ['#', license_name])
        for i in range(0, len(list)):
            result += '<tr>'
            result += '<td>'
            result += HtmlUtilClass.get_check_or_cross(list[i])
            result += '</td>'
            result += '<td>'
            result += title_array[i]
            result += '</td>'
            result += '</tr>'
        result += HtmlUtilClass.get_table_footer()
        return result


    @staticmethod
    def pretty_print_single_license_category_table(tab_id, license_name, perm_or_cat):
        result = HtmlUtilClass.get_table_header(tab_id, ['#', license_name])
        for key in sorted(perm_or_cat.keys()):
            result += '<tr>'
            result += '<td>'
            result += HtmlUtilClass.get_check_or_cross(perm_or_cat[key])
            result += '</td>'
            result += '<td>'
            result += key
            result += '</td>'
            result += '</tr>'
        result += HtmlUtilClass.get_table_footer()
        return result


    @staticmethod
    def contains_ignore_case(list, elem):
        for el in list:
            if elem.lower() in el.lower():
                return True

    @staticmethod
    def discard_ignore_case(list, elem):
        elem_to_discard = set()
        for el in list:
            if elem.lower() in el.lower():
                elem_to_discard.add(el)

        for el in elem_to_discard:
            list.discard(el.lower())


    @staticmethod
    def print_br():
        return '<br/>'

    @staticmethod
    def print_hr():
        return '<hr/>'

    @staticmethod
    def get_sparql_keywords():
        return ["GROUP_CONCAT ",
                        "DATATYPE ",
                        "BASE ",
                        "PREFIX ",
                        "SELECT ",
                        "SELECT ",
                        "CONSTRUCT ",
                        "DESCRIBE ",
                        "ASK ",
                        "FROM ",
                        "NAMED ",
                        "ORDER ",
                        "BY ",
                        "LIMIT ",
                        "ASC ",
                        "DESC ",
                        "OFFSET ",
                        "DISTINCT",
                        "REDUCED ",
                        "WHERE ",
                        "GRAPH ",
                        "OPTIONAL ",
                        "UNION ",
                        "FILTER ",
                        "GROUP ",
                        "HAVING ",
                        "AS ",
                        "VALUES ",
                        "LOAD ",
                        "CLEAR ",
                        "DROP ",
                        "CREATE ",
                        "MOVE ",
                        "COPY ",
                        "SILENT ",
                        "INSERT ",
                        "DELETE ",
                        "DATA ",
                        "WITH ",
                        "TO ",
                        "USING ",
                        "NAMED ",
                        "MINUS ",
                        "BIND ",
                        "LANGMATCHES ",
                        "LANG ",
                        "BOUND ",
                        "SAMETERM ",
                        "ISIRI ",
                        "ISURI ",
                        "ISBLANK ",
                        "ISLITERAL ",
                        "REGEX ",
                        "TRUE ",
                        "FALSE ",
                        "UNDEF ",
                        "ADD ",
                        "DEFAULT ",
                        "ALL ",
                        "SERVICE ",
                        "INTO ",
                        "IN ",
                        "NOT ",
                        "IRI ",
                        "URI ",
                        "BNODE ",
                        "RAND ",
                        "ABS ",
                        "CEIL ",
                        "FLOOR ",
                        "ROUND ",
                        "CONCAT ",
                        "STRLEN ",
                        "UCASE ",
                        "LCASE ",
                        "ENCODE_FOR_URI ",
                        "CONTAINS ",
                        "STRSTARTS ",
                        "STRENDS ",
                        "STRBEFORE ",
                        "STRAFTER ",
                        "YEAR ",
                        "MONTH ",
                        "DAY ",
                        "HOURS ",
                        "MINUTES ",
                        "SECONDS ",
                        "TIMEZONE ",
                        "TZ ",
                        "NOW ",
                        "UUID ",
                        "STRUUID ",
                        "MD5 ",
                        "SHA1 ",
                        "SHA256 ",
                        "SHA384 ",
                        "SHA512 ",
                        "COALESCE ",
                        "IF ",
                        "STRLANG ",
                        "STRDT ",
                        "ISNUMERIC ",
                        "SUBSTR ",
                        "REPLACE ",
                        "EXISTS ",
                        "COUNT ",
                        "SUM ",
                        "MIN ",
                        "MAX ",
                        "AVG ",
                        "SAMPLE ",
                        "SEPARATOR ",
                        "STR ",
                        "OPTION ",
                        "INFERENCE "
                        "DEFINE "]
