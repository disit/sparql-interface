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

class EnrichedQueryWrapper:

    def __init__(self):
        self.enriched_query = None
        self.var_structure = None
        self.var_graph_names = []
        self.stat_graph_iris = set()
        self.has_free_triples = False
        self.subquery_enriched_queries_wrapper = []
        self.from_clauses = set()
        self.from_named_clauses = set()
        self.prefixes = ''
        self.sparql_query = None
        self.projection_graph_var_names = []
        self.graphs_vars_relation = {}
        self.query_result = None

    def get_var_graph_names(self):
        return self.var_graph_names

    def get_stat_graph_iris(self):
        return self.stat_graph_iris

    def get_has_free_triples(self):
        return self.has_free_triples

    def get_enriched_query(self):
        return self.enriched_query

    def get_subquery_enriched_queries(self):
        return self.subquery_enriched_queries_wrapper

    def set_subquery_enriched_queries(self, sub_queries):
        self.subquery_enriched_queries_wrapper = sub_queries

    def get_var_structure(self):
        return self.var_structure

    def get_from_clauses(self):
        return self.from_clauses

    def get_from_named_clauses(self):
        return self.from_named_clauses

    def set_from_named_clauses(self, from_named_clauses):
        self.from_named_clauses = from_named_clauses

    def set_from_clauses(self, from_clauses):
        self.from_clauses = from_clauses

    def set_sparql_query(self, sparql_query):
        self.sparql_query = sparql_query

    def get_sparql_query(self):
        return self.sparql_query

    def get_prefixes(self):
        return self.prefixes

    def set_prefixes(self, prefixes):
        self.prefixes = prefixes

    def get_projection_graph_var_names(self):
        return self.projection_graph_var_names

    def set_projection_graph_var_names(self, projection_graph_var_names):
        self.projection_graph_var_names = projection_graph_var_names

    def get_graphs_vars_relation(self):
        return self.graphs_vars_relation

    def set_graphs_vars_relation(self, graphs_vars_relation):
        self.graphs_vars_relation = graphs_vars_relation

    def set_enriched_query(self, enriched_query):
        self.enriched_query = enriched_query

    def get_query_result(self):
        return self.query_result

    def set_query_result(self,query_result):
        self.query_result = query_result