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

class Union:
    def __init__(self):
        self.union_branches = [] #array of GroupGraphPattern objects

    def get_all_variables(self) :
        all_variables = []
        for b in self.union_branches :
            all_variables.extend(b.get_all_variables())
        return all_variables

    def get_all_binds(self) :
        all_binds = []
        for b in self.union_branches :
            all_binds.extend(b.get_all_binds())
        return all_binds

    def get_all_sub_queries(self) :
        all_sub_queries = []
        for b in self.union_branches :
            all_sub_queries.extend(b.get_all_sub_queries())
        return all_sub_queries

    def __str__(self):
        res = ''
        for ub in self.union_branches:
            if ub != self.union_branches[0]:
                res += ' UNION '
            res += str(ub)            
        return res
