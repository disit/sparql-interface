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

from flask import Flask, request, jsonify, json, make_response
from flask.ext.cors import cross_origin
import sys
import logging
from logging.handlers import RotatingFileHandler
from graphs_queries_generator import GraphsQueriesGenerator
from graphs_license_response_manager import GraphsLicenseResponseManager
from sparql_query import SparqlQueryUnmanagedElementException 
import configparser

app = Flask(__name__)

@app.route("/")
@cross_origin()
def check_license():
    try:
        source_query = request.args.get('query', '')
        user_category = request.args.get('user_category', '')

        graphs_queries_generator = GraphsQueriesGenerator()
        graphs_query = graphs_queries_generator.get_enriched_query_from_query(source_query)
        graphs_license_response_manager.set_query(graphs_query)
        graphs_license_response_manager.send_queries_to_endpoint(user_category)
        tmp_str = graphs_license_response_manager.get_license_response()
        
        return tmp_str
    
    except SparqlQueryUnmanagedElementException as ex:
        app.logger.error(str(ex))
        response = jsonify(message=str(ex))
        response.status_code = 500
        return response
    except Exception as ex:
        app.logger.error(str(ex))
        response = jsonify(message=str(ex))
        response.status_code = 500
        return response

@app.route("/user-categories")
@cross_origin()
def get_user_categories():
    try:
        category_selection_list = ['']
        category_selection_list.extend(graphs_license_response_manager.categories)
        response = make_response(json.dumps(category_selection_list))
        return response
    
    except Exception as ex:
        app.logger.error(str(ex))
        response = jsonify(message=str(ex))
        response.status_code = 500
        return response

@app.errorhandler(Exception)
def unhandled_exception(ex):
    app.logger.error('Unexpected Exception: %s', (ex))
    response = jsonify(message=str(ex))
    response.status_code = 500
    return response

if __name__ == "__main__":
    handler = RotatingFileHandler('license_checker.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    graphs_license_response_manager = GraphsLicenseResponseManager()
    
    config = configparser.ConfigParser()
    config.read("config.cfg")
    host = config.get('PythonServer', 'host')
    port = config.get('PythonServer', 'port')
    app.run(host=host, port=port)
