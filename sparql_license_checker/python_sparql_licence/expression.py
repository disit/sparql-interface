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
from exceptions import SparqlQueryUnmanagedElementException    
from var_or_term import VarOrTerm
from group_graph_pattern import GroupGraphPattern

class Expression:
    def __init__(self):
        self.expression_str = ''
        self.variables = []
        self.all_binds = []
        self.all_sub_queries = []
    
    def init_from_element(self, expr):
        #print('----------')
        #print(expr)
        #print('----------')
        if expr is not None :
            self.manage_element(expr)
    
    def manage_element(self, element):
                        
        if isinstance(element, sparql.parserutils.CompValue) : 

            if 'ConditionalOrExpression' in element.name :
                self.manage_or_expr(element)

            elif 'ConditionalAndExpression' in element.name :
                self.manage_and_expr(element)

            elif 'RelationalExpression' in element.name :
                self.manage_relational_expr(element)

            elif 'AdditiveExpression' in element.name :
                self.manage_additive_expr(element)

            elif 'MultiplicativeExpression' in element.name :
                self.manage_multiplicative_expr(element)

            elif 'UnaryNot' in element.name :
                e = self.get_expression_from_element(element['expr'])
                self.expression_str += ' !' + e.get_expression_str()
            elif 'UnaryPlus' in element.name :
                e = self.get_expression_from_element(element['expr'])
                self.expression_str += ' +' + e.get_expression_str()
            elif 'UnaryMinus' in element.name :
                e = self.get_expression_from_element(element['expr'])
                self.expression_str += ' -' + e.get_expression_str()

            elif 'BrackettedExpression' in element.name :
                e = self.get_expression_from_element(element['expr'])
                self.expression_str += '(' + e.get_expression_str() + ')'

            elif 'Builtin' in element.name :
                self.manage_builtin(element)

            elif 'Aggregate' in element.name:
                self.manage_aggregate(element)

            elif 'Function' in element.name :
                self.manage_function(element)
        
            else :
                self.manage_var_or_term(element)
            
            return
            
        self.manage_var_or_term(element)

            
    def manage_or_expr(self, element):
        e = self.get_expression_from_element(element['expr'])
        self.expression_str += e.get_expression_str()
        if 'other' in element:
            for other in element['other']:
                o = self.get_expression_from_element(other)
                self.expression_str += ' || ' + o.get_expression_str()

    def manage_and_expr(self, element):
        e = self.get_expression_from_element(element['expr'])
        self.expression_str += e.get_expression_str()
        if 'other' in element:
            for other in element['other']:
                o = self.get_expression_from_element(other)
                self.expression_str += ' && ' + o.get_expression_str()
        
    def manage_relational_expr(self, element):
        e = self.get_expression_from_element(element['expr'])
        self.expression_str += e.get_expression_str()
        if 'other' in element :
            self.expression_str += ' ' + str(element['op']) + ' '

            if isinstance(element['other'], (list, tuple, sparql.algebra.ParseResults)):
                # ExpressionList        
                self.expression_str += '('
                for other in element['other']:
                    o = self.get_expression_from_element(other)
                    self.expression_str += o.get_expression_str() + ', '
                    
                self.expression_str = self.expression_str[:-2]   
                self.expression_str += ')'
        
            else:
                o = self.get_expression_from_element(element['other'])
                self.expression_str += o.get_expression_str()


    def manage_additive_expr(self, element):
        e = self.get_expression_from_element(element['expr'])
        self.expression_str += e.get_expression_str()
        if 'other' in element :
            for other, op in zip(element['other'], element['op']):
                self.expression_str += ' ' + str(op) + ' '
                o = self.get_expression_from_element(other)
                self.expression_str += o.get_expression_str()
        
    def manage_multiplicative_expr(self, element):
        e = self.get_expression_from_element(element['expr'])
        self.expression_str += e.get_expression_str()
        if 'other' in element :
            for other, op in zip(element['other'], element['op']):
                self.expression_str += ' ' + str(op) + ' '
                o = self.get_expression_from_element(other)
                self.expression_str += o.get_expression_str()


    def manage_builtin(self, element):
        if 'Aggregate' in element.name:
            self.manage_aggregate(element)
        elif 'REGEX' in element.name:
            self.manage_regex(element)
        elif 'NOTEXISTS' in element.name:
            self.manage_not_exists(element)
        elif 'EXISTS' in element.name:
            self.manage_exists(element)
        elif 'REPLACE' in element.name:
            self.manage_replace(element)
        elif 'SUBSTR' in element.name:
            self.manage_substr(element)

        elif 'COALESCE' in element.name or 'CONCAT' in element.name:
            self.expression_str += ' ' + element.name.split('_', 1)[1]        
            # ExpressionList        
            self.expression_str += '('
            for other in element['arg']:
                o = self.get_expression_from_element(other)
                self.expression_str += o.get_expression_str() + ', '
                
            self.expression_str = self.expression_str[:-2]   
            self.expression_str += ')'
        
        elif 'BNODE' in element.name:
            self.expression_str += ' ' + element.name.split('_', 1)[1]        
            self.expression_str += '('
            if 'arg' in element:
                e = self.get_expression_from_element(element['arg'])
                self.expression_str += e.get_expression_str()
            self.expression_str += ')'
        
        elif 'BOUND' in element.name:
            self.expression_str += ' ' + element.name.split('_', 1)[1]        
            self.expression_str += '('
            self.manage_var_or_term(element['var'])
            self.expression_str += ')'

        elif 'NOW' in element.name or 'UUID' in element.name or 'STRUUID' in element.name or 'RAND' in element.name:
            self.expression_str += ' ' + element.name.split('_', 1)[1]        
            self.expression_str += '()'

        elif 'arg' in element:
            self.expression_str += ' ' + element.name.split('_', 1)[1]        
            e = self.get_expression_from_element(element['arg'])
            self.expression_str += '(' + e.get_expression_str() + ')'

        elif 'arg1' in element and 'arg2' in element and 'arg3' in element:
            self.expression_str += ' ' + element.name.split('_', 1)[1]        
            e = self.get_expression_from_element(element['arg1'])
            self.expression_str += '(' + e.get_expression_str() + ', '
            e = self.get_expression_from_element(element['arg2'])
            self.expression_str += e.get_expression_str() + ', '
            e = self.get_expression_from_element(element['arg3'])
            self.expression_str += e.get_expression_str() + ')'

        elif 'arg1' in element and 'arg2' in element:
            self.expression_str += ' ' + element.name.split('_', 1)[1]        
            e = self.get_expression_from_element(element['arg1'])
            self.expression_str += '(' + e.get_expression_str() + ', '
            e = self.get_expression_from_element(element['arg2'])
            self.expression_str += e.get_expression_str() + ')'

        else :
            self.manage_unknown_element(element)

    
    def manage_aggregate(self, element):
        if 'Sum' in element.name or 'Min' in element.name or 'Max' in element.name or \
            'Avg' in element.name or 'Sample' in element.name or 'Count' in element.name:

            self.expression_str += ' ' + element.name.split('_', 1)[1].upper()
            self.expression_str += '('
            if 'distinct' in element and element['distinct'] :
                self.expression_str += 'DISTINCT '
            e = self.get_expression_from_element(element['vars'])
            self.expression_str += e.get_expression_str() + ')'

        elif 'GroupConcat' in element.name:
            self.expression_str += ' GROUP_CONCAT'
            self.expression_str += '('
            if 'distinct' in element and element['distinct'] :
                self.expression_str += 'DISTINCT '
            e = self.get_expression_from_element(element['vars'])
            self.expression_str += e.get_expression_str()
            if 'separator' in element:
                self.expression_str += '; SEPARATOR = "' + str(element['separator']) + '"' 
            self.expression_str += ')'
            
        else :
            self.manage_unknown_element(element)

    def manage_regex(self, element):
        self.expression_str += ' REGEX'
        self.expression_str += '('

        e = self.get_expression_from_element(element['text'])
        self.expression_str += e.get_expression_str()

        e = self.get_expression_from_element(element['pattern'])
        self.expression_str += ', ' + e.get_expression_str()

        if 'flag' in element:
            e = self.get_expression_from_element(element['flag'])
            self.expression_str += ', ' + e.get_expression_str()

        self.expression_str += ')'


    def manage_exists(self, element):
        self.expression_str += ' EXISTS'
        self.manage_group_graph_pattern(element['graph'])

    def manage_not_exists(self, element):
        self.expression_str += ' NOT EXISTS'
        self.manage_group_graph_pattern(element['graph'])

    def manage_replace(self, element):
        self.expression_str += ' REPLACE'
        self.expression_str += '('

        e = self.get_expression_from_element(element['arg'])
        self.expression_str += e.get_expression_str()

        e = self.get_expression_from_element(element['pattern'])
        self.expression_str += ', ' + e.get_expression_str()

        e = self.get_expression_from_element(element['replacement'])
        self.expression_str += ', ' + e.get_expression_str()

        if 'flag' in element:
            e = self.get_expression_from_element(element['flag'])
            self.expression_str += ', ' + e.get_expression_str()

        self.expression_str += ')'

    def manage_substr(self, element):
        self.expression_str += ' SUBSTR'
        self.expression_str += '('

        e = self.get_expression_from_element(element['arg'])
        self.expression_str += e.get_expression_str()

        e = self.get_expression_from_element(element['start'])
        self.expression_str += ', ' + e.get_expression_str()

        if 'length' in element:
            e = self.get_expression_from_element(element['length'])
            self.expression_str += ', ' + e.get_expression_str()

        self.expression_str += ')'

    def manage_function(self, element):

        self.manage_var_or_term(element['iri'])

        self.expression_str += '('
        if 'distinct' in element and element['distinct'] :
            self.expression_str += 'DISTINCT '

        for expr in element['expr']:
            e = self.get_expression_from_element(expr)
            self.expression_str += e.get_expression_str() + ', '
            
        self.expression_str = self.expression_str[:-2]   
        self.expression_str += ')'


    def get_expression_from_element(self, element):
        expr = Expression()
        expr.init_from_element(element)
        self.variables.extend(expr.variables)
        self.all_binds.extend(expr.get_all_binds())
        self.all_sub_queries.extend(expr.get_all_sub_queries())
        return expr


    def get_variables(self):
        return self.variables
    
    def get_all_binds(self):
        return self.all_binds

    def get_all_sub_queries(self):
        return self.all_sub_queries

    def manage_group_graph_pattern(self, element):
        group_graph_pattern = GroupGraphPattern()
        group_graph_pattern.init_from_element(element)

        self.expression_str += str(group_graph_pattern)        

        self.variables.extend(group_graph_pattern.get_all_variables())
        self.all_binds.extend(group_graph_pattern.get_all_binds())
        self.all_sub_queries.extend(group_graph_pattern.get_all_sub_queries())

    def manage_var_or_term(self, element):
        var_or_term = VarOrTerm()
        var_or_term.init_from_element(element)
        if var_or_term.get_variable() :
            self.variables.append(var_or_term.get_variable())
        self.expression_str += var_or_term.get_var_or_term()
        
    def manage_unknown_element(self, element):
        raise SparqlQueryUnmanagedElementException('UNMANAGED SPARQL QUERY element: ' + str(element))
        
    def get_expression_str(self):
        return self.expression_str
