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

from rdflib.plugins import sparql

from graph_clause import GraphClause
from sparql_query import SparqlQuery
from enriched_query import EnrichedQueryWrapper
from group_graph_pattern import GroupGraphPattern
import copy
import re

class GraphsQueriesGenerator:

    def __init__(self):
        self.query = []


    def get_enriched_query_from_query(self, source_query):
        self.generate_enriched_query(source_query)
        return self.query

    def generate_enriched_query(self, source_query):
        parsed_query = sparql.parser.parseQuery(source_query)
        self.sparql_query = SparqlQuery()
        self.sparql_query.init_from_parsed_tree(parsed_query)
        self.query = self.get_enriched_query_wrapper(self.sparql_query, self.sparql_query.prefixes, self.sparql_query.from_clauses, self.sparql_query.from_named_clauses)

    def get_enriched_query_wrapper(self, sparql_query, prefixes, from_clauses, from_named_clauses):

        return self.elab_query(sparql_query, prefixes, from_clauses, from_named_clauses)


    def manage_optionals(self, optionals, enriched_query, add_graph=False):

        for optional in optionals:

            self.manage_group_graph_pattern(optional.group_graph_pattern,
                                                     enriched_query,
                                                     add_graph)


    def manage_unions(self, unions, enriched_query, add_graph=False):

        for union in unions:
            for group_graph_pattern in union.union_branches:

                self.manage_group_graph_pattern(group_graph_pattern,
                                                enriched_query,
                                                add_graph)

    def manage_binds(self, binds):
        var_associations = []
        for elem in binds:
            if '?' in elem:
                binds = re.split(r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./> ]', elem)
                var_association = [bind for bind in binds if bind.startswith('?')]
                var_associations.append(var_association)
                #print('var: ' + str(var_association))
        return var_associations

    def has_triple_vars_in_projection(self, triple, enriched_query):

        var_structure = enriched_query.get_var_structure()

        if not var_structure.projection_variables:
            #print('* projection')
            return True

        if triple.subject in var_structure.projection_variables:
            return True
        if triple.object in var_structure.projection_variables:
            return True
        if triple.predicate in var_structure.projection_variables:
            return True

        for var_bind in var_structure.var_binds:
            if triple.subject in var_bind[0] and var_bind[1] in var_structure.projection_variables:
                #print('subject in Bind')
                return True
            if triple.predicate in var_bind[0] and var_bind[1] in var_structure.projection_variables:
                #print('predicate in Bind')
                return True
            if triple.object in var_bind and var_bind[1] in var_structure.projection_variables:
                #print('object in Bind')
                return True

        return False

    def manage_triples(self, input_group_graph_pattern, enriched_query, add_graph):

        triples = input_group_graph_pattern.triples
        input_group_graph_pattern.triples = []

        for triple in triples:
            enriched_query.has_free_triples = True

            projected_variable = self.has_triple_vars_in_projection(triple, enriched_query)
            t_str = str(triple)

            if add_graph:
                graph_name = self.get_unique_graph_var_name(enriched_query.get_projection_graph_var_names(), enriched_query.var_structure)
                if projected_variable:
                    enriched_query.graphs_vars_relation[graph_name] = t_str
                graph_clause = GraphClause()
                graph_clause.var_or_term = graph_name
                group_graph_pattern = GroupGraphPattern()
                group_graph_pattern.triples.append(triple)
                graph_clause.group_graph_pattern = group_graph_pattern
                input_group_graph_pattern.graphs.append(graph_clause)


    def get_unique_graph_var_name(self, graph_var_names, var_structure):

        i = 0
        graph_var_name = '?g'+str(i)
        while graph_var_name in graph_var_names or graph_var_name in var_structure.query_var_names:
            i += 1
            graph_var_name = '?g'+str(i)

        graph_var_names.append(graph_var_name)
        return graph_var_name

    def elab_query(self, input_query, prefixes, from_clauses, from_named_clauses):

        if input_query is None:
            return

        sparql_query = copy.deepcopy(input_query)

        enriched_query = EnrichedQueryWrapper()

        self.manage_from_and_from_named_clause(enriched_query, from_clauses, from_named_clauses)

        if not sparql_query.from_clauses and from_clauses:
            for single_from in from_clauses:
                sparql_query.from_clauses.append('<'+single_from+'>')

        if not sparql_query.from_named_clauses and from_named_clauses:
            for single_from in from_named_clauses:
                sparql_query.from_named_clauses.append('<'+single_from+'>')

        enriched_query.set_prefixes(prefixes)
        enriched_query.set_sparql_query(sparql_query)

        sparql_enriched_query = copy.deepcopy(sparql_query)

        if not sparql_enriched_query.prefixes:
            sparql_enriched_query.prefixes = prefixes

        add_graph = True

        enriched_query.var_structure = VarStructure()
        enriched_query.var_structure.var_binds = self.manage_binds(sparql_query.get_all_binds())
        enriched_query.var_structure.query_var_names = sparql_query.get_all_variables()
        enriched_query.var_structure.projection_variables = sparql_query.projection_variables

        self.manage_group_graph_pattern(sparql_enriched_query.group_graph_pattern,
                                        enriched_query,
                                        add_graph)

        sparql_enriched_query.modifiers = {
                                            'order': '',
                                            'group': '',
                                            'projection': [],
                                            'distinct_reduced': 'DISTINCT',
                                            'offset': '',
                                            'limit': ''
                                          }
        for graph_var_name in enriched_query.get_projection_graph_var_names():
                sparql_enriched_query.modifiers['projection'].append(graph_var_name)





        enriched_query.set_enriched_query(sparql_enriched_query)

        return enriched_query

    def manage_from_and_from_named_clause(self, enriched_query, from_clauses, from_named_clauses):

        for single_from in from_clauses:
            single_from = single_from.replace('<', '')
            single_from = single_from.replace('>', '')
            enriched_query.get_from_clauses().add(single_from)

        for single_named_from in from_named_clauses:
            single_named_from = single_named_from.replace('<', '')
            single_named_from = single_named_from.replace('>', '')
            enriched_query.get_from_named_clauses().add(single_named_from)


    def manage_group_graph_pattern(self,
                                   group_graph_pattern,
                                   enriched_query,
                                   add_graph=False):

        for graph in group_graph_pattern.graphs:
            if '?' in graph.var_or_term:
                enriched_query.get_var_graph_names().append(graph.var_or_term)
                enriched_query.get_projection_graph_var_names().append(graph.var_or_term)
            else:
                enriched_query.get_stat_graph_iris().add(graph.var_or_term[1:len(graph.var_or_term)-1])

            enriched_query.graphs_vars_relation[graph.var_or_term] = str(graph)

        #*********************************************************************
        #**************************** SUB-SELECT *****************************
        #*********************************************************************
        if group_graph_pattern.get_sub_queries():
            for sub_query in group_graph_pattern.get_sub_queries():
                enriched_query.get_subquery_enriched_queries().append(self.elab_query(sub_query,
                                                                                      enriched_query.get_prefixes(),
                                                                                      enriched_query.get_from_clauses(),
                                                                                      enriched_query.get_from_named_clauses()))

        #*********************************************************************
        #**************************** TRIPLETTE ******************************
        #*********************************************************************
        self.manage_triples(group_graph_pattern,
                            enriched_query,
                            add_graph)


        #*********************************************************************
        #****************************** UNION ********************************
        #*********************************************************************
        self.manage_unions(group_graph_pattern.unions,
                                    enriched_query,
                                    add_graph)

        #*********************************************************************
        #***************************** OPTIONAL ******************************
        #*********************************************************************
        self.manage_optionals(group_graph_pattern.optionals,
                                       enriched_query,
                                       add_graph)

    def print_original_query_with_extras(self, sparql_query, prefixes, from_clauses, from_named_clauses):
        query_plus_extras = copy.deepcopy(sparql_query)
        query_plus_extras.from_clauses = from_clauses
        query_plus_extras.from_named_clauses = from_named_clauses
        query_plus_extras.prefixes = prefixes
        return str(query_plus_extras)


class VarStructure:

    def __init__(self):
        self.var_binds = []
        self.query_var_names = []
        self.projection_variables = []