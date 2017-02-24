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
import rdflib
from rdflib.plugins import sparql
from triples_block import TriplesBlock
from exceptions import SparqlQueryUnmanagedElementException    
from var_or_term import VarOrTerm
from union import Union
from optional import Optional
from graph_clause import GraphClause
from minus_clause import MinusClause
from values_clause import ValuesClause
from service_clause import ServiceClause
import sparql_query
import expression

class GroupGraphPattern:
    def __init__(self):
        self.triples = [] #array of Triplet objects
        self.sub_queries = [] #array of SparqlQuery objects
        self.unions = [] #array of Union objects
        self.optionals = [] #array of Optional objects
        self.graphs = [] #array of GraphClause objects
        self.binds = []
        self.filters = []

        self.minuses = [] 
        self.services = []
        self.values = []
        
        self.all_variables = []
        self.all_binds = []
        self.all_sub_queries = []
    
    def init_from_element(self, element):
        self.manage_element(element)
    
    def manage_element(self, element):
        #
        # main loop
        #
        
        if isinstance(element, (list, tuple, sparql.algebra.ParseResults)) :
            for sub_el in element :
                self.manage_element(sub_el)
                        
        elif isinstance(element, sparql.parserutils.CompValue) :
            if 'SubSelect' in element.name :
                self.manage_sub_select(element)
            elif 'GroupGraphPatternSub' in element.name :
                for part in element['part'] :
                    self.manage_element(part)
            elif 'TriplesBlock' in element.name :
                self.manage_triples_block(element)
            elif 'GroupOrUnionGraphPattern' in element.name :
                self.manage_group_or_union(element)
            elif 'OptionalGraphPattern' in element.name :
                self.manage_optional(element)
            elif 'GraphGraphPattern' in element.name :
                self.manage_graph_clause(element)
            elif 'Filter' in element.name :
                self.manage_filter(element)
            elif 'Bind' in element.name :
                self.manage_bind(element)

            elif 'MinusGraphPattern' in element.name :
                self.manage_minus(element)
            elif 'ServiceGraphPattern' in element.name :
                self.manage_service(element)
            elif 'InlineData' in element.name :
                self.manage_inline_data(element)
            
            else:
                self.manage_unknown_element(element)
        else:
            self.manage_unknown_element(element)


    def manage_sub_select(self, element):
        sub_select = sparql_query.SparqlQuery()
        element.name='SelectQuery'
        sub_select.init_from_parsed_tree(element)
        self.sub_queries.append(sub_select)
        self.all_sub_queries.append(sub_select)
        self.all_variables.extend(sub_select.get_all_variables())
        self.all_binds.extend(sub_select.get_all_binds())
        self.all_sub_queries.append(sub_select)

    def manage_group_or_union(self, element):
        if len(element['graph']) > 1 :
            self.manage_union(element)
        else :
            self.manage_element(element['graph'])

    def manage_union(self, element):
        union = Union()
        for graph in element['graph'] :
            union_branch = GroupGraphPattern()
            union_branch.init_from_element(graph)
            union.union_branches.append(union_branch)
        self.unions.append(union)
        self.all_variables.extend(union.get_all_variables())
        self.all_binds.extend(union.get_all_binds())
        self.all_sub_queries.extend(union.get_all_sub_queries())
         

    def manage_optional(self, element):
        optional = Optional()
        graph = element['graph']
        optional.group_graph_pattern = GroupGraphPattern()
        optional.group_graph_pattern.init_from_element(graph)
        self.optionals.append(optional)
        self.all_variables.extend(optional.get_all_variables())
        self.all_binds.extend(optional.get_all_binds())
        self.all_sub_queries.extend(optional.get_all_sub_queries())

    def manage_graph_clause(self, element):  
        graph_clause = GraphClause()
        graph_clause.var_or_term = self.get_var_or_term(element['term'])
        graph_clause.group_graph_pattern = GroupGraphPattern()
        graph_clause.group_graph_pattern.init_from_element(element['graph'])
        self.graphs.append(graph_clause)
        self.all_variables.extend(graph_clause.get_all_variables())
        self.all_binds.extend(graph_clause.get_all_binds())
        self.all_sub_queries.extend(graph_clause.get_all_sub_queries())

    def manage_filter(self, element):
        expr = self.get_expression(element['expr'])
        self.filters.append(expr.get_expression_str())        

    def manage_bind(self, element):
        expr = self.get_expression(element['expr'])
        var = self.get_var_or_term(element['var'])
        bind = '(' + expr.get_expression_str() + ' AS ' + var + ')'
        self.binds.append(bind)
        self.all_binds.append(bind)

    def manage_minus(self, element):
        # self.manage_unknown_element(element)
        minus_clause = MinusClause()
        minus_clause.group_graph_pattern = GroupGraphPattern()
        minus_clause.group_graph_pattern.init_from_element(element['graph'])
        self.minuses.append(minus_clause)
        self.all_variables.extend(minus_clause.get_all_variables())
        self.all_binds.extend(minus_clause.get_all_binds())
        self.all_sub_queries.extend(minus_clause.get_all_sub_queries())


    def manage_service(self, element):
        # self.manage_unknown_element(element)
        
        service_clause = ServiceClause()
        try :
            service_clause.silent = element['silent']
        except :
            pass

        service_clause.var_or_term = self.get_var_or_term(element['term'])
        service_clause.group_graph_pattern = GroupGraphPattern()
        service_clause.group_graph_pattern.init_from_element(element['graph'])
        self.services.append(service_clause)
        self.all_variables.extend(service_clause.get_all_variables())
        self.all_binds.extend(service_clause.get_all_binds())
        self.all_sub_queries.extend(service_clause.get_all_sub_queries())

    def manage_inline_data(self, element):
        # self.manage_unknown_element(element)
        values_clause = ValuesClause()
        for var in element['var']:
            var_or_term = self.get_var_or_term(var)
            values_clause.variables.append(var_or_term)

        for value_tuple in element['value']:
            tmp_value_tuple = []
            if isinstance(value_tuple, (list, tuple, sparql.algebra.ParseResults)) :
                for val in value_tuple :
                    var_or_term = self.get_var_or_term(val)
                    tmp_value_tuple.append(var_or_term)
            else :
                var_or_term = self.get_var_or_term(value_tuple)
                tmp_value_tuple.append(var_or_term)

            values_clause.value_tuples.append(tmp_value_tuple)
    
        self.values.append(values_clause)


    def manage_triples_block(self, element):
        triples_block = TriplesBlock()
        triples_block.init_from_triples_block(element)
        self.triples.extend(triples_block.get_triples())
        self.all_variables.extend(triples_block.get_all_variables())

        self.unions.extend(triples_block.get_unions())
        self.optionals.extend(triples_block.get_optionals())

    def get_var_or_term(self, element) :
        var_or_term = VarOrTerm()
        var_or_term.init_from_element(element)
        if var_or_term.get_variable() :
            self.all_variables.append(var_or_term.get_variable())
        return var_or_term.get_var_or_term()

    def get_expression(self, element) :
        try :
            expr = expression.Expression()
            expr.init_from_element(element)
            self.all_variables.extend(expr.variables)
            self.all_binds.extend(expr.get_all_binds())
            self.all_sub_queries.extend(expr.get_all_sub_queries())
            return expr
        except :
            self.manage_unknown_element(element)

    def manage_unknown_element(self, element):
        raise SparqlQueryUnmanagedElementException('UNMANAGED SPARQL QUERY element: ' + str(element))
        

    def get_sub_queries(self) :
        return self.sub_queries

    def get_all_variables(self) :
        return self.all_variables
    
    def get_all_binds(self) :
        return self.all_binds

    def get_all_sub_queries(self) :
        return self.all_sub_queries


    def __str__(self):
        res = '{'

        for s in self.sub_queries:
            res += '\n{' + str(s) + '}'

        for t in self.triples:
            res += '\n' + str(t)

        for g in self.graphs:
            res += '\n' + str(g)

        for u in self.unions:
            res += '\n' + str(u)

        for o in self.optionals:
            res += '\n' + str(o)

        for m in self.minuses:
            res += '\n' + str(m) 
        for s in self.services:
            res += '\n' + str(s) 
        for v in self.values:
            res += '\n' + str(v) 

        for b in self.binds:
            res += '\nBIND ' + b
            #res += '\nBIND (' + b + ')'

        for f in self.filters:
            res += '\nFILTER ' + f 
            #res += '\nFILTER (' + f +')'

        res += '\n}'
        return res    

