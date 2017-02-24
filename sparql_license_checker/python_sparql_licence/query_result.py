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

from HtmlUtilClass import HtmlUtilClass
from exceptions import SparqlQueryServerResponseException
from license_structure import LicenseStructure


class QueryResult:

    def __init__(self, license_permissions, license_categories, graph_id, class_name, query_name, enriched_query_wrapper):
        self.query_involved_graphs = {}
        self.sub_query = False
        self.licenses_array = []
        self.graphs_dataset_table = ''
        self.license_permissions = license_permissions
        self.categories = license_categories
        self.graphs_attribution = {}
        self.licenses_without_cat = {}
        self.licenses_available_for_cat = {}
        self.categories_array = []
        self.graph_id = graph_id
        self.class_name = class_name
        self.final_license_categories = None
        self.query_name = query_name
        self.enriched_query_wrapper = enriched_query_wrapper
        self.result = ''
        self.enriched_query_string = ''

    def set_graph(self, graph):
        self.query_involved_graphs = graph

    def set_sub_query(self, sub_query=True):
        self.sub_query = sub_query

    def is_sub_query(self):
        return self.sub_query

    def set_graphs_dataset_table(self, table):
        self.graphs_dataset_table = table

    def get_enriched_query_wrapper(self):
        return self.enriched_query_wrapper

    def set_enriched_query_wrapper(self, enriched_query_wrapper):
        self.enriched_query_wrapper = enriched_query_wrapper


    def set_enriched_query_string(self, enriched_query_string):
        self.enriched_query_string = enriched_query_string

    def compute_query_result_license_array(self, cnx):

        self.final_license = None
        self.licenses_array = []
        result = ''

        if not self.query_involved_graphs:
            raise SparqlQueryServerResponseException('QUERY RETURNED NO RESULTS 1')


        # ***** DIV TAB MANAGEMENT *****

        result += HtmlUtilClass.get_div_header(self.class_name, self.graph_id)

        #************************************

        result += HtmlUtilClass.get_query_results_title(self.sub_query)

        result += HtmlUtilClass.pretty_print_query_string(str(self.enriched_query_wrapper.get_sparql_query()), 'input_query_string_'+ self.graph_id)
        
        result += HtmlUtilClass.pretty_print_query_string(self.enriched_query_string, 'enriched_query_string_'+ self.graph_id, True)

        result += self.graphs_dataset_table

        #****************************************************************
        #**********************SUB QUERY MANAGEMENT**********************
        #****************************************************************
        sub_queries_result_string = ''
        for sub_query_wrapper in self.enriched_query_wrapper.subquery_enriched_queries_wrapper:
            sub_result_string, sub_query_license = sub_query_wrapper.query_result.compute_query_result_license_array(cnx)
            sub_queries_result_string += sub_result_string
            if sub_query_license:
                self.licenses_array.append(sub_query_license)
                self.licenses_without_cat = sub_query_wrapper.query_result.licenses_without_cat.copy()

        #****************************************************************

        if not self.query_involved_graphs['result_graphs'] and not self.query_involved_graphs['passage_graphs'] \
                and not self.licenses_array:
            print(self.query_involved_graphs)
            self.result = result+'</div>'+sub_queries_result_string
            return result+'</div>'+sub_queries_result_string, None


        if self.query_involved_graphs['passage_graphs']:
            result += HtmlUtilClass.print_title('Connection Graphs', 2, False, True)
            result += self.manage_single_query_graph(self.query_involved_graphs['passage_graphs'], cnx, self.sub_query, False)

        result += HtmlUtilClass.print_title('Dataset License Table - Permission/Prohibition and enabled Categories', 2, False, True)
        result += self.manage_single_query_graph(self.query_involved_graphs['result_graphs'], cnx, self.sub_query)
        result += '</div>'

        result += sub_queries_result_string

        self.result = result

        return result, self.final_license_categories

    def manage_single_query_graph(self, graph, cnx, sub_query, result_graphs=True):

        result = ''

        licenses_without_perm = {}
        global_graphs_licenses = {}

        if result_graphs:
            licenses_array = self.licenses_array.copy()
        else:
            licenses_array = []

        #Init the permission of this query with the eventual permission of sub query

        query = "SELECT PM.process, PM.source, PM.licenseModel FROM process_manager2 PM " \
                "WHERE PM.process = %s "

        cursor = cnx.cursor()

        license_table = HtmlUtilClass.get_licenses_table_header('licenses_tab',
                                                                self.license_permissions,
                                                                self.categories)

        count = 0

        for connection_cat_array in self.categories_array:
            license_table += HtmlUtilClass.print_connection_graph_row('Connection Graphs', connection_cat_array,  self.license_permissions)

        for lic in licenses_array:
            self.add_process_license_to_licenses_without_perm(licenses_without_perm, lic.lic_desc, lic)
            self.manage_missing_and_available_licenses_categories(self.licenses_without_cat, lic.lic_desc, lic.lic_desc, lic)
            license_table += HtmlUtilClass.print_single_license_row(lic.lic_desc, lic, self.license_permissions, True)
            count += 1

        proc_name_set = set()

        for g in graph:

            proc_name = g[g.rfind('/')+1:len(g)]
            elements = cursor.execute(query, proc_name)

            if elements == 0:
                license_structure = LicenseStructure(self.license_permissions, self.categories).set_no_license()
                licenses_array.append(license_structure)
                if not HtmlUtilClass.contains_ignore_case(proc_name_set, proc_name):
                    self.manage_missing_and_available_licenses_categories(self.licenses_without_cat, proc_name, g, license_structure)
                    license_table += HtmlUtilClass.print_single_license_row(proc_name, license_structure, self.license_permissions)


            else:
                for (process, attribution, LMId) in cursor:
                    license_structure = LicenseStructure.retrieve_license(cnx, LMId, self.license_permissions, self.categories, {})
                    if not HtmlUtilClass.contains_ignore_case(proc_name_set, proc_name):
                        self.add_process_license_to_licenses_without_perm(licenses_without_perm, g, license_structure)
                        self.manage_missing_and_available_licenses_categories(self.licenses_without_cat, process, g, license_structure)
                        license_table += HtmlUtilClass.print_single_license_row(proc_name, license_structure, self.license_permissions)

                    if license_structure.perm['attribution'] == 1:
                        self.graphs_attribution[g] = attribution

                    licenses_array.append(license_structure)
                    global_graphs_licenses[g] = license_structure

            proc_name_set.add(proc_name.lower())

        cursor.close()
        self.final_license_categories = self.elab_final_license_and_categories(licenses_array)
        result_str = self.print_final_license_and_categories(cnx, licenses_without_perm, self.licenses_without_cat, self.final_license_categories, licenses_array, global_graphs_licenses, result_graphs, sub_query)


        # Adding the final license to the licenses of the query

        if result_graphs:
            self.licenses_array.append(self.final_license_categories)

        self.categories_array.append(self.final_license_categories.cat)

        license_table += HtmlUtilClass.print_single_license_row('<b>COMPUTED RESULT LICENSE</b>', self.final_license_categories, self.license_permissions, True)
        license_table += '</table>'
        result += license_table
        result += result_str
        return result


    def add_process_license_to_licenses_without_perm(self, licenses_without_perm, process, license_structure):
        for permission in sorted(self.license_permissions.keys()):

            if (self.license_permissions[permission].is_duty() and license_structure.perm[permission] == 1)\
                    or (not self.license_permissions[permission].is_duty() and license_structure.perm[permission] == 0):

                    if permission not in licenses_without_perm.keys():
                        licenses_without_perm[permission] = set()
                    licenses_without_perm[permission].add((process, license_structure.lic_desc))



    def manage_missing_and_available_licenses_categories(self, licenses_without_cat, process, g, license_structure):
        for category in sorted(self.categories):
            if license_structure.cat[category] == 0:
                if category not in licenses_without_cat.keys():
                    licenses_without_cat[category] = set()
                licenses_without_cat[category].add(g)
            else:
                if category not in self.licenses_available_for_cat.keys():
                    self.licenses_available_for_cat[category] = set()
                self.licenses_available_for_cat[category].add(g)


    def elab_final_license_and_categories(self, licenses_array):

        #****** ELABORATE FINAL LICENSE AND CATEGORIES *****
        final_license = LicenseStructure(self.license_permissions, self.categories)
        final_license.lic_desc = self.query_name

        final_license = self.elab_final_license(licenses_array, final_license)
        final_license = self.elab_final_categories(licenses_array, final_license)
        #****************************************************

        return final_license

    #*********************************************************************************************************
    #**************************************  FINAL LICENSE ***************************************************
    #*********************************************************************************************************
    def elab_final_license(self, licenses_array, final_license):

        for permission in sorted(self.license_permissions.keys()):
            final_license.perm[permission] = 0 if self.license_permissions[permission].is_duty() else 1

        print("final_license:"+str(final_license.perm))

        for lic in licenses_array:
            for permission in sorted(self.license_permissions.keys()):
                if not self.license_permissions[permission].is_duty():
                    final_license.perm[permission] *= lic.perm[permission]
                else:
                    final_license.perm[permission] = min(final_license.perm[permission]+lic.perm[permission], 1)

        return final_license


    #*********************************************************************************************************
    #**************************************  FINAL CATEGORIES ************************************************
    #*********************************************************************************************************
    def elab_final_categories(self, licenses_array, final_license):
        for category in sorted(self.categories):
            final_license.cat[category] = 1

        for licenses in licenses_array:
            for category in sorted(self.categories):
                final_license.cat[category] *= licenses.cat[category]

        for category_array in self.categories_array:
            for category in sorted(category_array.keys()):
                final_license.cat[category] *= category_array[category]

        print('final categories: '+str(final_license.cat))
        return final_license



    def print_final_license_and_categories(self,cnx, licenses_without_perm, licenses_without_cat, final_license, licenses_array, global_graphs_license, result_graphs=True, sub_query=False):

        if not final_license:
            return ''

        result = self.pretty_print_licenses_without_permission(licenses_without_perm, global_graphs_license, licenses_array, final_license)

        result += self.pretty_print_licenses_without_category(licenses_without_cat, final_license)

        prefix = ''
        if result_graphs:
            prefix += 'Computed  '
        else:
            prefix += 'Connection '

        if sub_query:
            prefix += ' Sub-'

        title = prefix + 'Query License'
        title += ' and Categories'
        final_license_name = prefix + 'Query License conditions'

        final_license_str = HtmlUtilClass.print_title(title, 2, False, True)


        if final_license.perm['derivative'] == 0:
            final_license_str += HtmlUtilClass.print_title('Attention: Computed query license is an <b>INVALID</b> license. This error is caused'
                                                           ' by the presence of "no-derivative" licenses', 3)

        final_license_str += "Computed query license resulting from graphs licenses combination should have the following conditions :"
        final_license_str += self.pretty_print_final_license(final_license_name, final_license)
        final_license_str += self.check_database_licenses(final_license, final_license_name, cnx)




        if final_license.is_license_usable_by_some_category():
            final_license_str += "<br/> Categories enabled to execute the query are the following :"
            final_license_str += final_license.pretty_print_license_category_table('categories enabled to execute query', "categories enabled to execute query.", True)
            final_license_str += '<br/>'
        else:
            invalid_final_license_message = "ATTENTION: There is not a possible category authorized to use the licensed data."
            final_license_str += HtmlUtilClass.print_title(invalid_final_license_message, 3, True, True)

        result += HtmlUtilClass.get_div('final_result', final_license_str)
        result += '<br/>'

        result = HtmlUtilClass.get_div('final_license', result)

        return result

    def pretty_print_licenses_without_permission(self, licenses_without_perm, global_graphs_license, licenses_array, final_license):

        result = HtmlUtilClass.print_title('Prohibitions and Duties imposed by involved graphs/datasets licenses', 2, True, True)
        result += '<p> Computed query result license will impose the following duties and prohibitions, due to graphs/dataset licenses:'

        for key in sorted(licenses_without_perm.keys()):
            if licenses_without_perm[key]:

                lic_result = HtmlUtilClass.print_title(key, 3, False, True)

                if not self.license_permissions[key].is_duty():
                    lic_result += "<p>Attention: the following graphs/datasets are licensed with a <b>NO "+key.upper()+"</b> prohibition "

                    if key.lower() == 'derivative':
                        if final_license.perm['derivative'] == 0:
                            final_license.valid = False
                            lic_result += "<p> Attention: Due to the presence of <b>NO DERIVATIVE</b> licenses query results will be unusable." \
                                          "The Computed query license is an <b> INVALID </b> license due to the presence" \
                                          " of these <b>NO DERIVATIVE</b> licenses."

                else:
                    lic_result += "<p>Attention the following graphs/datasets are licensed with a <b>"+key.upper()+"</b> duty:"

                    if key.lower() == 'sharealike':
                        compatible = True
                        for lic in licenses_array:
                            if lic.perm['sharealike'] == 1:
                                #Se la licenza share alike garantisce un permesso che non Ã¨ dato nelle altre, le licenze non sono compatibili
                                for permission in sorted(self.license_permissions.keys()):
                                    if permission.lower() != 'sharealike':
                                        compatible = compatible and (lic.perm[permission] == final_license.perm[permission])

                        lic_result += " Due to licenses nature it's "
                        if not compatible:
                            final_license.valid = False
                            lic_result += ' <b>NOT</b> '
                        lic_result += " possible to find a license that satisfies <b>SHARE ALIKE</b> licenses duty.<br/>"

                        if not compatible:
                            lic_result += 'The <b>computed query result license</b> is then an invalid license, since it can\'t satisfy all the single graphs licenses requirements.'

                dataset_table = self.print_dataset_without_permissions(key, licenses_without_perm)
                if not dataset_table:
                    lic_result = ''
                else:
                    lic_result+=dataset_table
                lic_result += self.print_sub_queries_without_permissions(key, licenses_without_perm,  self.license_permissions[key].is_duty() )
                lic_result += self.print_possible_from_clauses_for_missing_perm(key, licenses_without_perm, global_graphs_license)
                result += HtmlUtilClass.get_div('result', lic_result)

        result = HtmlUtilClass.get_div('prohibition_duty',result)

        return result

    def pretty_print_licenses_without_category(self, licenses_without_cat, final_license):
        result =''
        if licenses_without_cat:
            result += HtmlUtilClass.print_title('Categories not authorized to execute Query', 2, True, True)
            category_dataset_table_title = '<p> The following categories are not authorized to execute query:'
            for category in sorted(self.licenses_without_cat.keys()):
                # if final_license.cat[category] == 0:
                #result += "<p>Attention the final license does not authorize query execution for the category: "+category+"</b> "
                category_result = "<h3>"+category+"</h3> "
                category_dataset_table = self.print_dataset_without_category(category, licenses_without_cat)
                if category_dataset_table:
                    result += category_dataset_table_title
                    category_result += category_dataset_table
                category_result += self.print_sub_queries_without_category(category, licenses_without_cat)
                category_result += self.print_possible_from_clauses_for_missing_cat(category)
                result += HtmlUtilClass.get_div('categories_result', category_result)

            result = HtmlUtilClass.get_div('categories',result)

        return result


    def print_dataset_without_permissions(self, condition, licenses_without_perm):

        header = ['graph', 'license']
        if condition.strip().lower() == 'attribution':
            header.append('attribution string')

        header_text = HtmlUtilClass.get_table_header(condition, header)
        result = ''
        for elem in licenses_without_perm[condition]:
            if 'sub-query' not in elem[0].lower():
                result += '<tr>'
                for el in elem:
                    result += '<td>'+el+'</td>'

                if condition.strip().lower() == 'attribution'\
                    and elem[0] is not None\
                    and elem[0] in self.graphs_attribution.keys():

                    result += '<td>'+str(self.graphs_attribution[elem[0]])+'</td>'

                result += '</tr>'
        if not result:
            return ''

        result = header_text + result + HtmlUtilClass.get_table_footer()
        return result


    def print_sub_queries_without_permissions(self, condition, licenses_without_perm, is_duty):

        result = '\nAttention the following computed sub-query license '
        result += ' impose <b> NO '+condition.upper()+'</b> prohibition ' if not is_duty else ' require  <b>'+condition.upper()+'</b> duty:'
        result +='<ul>'
        li_elements = ''
        for elem in licenses_without_perm[condition]:
            if 'sub-query' in elem[0].lower():
                li_elements += HtmlUtilClass.get_list_element(elem[1])
        if not li_elements:
            return ''
        result += li_elements
        result += '</ul>'

        return result

    def print_dataset_without_category(self, category, licenses_without_cat):

        header = ['graphs unusable by category '+category]

        header_text = HtmlUtilClass.get_table_header(category, header)
        result=''
        for elem in licenses_without_cat[category]:
            if 'sub-query' not in elem.lower():
                result += '<tr>'
                result += '<td>'+elem+'</td>'
                result += '</tr>'
        if not result:
            return ''

        result = header_text + result + HtmlUtilClass.get_table_footer()
        return result

    def print_sub_queries_without_category(self, category, licenses_without_cat):

        result = '\nAttention category '+category+' in unauthorized to execute the following sub-queries:'
        result +='<ul>'
        li_elements = ''
        for elem in licenses_without_cat[category]:
            if 'sub-query' in elem.lower():
                li_elements += HtmlUtilClass.get_list_element(elem)
        result += '</ul>'

        if not li_elements:
            return ''

        result += li_elements
        return result

    def pretty_print_final_license(self, final_license_name, final_license):
        if not final_license:
            return ''
        result = final_license.pretty_print_license_category_table('final license conditions', final_license_name)
        return result




    def print_possible_from_clauses_for_missing_cat(self, category):

        licenses_available_for_cat = self.get_licenses_available_for_cat_recursively(category)
        if not licenses_available_for_cat:
            return ''

        result = '\n\tQuery can be executed by category <b>'+category+'</b> by using the following FROM and FROM NAMED clauses:'
        result += '<ul>'
        from_li = ''
        from_named_li = ''
        for graph in licenses_available_for_cat:
            if 'sub-query' not in graph.lower():
                from_li += HtmlUtilClass.get_list_element('\n<i>FROM</i> &#60;'+graph+'&#62;')
                from_named_li += HtmlUtilClass.get_list_element('\n<i>FROM NAMED</i> &#60;'+graph+'&#62;')

        result += from_li
        result += from_named_li
        result += '</ul>'
        return HtmlUtilClass.get_div('from_category_'+category,result)

    def print_possible_from_clauses_for_missing_perm(self, permission, licenses_without_perm, global_graphs_license):

        if not permission in licenses_without_perm:
            return ''

        graphs_without_perm = set()
        for elem in licenses_without_perm[permission]:
            graphs_without_perm.add(elem[0])

        result = '\n\tThis Duty or Prohibition can be excluded using the following <i>FROM</i> and <i>FROM NAMED</i> clauses:'
        result += '<ul>'
        from_li = ''
        from_named_li = ''
        for graph in global_graphs_license.keys():
            if 'sub-query' not in graph.lower() and graph not in graphs_without_perm:
                from_li += HtmlUtilClass.get_list_element('\n<i>FROM</i> &#60;'+graph+'&#62;')
                from_named_li += HtmlUtilClass.get_list_element('\n<i>FROM NAMED</i> &#60;'+graph+'&#62;')

        if not from_li and not from_named_li:
            return  ''

        result += from_li
        result += from_named_li
        result += '</ul>'
        result = HtmlUtilClass.get_div('from', result, )
        return result


    def check_database_licenses(self, final_license, final_license_name, cnx):

        available_lic_string = self.get_available_lic_string(final_license, cnx)

        result = ''

        if available_lic_string:
            result += 'Licenses available on SiiMobility Database that satisfies computed query result license conditions are : <br/>'
            result += '<ul>'
            result += available_lic_string
            result += '</ul>'
        else:
            invalid_final_license_message = "ATTENTION: License database doesn't contain any license that satisfies computed query result license conditions."
            result += HtmlUtilClass.print_title(invalid_final_license_message, 3, True, False)

        return result

    def get_available_lic_string(self, license, cnx):
        available_lic_string = ""
        permission_string = ""

        cursor = cnx.cursor()
        for permission in sorted(license.perm.keys()):
            if license.perm[permission] == 1:
                if permission_string:
                    permission_string += ', '
                permission_string += str(permission)

        query = '''
                SELECT Q.LMid, Q.description, Q.link
                FROM (
                     SELECT L.LMid, L.description, L.link, GROUP_CONCAT(LPC.description ORDER BY LPC.description SEPARATOR ', ') as PERM
                     FROM licenses_permcond LP, licenses L, lic_perm_cond LPC
                     WHERE LP.LMid = L.LMid and LPC.Pid = LP.Pid
                     GROUP BY L.LMid ORDER BY L.Lmid desc ) as Q

                WHERE Q.PERM = %s                '''



        cursor.execute(query, [permission_string])
        for (Lmid, lic_desc, lic_link) in cursor:
            available_lic_string += HtmlUtilClass.get_list_element(lic_desc, lic_link, True)


        return available_lic_string

    def get_licenses_available_for_cat_recursively(self, category, licenses_available_for_cat=None):
        if category not in self.licenses_available_for_cat.keys():
            return set()
        if licenses_available_for_cat is None:
            licenses_available_for_cat = set()
            for elem in self.licenses_available_for_cat[category]:
                if 'sub-query' not in elem:
                    licenses_available_for_cat.add(elem)
        else:
            licenses_available_for_cat.intersection(self.licenses_available_for_cat[category])
        for sub_query_wrapper in self.enriched_query_wrapper.subquery_enriched_queries_wrapper:
            if category in sub_query_wrapper.query_result.licenses_available_for_cat.keys():
                licenses_available_for_cat.intersection(sub_query_wrapper.query_result.get_licenses_available_for_cat_recursively(category), licenses_available_for_cat)
            else:
                return set()

        return licenses_available_for_cat

