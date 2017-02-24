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

from HtmlUtilClass import HtmlUtilClass

class LicenseStructure:

    def __init__(self, license_permissions, categories):

        self.license_permissions = license_permissions
        self.categories = categories

        self.LMid = ''
        self.lic_desc = ''
        self.lic_link = ''

        self.perm = {}
        for permission in sorted(self.license_permissions.keys()):
            self.perm[permission] = 0

        self.cat = {}
        for category in sorted(self.categories):
            self.cat[category] = 1

        self.valid = True

    def pretty_print_license_category_table(self, tab_id='', license_name='', print_categories=False):

        if print_categories:
            return HtmlUtilClass.pretty_print_single_license_category_table(tab_id, license_name, self.cat)
        else:
            return HtmlUtilClass.pretty_print_single_license_category_table(tab_id, license_name, self.perm)


    def is_license_usable_by_some_category(self):

        for category in sorted(self.categories):
            if self.cat[category] > 0:
                return True

        return False




    #*********************************************************************************************************
    #************************************** RETRIEVE LICENSE   ***********************************************
    #*********************************************************************************************************
    @staticmethod
    def retrieve_license(cnx, LMid, license_permissions, categories, license_cache):

        license_structure = LicenseStructure(license_permissions, categories)

        if LMid is None:
            return license_structure.set_no_license()

        if not (LMid in license_cache.keys()):

            cursor2 = cnx.cursor()

            query2 = '''
                     SELECT L.LMid, L.description, L.link, GROUP_CONCAT(LPC.description SEPARATOR ', ')
                     FROM licenses_permcond LP, licenses L, lic_perm_cond LPC
                     WHERE LP.LMid = L.LMid and LP.LMid = %s and LPC.Pid = LP.Pid
                     GROUP BY L.LMid ORDER BY LP.Pid desc
                     '''
            found = cursor2.execute(query2, LMid)
            if found == 0:
                license_structure.set_no_license()
                license_cache[LMid] = license_structure
                return license_structure

            for (id, lic_desc, lic_link, perm_list_result) in cursor2:
                license_structure.lic_desc = lic_desc
                license_structure.lic_link = lic_link
                license_structure.LMid = LMid
                perm_list = [str(el).strip() for el in perm_list_result.split(',')]
                for pid in perm_list:
                    license_structure.perm[pid] = 1

            cursor2 = cnx.cursor()

            query2 = '''
                    SELECT L.Lmid, GROUP_CONCAT(C.name SEPARATOR ', ')
                    FROM licenses L, licenses_categories LC, lic_categories C
                    WHERE L.LMId = LC.LMId and LC.LMid = %s and C.CatId = LC.CatId
                    GROUP by L.LMid
                    ORDER by LC.CatId DESC
                    '''
            cursor2.execute(query2, LMid)
            for (id, cat_list_result) in cursor2:
                cat_list = [str(el).strip() for el in cat_list_result.split(',')]
                for category in sorted(categories):
                    if category not in cat_list:
                        license_structure.cat[category] = 0

            license_cache[LMid] = license_structure

        else:
            print('CACHING LICENSE')
            license_structure = license_cache[LMid]

        return license_structure



    def set_no_license(self):
        self.perm = {}
        for permission in sorted(self.license_permissions.keys()):
            self.perm[permission] = 0 if self.license_permissions[permission].is_duty() else 1

        self.cat = {}
        for category in sorted(self.categories):
            self.cat[category] = 1
        self.lic_desc = 'no license'
        self.lic_link = ''
        return self