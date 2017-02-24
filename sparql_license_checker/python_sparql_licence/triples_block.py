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
from path import Path
import expression


class TriplesBlock:
    def __init__(self):
        self.triples = [] #array of Triplet objects
        self.unions = [] #array of Union objects
        self.optionals = [] #array of Optional objects

        self.all_variables = []
    
    def init_from_triples_block(self, triples_block):
        self.manage_triples(triples_block['triples'])

    
    def manage_triples(self, triples):
        for triples_same_subject in triples :
            while triples_same_subject :
                tmp_subject = self.get_var_or_term(triples_same_subject.pop(0))
                tmp_predicate = triples_same_subject.pop(0)
                tmp_object = self.get_var_or_term(triples_same_subject.pop(0))
                tmp_inference = ''

                if len(triples_same_subject) > 0 \
                    and isinstance(triples_same_subject[0], sparql.parserutils.CompValue) and 'OptionInference' in triples_same_subject[0].name :
                    tmp_inference = str(triples_same_subject.pop(0)['param'])
                
                
                path = Path()
                path.init_from_path(tmp_subject, tmp_predicate, tmp_object, tmp_inference)
                self.triples.extend(path.get_triples())
                self.unions.extend(path.get_unions())
                self.optionals.extend(path.get_optionals())
                self.all_variables.extend(path.get_all_variables())


    def get_var_or_term(self, element) :
        var_or_term = VarOrTerm()
        var_or_term.init_from_element(element)
        if var_or_term.get_variable() :
            self.all_variables.append(var_or_term.get_variable())
        return var_or_term.get_var_or_term()


    def manage_unknown_element(self, element):
        raise SparqlQueryUnmanagedElementException('UNMANAGED SPARQL QUERY element: ' + str(element))
        

    def get_triples(self) :
        return self.triples

    def get_unions(self) :
        return self.unions

    def get_optionals(self) :
        return self.optionals

    def get_all_variables(self) :
        return self.all_variables

    def __str__(self):
        res = '\n# TRIPLES_BLOCK:'
        return res
