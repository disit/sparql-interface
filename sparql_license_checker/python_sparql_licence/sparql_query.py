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
from expression import Expression
from exceptions import SparqlQueryUnmanagedElementException    
from group_graph_pattern import GroupGraphPattern
from var_or_term import VarOrTerm


class SparqlQuery:
    def __init__(self):
        self.prefixes = []
        self.define_clauses = []
        self.from_clauses = []
        self.from_named_clauses = []
        self.projection_variables = []
        self.modifiers = {
            'order': '', 
            'group': '', 
            'projection': ['*'], 
            'distinct_reduced': '', 
            'offset': '', 
            'limit': ''
        }
        self.group_graph_pattern = None

        self.all_variables = []
        self.all_sub_queries = []
        self.all_binds = []
        
    def init_from_parsed_tree(self, parsed_tree):
        #
        # entry point
        #
        # import pdb; pdb.set_trace()
        
        self.manage(parsed_tree)
        
    def manage(self, element):
        #
        # main loop
        #
        
        if isinstance(element, (list, tuple, sparql.algebra.ParseResults)) :
            for sub_el in element :
                self.manage(sub_el)
                        
        elif isinstance(element, sparql.parserutils.CompValue) :
            if 'PrefixDecl' in element.name :
                self.manage_prefix(element)
            elif 'Define' in element.name :
                self.manage_define(element)
            elif 'SelectQuery' in element.name \
                    or 'ConstructQuery' in element.name \
                    or 'AskQuery' in element.name \
                    or 'DescribeQuery' in element.name:
                self.manage_select_query(element)
            
            else:
                self.manage_unknown_element(element)
        else:
            self.manage_unknown_element(element)
            
            
                
    def manage_prefix(self, element):
        p = ''
        if 'prefix' in element :
            p += str(element['prefix'])
        self.prefixes.append(p + ': ' + '<' + str(element['iri']) + '>')
    
    def manage_define(self, element):
        define = ''

        var_or_term = VarOrTerm()
        var_or_term.init_from_element(element['param1'])
        define += str(var_or_term.get_var_or_term())
        var_or_term = VarOrTerm()
        var_or_term.init_from_element(element['param2'])
        define += ' ' + str(var_or_term.get_var_or_term())
        self.define_clauses.append(define)

    def manage_select_query(self, element):        
        if 'limitoffset' in element :
            self.manage_limit_offset(element['limitoffset'])
        if 'orderby' in element :
            self.manage_order_by(element['orderby'])
        if 'groupby' in element :
            self.manage_group_by(element['groupby'])
        if 'projection' in element :
            self.manage_projection(element['projection'])
        if 'modifier' in element :
            self.manage_modifiers(element['modifier'])
        if 'where' in element:
            self.manage_where(element['where'])
        if 'datasetClause' in element:
            self.manage_dataset_clauses(element['datasetClause'])
        
    def manage_limit_offset(self, element):
        if 'limit' in element:
            self.modifiers['limit'] = str(element['limit'])
        if 'offset' in element:
            self.modifiers['offset'] = str(element['offset'])
    
    def manage_order_by(self, element):
        if 'condition' in element:
            for cond in element['condition'] :
                order_str = ''
                if 'order' in cond :
                    order_str += str(cond['order'])
                expr = self.get_expression(cond['expr'])
                self.modifiers['order'] += order_str + ' ' + expr.get_expression_str() + ' '

    def manage_group_by(self, element):
        if 'condition' in element:
            for cond in element['condition'] :
                if isinstance(cond, sparql.parserutils.CompValue) : 
                    if 'GroupAs' in cond.name:
                        self.modifiers['group'] += '('
                        expr = self.get_expression(cond['expr'])
                        self.modifiers['group'] += expr.get_expression_str()
                        if 'var' in cond:
                            expr = self.get_expression(cond['var'])
                            self.modifiers['group'] += ' AS ' + expr.get_expression_str()
                        self.modifiers['group'] += ') '
                        
                else:
                    expr = self.get_expression(cond)
                    self.modifiers['group'] += expr.get_expression_str() + ' '

    def manage_projection(self, element):
        for e in element :
            if 'var' in e :
                var = self.get_var_or_term(e['var'])
                self.modifiers['projection'].append(var)
                self.projection_variables.append(var)
            elif 'expr' in e :
                self.manage_projection_expr(e)
                
        if len(self.modifiers['projection']) > 1 and '*' in self.modifiers['projection'] :
            self.modifiers['projection'].remove('*')
        
    def manage_projection_expr(self, element):
        expr = self.get_expression(element['expr'])
        self.projection_variables.extend(expr.variables)

        evar = self.get_var_or_term(element['evar'])
        self.projection_variables.extend(evar)

        self.modifiers['projection'].append( '(' + expr.get_expression_str() + ' AS ' + evar + ')')
    
    def manage_modifiers(self, element):   
        self.modifiers['distinct_reduced'] = str(element)
        
    def manage_where(self, element):
        self.group_graph_pattern = GroupGraphPattern()
        self.group_graph_pattern.init_from_element(element)
        self.all_variables.extend(self.group_graph_pattern.get_all_variables())
        self.all_binds.extend(self.group_graph_pattern.get_all_binds())
        self.all_sub_queries.extend(self.group_graph_pattern.get_all_sub_queries())

    def manage_dataset_clauses(self, element):
        for dataset_clause in element :
            if 'default' in dataset_clause :
                term = VarOrTerm()
                term.init_from_element(dataset_clause['default'])        
                self.from_clauses.append(term.get_var_or_term())
            elif 'named' in dataset_clause :
                term = VarOrTerm()
                term.init_from_element(dataset_clause['named'])        
                self.from_named_clauses.append(term.get_var_or_term())

    def get_var_or_term(self, element) :
        var_or_term = VarOrTerm()
        var_or_term.init_from_element(element)
        if var_or_term.get_variable() :
            self.all_variables.append(var_or_term.get_variable())
        return var_or_term.get_var_or_term()

    def get_expression(self, element) :
        try :
            expr = Expression()
            expr.init_from_element(element)
            self.all_variables.extend(expr.variables)
            self.all_binds.extend(expr.get_all_binds())
            self.all_sub_queries.extend(expr.get_all_sub_queries())
            return expr
        except :
            self.manage_unknown_element(element)

    def get_all_variables(self) :
        return set(self.all_variables)

    def get_all_sub_queries(self) :
        return set(self.all_sub_queries)
    
    def get_all_binds(self) :
        return set(self.all_binds)
    


    def manage_unknown_element(self, element):
        raise SparqlQueryUnmanagedElementException('UNMANAGED SPARQL QUERY element: ' + str(element))



    def __str__(self):
        res = ''

        for d in self.define_clauses: 
            res += '\nDEFINE ' + d 

        for p in self.prefixes:
            res += '\nPREFIX ' + p 

        res +='\nSELECT'

        if self.modifiers['distinct_reduced']:
            res += ' ' + self.modifiers['distinct_reduced'] + ' '

        for p in self.modifiers['projection']:
            res += ' ' + p

        for f in self.from_clauses:
            res += '\nFROM ' + str(f)

        for f in self.from_named_clauses:
            res += '\nFROM NAMED ' + str(f)

        res += '\nWHERE \n'
        res += str(self.group_graph_pattern)

        if self.modifiers['group']:
            res += '\nGROUP BY ' + self.modifiers['group']

        if self.modifiers['order']:
            res += '\nORDER BY ' + self.modifiers['order']

        if self.modifiers['limit']:
            res += '\nLIMIT ' + self.modifiers['limit']

        if self.modifiers['offset']:
            res += '\nOFFSET ' + self.modifiers['offset']

        return res

