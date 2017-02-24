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

class GraphClause:
    def __init__(self):
        self.group_graph_pattern = None #element of GroupGraphPattern objects
        self.var_or_term = ''

    def get_all_variables(self):
        return self.group_graph_pattern.get_all_variables()

    def get_all_binds(self):
        return self.group_graph_pattern.get_all_binds()

    def get_all_sub_queries(self):
        return self.group_graph_pattern.get_all_sub_queries()

    def __str__(self):
        return 'GRAPH ' + str(self.var_or_term) + str(self.group_graph_pattern)
