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

import rdflib
from rdflib.plugins import sparql
from triplet import Triplet
from var_or_term import VarOrTerm
from union import Union
from optional import Optional
from exceptions import SparqlQueryUnmanagedElementException
import group_graph_pattern

class Path:
    def __init__(self):
        self.triples = [] #array of Triplet objects
        self.unions = [] #array of Union objects
        self.optionals = [] #array of Optional objects
        self.subject = ''
        self.object = ''
        self.inference = ''

        self.all_variables = []
    
    def init_from_path(self, subject, path, object, inference):

        self.subject = subject
        self.object = object
        self.inference = inference

        if isinstance(path, sparql.parserutils.CompValue) and 'PathAlternative' in path.name :
            self.manage_path_alternative(path)
        elif isinstance(path, sparql.parserutils.CompValue) and 'PathSequence' in path.name :
            self.manage_path_sequence(path)
        elif isinstance(path, sparql.parserutils.CompValue) and 'PathEltOrInverse' in path.name :
            self.manage_path_elt_or_inverse(path)
        elif isinstance(path, sparql.parserutils.CompValue) and 'PathElt' in path.name :
            self.manage_path_elt(path)
        else :
            triplet = Triplet()
            triplet.subject = subject
            triplet.predicate = self.get_var_or_term(path)
            triplet.object = object
            triplet.inference = inference
            self.triples.append(triplet)



    def manage_path_alternative(self, path_alternative) :
        if len(path_alternative['part']) > 1 :
            union = Union()
            for path_sequence in path_alternative['part'] :

                path = Path()
                path.init_from_path(self.subject, path_sequence, self.object, self.inference)

                union_branch = group_graph_pattern.GroupGraphPattern()
                union_branch.triples.extend(path.get_triples())
                union_branch.unions.extend(path.get_unions())
                union_branch.optionals.extend(path.get_optionals())
                union_branch.all_variables.extend(path.get_all_variables())
                
                union.union_branches.append(union_branch)
            self.unions.append(union)

        else :
            path = Path()
            path.init_from_path(self.subject, path_alternative['part'][0], self.object, self.inference)
            self.triples.extend(path.get_triples())
            self.unions.extend(path.get_unions())
            self.optionals.extend(path.get_optionals())
            self.all_variables.extend(path.get_all_variables())


    def manage_path_sequence(self, path_sequence) :
        if len(path_sequence['part']) > 1 :
            previous_object = self.subject
            for path_elt_or_inverse in path_sequence['part'] :
                path = Path()
                current_subject = previous_object 
                
                if path_sequence['part'].index(path_elt_or_inverse) == len(path_sequence['part']) - 1 :
                    new_intermediate_object = self.object
                else : 
                    new_intermediate_object = self.get_unique_bnode_name()

                path.init_from_path(current_subject, path_elt_or_inverse, new_intermediate_object, self.inference)

                self.triples.extend(path.get_triples())
                self.unions.extend(path.get_unions())
                self.optionals.extend(path.get_optionals())
                self.all_variables.extend(path.get_all_variables())

                previous_object = new_intermediate_object
                
        else :
            path = Path()
            path.init_from_path(self.subject, path_sequence['part'][0], self.object, self.inference)
            self.triples.extend(path.get_triples())
            self.unions.extend(path.get_unions())
            self.optionals.extend(path.get_optionals())
            self.all_variables.extend(path.get_all_variables())


    def manage_path_elt_or_inverse(self, path_elt_or_inverse) :
        path = Path()
        path.init_from_path(self.object, path_elt_or_inverse['part'], self.subject, self.inference)
        self.triples.extend(path.get_triples())
        self.unions.extend(path.get_unions())
        self.optionals.extend(path.get_optionals())
        self.all_variables.extend(path.get_all_variables())

    def manage_path_elt(self, path_elt) :

        if 'mod' in path_elt :
            path_mod = path_elt['mod']

            if path_mod == '*' :
                self.manage_unknown_element(' property path: * (zero or more)')
            elif path_mod == '+' :
                self.manage_unknown_element(' property path: + (one or more)')
            elif path_mod == '?' :
                optional = Optional()

                optional.group_graph_pattern = group_graph_pattern.GroupGraphPattern()
                path = Path()
                path.init_from_path(self.subject, path_elt['part'], self.object, self.inference)
                optional.group_graph_pattern.triples.extend(path.get_triples())
                optional.group_graph_pattern.unions.extend(path.get_unions())
                optional.group_graph_pattern.optionals.extend(path.get_optionals())
                optional.group_graph_pattern.all_variables.extend(path.get_all_variables())

                self.optionals.append(optional)
        else :
            path = Path()
            path.init_from_path(self.subject, path_elt['part'], self.object, self.inference)
            self.triples.extend(path.get_triples())
            self.unions.extend(path.get_unions())
            self.optionals.extend(path.get_optionals())
            self.all_variables.extend(path.get_all_variables())
                


    def get_unique_bnode_name(self) :
        n = rdflib.BNode()
        var = str(n.n3())
        var = var.replace('_:', '?')
        self.all_variables.append(var)
        return var

    def get_var_or_term(self, element) :
        var_or_term = VarOrTerm()
        var_or_term.init_from_element(element)
        if var_or_term.get_variable() :
            self.all_variables.append(var_or_term.get_variable())
        return var_or_term.get_var_or_term()

    def get_triples(self):
        return self.triples

    def get_unions(self):
        return self.unions

    def get_optionals(self):
        return self.optionals

    def get_all_variables(self):
        return self.all_variables
    
    def manage_unknown_element(self, element):
        raise SparqlQueryUnmanagedElementException('UNMANAGED SPARQL QUERY element: ' + str(element))
