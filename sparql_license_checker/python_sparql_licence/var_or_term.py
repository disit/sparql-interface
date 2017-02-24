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
import numbers
from exceptions import SparqlQueryUnmanagedElementException    

class VarOrTerm:
    def __init__(self):
        self.variable = None
        self.var_or_term = ''
    
    def init_from_element(self, element):
        self.var_or_term = self.__get_var_or_term(element)        

    def __get_var_or_term(self, element):

        if isinstance(element, rdflib.BNode):
            try:
                if '_:' in str(element):
                    return str(element)
            except:
                pass
            return element.n3()
        if isinstance(element, rdflib.term.Variable) :
            self.variable = '?' + str(element)
            return self.variable
        if isinstance(element, rdflib.term.Literal) :
            # TODO: dovrebbe andare bene anche element.n3()
            tmp = element.toPython()
            if isinstance(tmp, bool):
                return str(tmp).lower()
            if isinstance(tmp, numbers.Number):
                return str(tmp)
            return '"' + str(element) + '"'
        if 'string' in element :
            return '"' + str(element['string']) + '"'
        if isinstance(element, rdflib.term.URIRef) :
            return '<' + str(element) + '>'
        if isinstance(element, str) :
            return element

        try :
            res = element.n3()
            self.variable = res
            return res
        except :
            pass

        try :
            res = str(element['prefix']) + ':' + str(element['localname']) 
            return res
        except :
            pass
        
        try :
            res = ':' + str(element['localname']) 
            return res
        except :
            pass
        

        self.manage_unknown_element(element)

    def get_variable(self) :
        return self.variable

    def get_var_or_term(self) :
        return self.var_or_term

    def manage_unknown_element(self, element):
        raise SparqlQueryUnmanagedElementException('UNMANAGED SPARQL QUERY element: ' + str(element))
