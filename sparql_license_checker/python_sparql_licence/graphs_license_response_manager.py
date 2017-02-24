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

from SPARQLWrapper import SPARQLWrapper, JSON
import pymysql
import configparser
import copy
from HtmlUtilClass import HtmlUtilClass
from exceptions import SparqlQueryServerResponseException
from license_permissions import LicensePermissions
from graphs_queries_generator import GraphsQueriesGenerator
from query_result import QueryResult

class GraphsLicenseResponseManager:

    def __init__(self):

        config = configparser.ConfigParser()
        config.read("config.cfg")

        self.licenses_without_cat = {}
        self.licenses_available_for_cat = {}

        self.host = config.get("Database", "host")
        self.port = int(config.get("Database", "port"))
        self.user = config.get("Database", "user")
        self.password = config.get("Database", "password")
        self.db = config.get("Database", "db")

        self.endpoint = config.get("Endpoint", "endpoint")

        self.debug = str(config.get("Debug", "enable_debug")).lower() == 'true'

        cnx = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, db=self.db)

        self.license_permissions = self.load_permission_duty(cnx)
        self.categories = self.load_categories(cnx)
        self.queries_cache = {}



        self.final_license = None
        self.ul_tab_chooser = ''


    def load_permission_duty(self, cnx):
        query = "SELECT PId, description, duty FROM lic_perm_cond order by PId asc"
        cursor = cnx.cursor()
        cursor.execute(query)
        license_corr = {}

        for (pid, desc, duty) in cursor:
            license_corr[desc] = LicensePermissions(duty, desc, pid)

        return license_corr

    def load_categories(self, cnx):
        query = "SELECT CatId, name FROM lic_categories order by CatId asc"
        cursor = cnx.cursor()
        cursor.execute(query)
        categories = []
        for (catId, name) in cursor:
            categories.insert((catId-1), name)

        return categories

    def set_query(self, queries_str):
        self.query = queries_str

    def get_proper_results(self, enriched_query, sub_query):

        if str(enriched_query.sparql_query) in self.queries_cache.keys():
            print('CACHING')
            return self.queries_cache[str(enriched_query.sparql_query)]

        var_list_result = {}

        enriched_query_string = ''

        if not sub_query:
            print('***CHECK RESULTS****')
            #CHECK Solution to original query
            new_sparql_query = copy.deepcopy(enriched_query.sparql_query)
            if not new_sparql_query.prefixes:
                new_sparql_query.prefixes = enriched_query.prefixes
            new_sparql_query.modifiers['limit'] = '1'
            results = self.get_results_from_endpoint(new_sparql_query)
            check = self.elab_results(enriched_query, results, {})
            if not check or ( not check['result_graphs'] and not check['passage_graphs']):
                raise SparqlQueryServerResponseException('QUERY RETURNED NO RESULTS')



        if not enriched_query.get_enriched_query().modifiers['projection']:
            return {'result_graphs': set(), 'passage_graphs': set()}, ""



        if enriched_query.get_from_clauses()\
                and enriched_query.get_from_named_clauses() \
                and enriched_query.get_var_graph_names():

            print('****FROM FROM NAMED e GRAPH***')
            #FROM NAMED e GRAPH variabili
            new_sparql_query = copy.deepcopy(enriched_query.sparql_query)
            new_sparql_query.modifiers = {
                                            'order': '',
                                            'group': '',
                                            'projection': enriched_query.get_var_graph_names(),
                                            'distinct_reduced': 'DISTINCT',
                                            'offset': '',
                                            'limit': ''
                                          }
            results = self.get_results_from_endpoint(new_sparql_query)
            values_dict = {}
            graphs = self.elab_results(enriched_query, results, var_list_result, values_dict)

            enriched_query_string = str(new_sparql_query)

            #FROM e triplette
            new_sparql_query = copy.deepcopy(enriched_query.enriched_query)
            new_sparql_query.group_graph_pattern.values.extend(self.generate_values_list(values_dict))
            #new_sparql_query.from_named_clauses = new_sparql_query.from_clauses
            new_sparql_query.from_named_clauses = new_sparql_query.from_clauses
            results = self.get_results_from_endpoint(new_sparql_query)
            var_graphs_graphs = self.elab_results(enriched_query, results, var_list_result)

            graphs = self.do_graphs_union(graphs, var_graphs_graphs)

            enriched_query_string += '<br/>' +str(new_sparql_query)

        if enriched_query.get_from_clauses()\
                and enriched_query.get_from_named_clauses() \
                and not enriched_query.get_var_graph_names():

            print('****FROM FROM NAMED No GRAPH ***')
            new_sparql_query = copy.deepcopy(enriched_query.get_enriched_query())
            #new_sparql_query.from_clauses = [] #TODO REMOVE?
            new_sparql_query.from_named_clauses = new_sparql_query.from_clauses
            results = self.get_results_from_endpoint(new_sparql_query)
            graphs = self.elab_results(enriched_query, results, var_list_result)
            graphs = self.do_graphs_intersection(graphs, enriched_query.get_from_clauses())

            enriched_query_string = str(new_sparql_query)


        if enriched_query.get_from_clauses()\
                and not enriched_query.get_from_named_clauses() \
                and enriched_query.get_var_graph_names():

            print('***FROM e GRAFI ****')
            new_sparql_query = copy.deepcopy(enriched_query.sparql_query)
            new_sparql_query.modifiers = {
                                            'order': '',
                                            'group': '',
                                            'projection': enriched_query.get_var_graph_names(),
                                            'distinct_reduced': 'DISTINCT',
                                            'offset': '',
                                            'limit': ''
                                          }
            results = self.get_results_from_endpoint(new_sparql_query)
            values_dict = {}
            var_graphs_graphs = self.elab_results(enriched_query, results, var_list_result, values_dict)

            enriched_query_string = str(new_sparql_query)

            new_sparql_query = copy.deepcopy(enriched_query.get_enriched_query())
            new_sparql_query.from_named_clauses = new_sparql_query.from_clauses
            new_sparql_query.group_graph_pattern.values = self.generate_values_list(values_dict)
            results = self.get_results_from_endpoint(new_sparql_query)
            graphs = self.elab_results(enriched_query, results, var_list_result)
            graphs = self.do_graphs_intersection(graphs, enriched_query.get_from_clauses())

            graphs = self.do_graphs_union(graphs, var_graphs_graphs)

            enriched_query_string += '<br/>' +str(new_sparql_query)

        if enriched_query.get_from_clauses()\
                and not enriched_query.get_from_named_clauses() \
                and not enriched_query.get_var_graph_names():
            print('***FROM e triple libere****')
            new_sparql_query = copy.deepcopy(enriched_query.get_enriched_query())
            new_sparql_query.from_named_clauses = new_sparql_query.from_clauses
            results = self.get_results_from_endpoint(new_sparql_query)
            graphs = self.elab_results(enriched_query, results, var_list_result)
            graphs = self.do_graphs_intersection(graphs, enriched_query.get_from_clauses())

            enriched_query_string = str(new_sparql_query)

        if not enriched_query.get_from_clauses()\
                and enriched_query.get_from_named_clauses() \
                and enriched_query.get_var_graph_names():

            print('**** FROM NAMED e GRAPH ***')
            new_sparql_query = copy.deepcopy(enriched_query.sparql_query)
            new_sparql_query.modifiers = {
                                            'order': '',
                                            'group': '',
                                            'projection': enriched_query.get_var_graph_names(),
                                            'distinct_reduced': 'DISTINCT',
                                            'offset': '',
                                            'limit': ''
                                          }
            results = self.get_results_from_endpoint(new_sparql_query)
            graphs = self.elab_results(enriched_query, results, var_list_result)

            enriched_query_string = str(new_sparql_query)

        if not enriched_query.get_from_clauses()\
                and not enriched_query.get_from_named_clauses():

            print('***** NO FROM NO FROM NAMED *******')
            results = self.get_results_from_endpoint(enriched_query.get_enriched_query())
            graphs = self.elab_results(enriched_query, results, var_list_result)

            enriched_query_string = str(enriched_query.get_enriched_query())

        if enriched_query.stat_graph_iris:
            graphs['result_graphs'] = graphs['result_graphs'].union(enriched_query.stat_graph_iris)

        table = ''
        for var in sorted(var_list_result.keys()):
            table += HtmlUtilClass.get_vars_table("graphs", var, var_list_result[var])
        var_list_result = HtmlUtilClass.get_titled_div('Graphs', table, 'vars')

        self.queries_cache[str(enriched_query.sparql_query)] = graphs, var_list_result, enriched_query_string

        return graphs, var_list_result, enriched_query_string

    def get_results_from_endpoint(self, query):
        wrapper = SPARQLWrapper(self.endpoint)
        wrapper.setReturnFormat(JSON)
        query_string = str(query)
        print('********************************************************************')
        print(query_string)
        wrapper.setQuery(query_string)
        result = wrapper.query().convert()
        print('********************************************************************')
        return result

    def do_graphs_intersection(self, graph_structure, graph_set):
        new_graph_structure = {}
        new_graph_structure['passage_graphs'] = graph_structure['passage_graphs'].intersection(graph_set)
        new_graph_structure['result_graphs'] = graph_structure['result_graphs'].intersection(graph_set)
        return new_graph_structure

    def do_graphs_union(self, graph_structure1, graph_structure2):
        new_graph_structure = {}
        new_graph_structure['passage_graphs'] = graph_structure1['passage_graphs'].union(graph_structure2['passage_graphs'])
        new_graph_structure['result_graphs'] = graph_structure1['result_graphs'].union(graph_structure2['result_graphs'])
        return new_graph_structure

    def elab_results(self, enriched_query, results, var_dict, values_string_list=None):

        result_graphs = set()
        passage_graphs = set()


        if results:
            var_list = results['head']['vars']

            for var in var_list:
                if not HtmlUtilClass.contains_ignore_case(var_dict.keys(), var):
                    var_dict[var] = set()

            res = results['results']

            for elem in res['bindings']:
                for var in var_list:
                    if var in elem.keys():
                        graph = elem[var]['value']
                        if var in elem.keys():
                            var_dict[var].add(graph)

                            if values_string_list is not None and ('?'+var) in enriched_query.var_graph_names:
                                if '?'+var not in values_string_list.keys():
                                    values_string_list['?'+var] = set()

                                if not HtmlUtilClass.contains_ignore_case(values_string_list['?'+var], graph):
                                    values_string_list['?'+var].add(graph)

                            if HtmlUtilClass.contains_ignore_case(enriched_query.graphs_vars_relation.keys(), ('?'+var)):
                                passage_graphs.discard(graph)
                                HtmlUtilClass.discard_ignore_case(passage_graphs, graph)

                                if not HtmlUtilClass.contains_ignore_case(result_graphs, graph):
                                    result_graphs.add(graph)
                            else:

                                if not HtmlUtilClass.contains_ignore_case(passage_graphs,graph) and graph not in result_graphs :
                                    passage_graphs.add(graph)

        graphs = {'result_graphs': result_graphs, 'passage_graphs': passage_graphs}
        return graphs


    def clear_attributes_value(self):
        self.graphs = []
        self.final_license = None


    #*******************************************************************************************************************
    #**************************************** SEND QUERIES TO ENDPOINT *************************************************
    #*******************************************************************************************************************


    def send_queries_to_endpoint(self, user_cat_id):
        self.user_cat_id = user_cat_id
        self.clear_attributes_value()

        self.result = {}

        self.ul_tab_chooser = '<ul class="tabs">'
        self.i = 0
        self.manage_query(self.query)

        self.ul_tab_chooser += '</ul>'

    def manage_queries(self, queries):

        for query in queries:
            self.manage_query(query)

    def manage_query(self, query):

        sub_query = (self.i > 0)

        div_name = 'sub_query_main_div' if sub_query else 'query_main_div'
        if not sub_query:
            div_name+= ' current'
        div_name += ' tab-content'

        graph_id = 'query_result_'+str(self.i)

        li_content = ('Sub-' if sub_query else 'Main ') + 'Query ' + (str(self.i) if sub_query else  '')
        li_class = 'tab-link' + (' current' if not sub_query else '')
        self.ul_tab_chooser += HtmlUtilClass.get_list_element_for_tab(li_content, li_class, graph_id)
        self.i+=1

        graphs, graphs_dataset_table, enriched_query_string = self.get_proper_results(query, sub_query)
        query_result = QueryResult(self.license_permissions, self.categories, graph_id, div_name, li_content, query)
        self.manage_queries(query.get_subquery_enriched_queries())
        query_result.set_graph(graphs)
        query_result.set_graphs_dataset_table(graphs_dataset_table)
        query_result.set_sub_query(sub_query)
        query_result.set_enriched_query_string(enriched_query_string)

        query.query_result = query_result


    def manage_final_result(self, result, cnx):
        if self.user_cat_id and self.user_cat_id != 'null':
            if self.final_license.cat[self.user_cat_id] == 0:
                result = HtmlUtilClass.print_title('Category Permission Error', 1)
                result += '<p> Attention the selected Category does not have the permission to execute the query. '
                result += '<p> The following graphs have restricted access for category : ' + self.user_cat_id
                result += self.query.query_result.print_dataset_without_category(self.user_cat_id, self.query.query_result.licenses_without_cat)
                result = HtmlUtilClass.get_div('tab-content current', result, 'category_error')
                alternative_query_result = self.print_alternative_query_results(cnx)

                result += alternative_query_result

                ul_category_error = '<ul class="tabs">'
                ul_category_error += HtmlUtilClass.get_list_element_for_tab('Category Error', 'tab-item current', 'category_error')
                ul_category_error += HtmlUtilClass.get_list_element_for_tab('Query modification suggestion', 'tab-item', 'modified_query_results')
                ul_category_error += '</ul>'
                if alternative_query_result:
                    result = ul_category_error + result

            else:
                result = HtmlUtilClass.print_title('Computed Query license for category '+ self.user_cat_id, 1, True)
                result += '<p> The selected Category will be subject to the following license when using the data resulting from the query. '
                result += self.query.query_result.pretty_print_final_license('final license computation for category ' + self.user_cat_id, self.final_license)
                result += self.query.query_result.check_database_licenses(self.final_license,'computed query license for category ' + self.user_cat_id, cnx)

                result = HtmlUtilClass.get_div('result',result,'final_category_license')

        return HtmlUtilClass.get_div('main_result', result)

    def get_license_response(self):
        cnx = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, db=self.db)
        result = self.ul_tab_chooser

        string_result, self.final_license = self.query.query_result.compute_query_result_license_array(cnx)
        result += string_result

        result = self.manage_final_result(result, cnx)
        cnx.close()
        return result


    def print_alternative_query_results(self, cnx):

        if not self.query.query_result.get_licenses_available_for_cat_recursively(self.user_cat_id):
            return ''

        added_from = False

        modified_query = copy.deepcopy(self.query.query_result.get_enriched_query_wrapper().sparql_query)

        modified_query.from_clauses = []
        modified_query.from_named_clauses = []

        for graph in self.query.query_result.get_licenses_available_for_cat_recursively(self.user_cat_id):
            added_from = True
            graph_name = '<'+graph+'>'
            modified_query.from_clauses.append(graph_name)
            modified_query.from_named_clauses.append(graph_name)

        if not added_from:
            return ''

        result = HtmlUtilClass.print_title("Query modification Suggestion", 1)
        result += '\n\tProposed query can be executed by selected category in the following modified form:'

        try:

            mod_query_glm = GraphsLicenseResponseManager()
            result += HtmlUtilClass.pretty_print_query_string(str(modified_query), 'alternative_query')
            print('******************************************************************************************')
            print('********************                QUERY MODIFICATION            ************************')
            print('******************************************************************************************')
            graphs_queries_generator = GraphsQueriesGenerator()
            graphs_queries = graphs_queries_generator.get_enriched_query_from_query(str(modified_query))
            mod_query_glm.set_query(graphs_queries)
            mod_query_glm.send_queries_to_endpoint(None)
            mod_query_glm.get_license_response()

            result += mod_query_glm.query.query_result.pretty_print_final_license('final license computation for category ' + self.user_cat_id, mod_query_glm.final_license)
            result += mod_query_glm.query.query_result.check_database_licenses(mod_query_glm.final_license,'computed query license for category ' + self.user_cat_id, cnx)

            result = str(result).replace('Computed final license for category '+str(self.user_cat_id), 'Modified Query License Computation Results')

        except:
            return ''


        return HtmlUtilClass.get_div('tab-content', result, 'modified_query_results')


    def set_sparql_query_structure(self, sparql_query):
        self.sparql_query = sparql_query


    def set_has_free_triple(self, has_free_triple):
        self.has_free_triple = has_free_triple

    def set_has_variable_graph(self, has_variable_graph):
        self.has_variable_graph = has_variable_graph

    def generate_values_list(self, values_dict):

        value_clauses = []
        for var in values_dict.keys():

            value_clause = 'VALUES '+var+'{'
            for graph in values_dict[var]:
                value_clause += '<'+graph+'> '
            value_clause += '}'
            value_clauses.append(value_clause)
        return value_clauses



