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

class ValuesClause:
    def __init__(self):
        self.variables = []
        self.value_tuples = []

    def __str__(self):
        res = 'VALUES: ('
        for var in self.variables:
            res += ' ' + var
        res += ') {'
        for t in self.value_tuples:
            res += '\n('
            for val in t:
                res += ' ' + val 
            res += ')'
        res += '\n}'
        return res
