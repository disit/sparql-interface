/*  SPARQL License Checker
  Copyright (C) 2017 DISIT Lab http://www.disit.org - University of Florence

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as
  published by the Free Software Foundation, either version 3 of the
  License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.*/

function LicenseChecker(flint, editorId, config) {
    
    this.flint = flint;
    this.editorId = editorId;
    this.config = config;

    this.licenseCheckButton = null;
    this.categorySelectionField = null;

    this.getLicenseCheckButton = function(editor) {
        this.licenseCheckButton = new function LicenseCheckButton() {
            this.disable = function() {
                $('.license-check-button').css('visibility', 'hidden');
            };

            this.enable = function() {
                $('.license-check-button').css('visibility', 'visible');
            };

            this.display = function(container) {
                try {
                    $('#' + container)
                    .append(
                        "<input class='license-check-button' id='license-check-submit' " 
                        + "style='width: 110px'"
                        + "type='submit' value='License Check' title='License Check'/>"
                    );
                } catch (e) {
                    editor.getErrorBox().show(e);
                }
            };

            this.setSubmitAction = function(callback) {
                $('#license-check-submit').click(callback);
            };
        };
        this.licenseCheckButton.editor = editor;
        return this.licenseCheckButton;
    };
    
    this.getCategorySelectionField = function(editor) {
        this.categorySelectionField = new function CategorySelectionField() {
            this.display = function(container) {
                var me = this;
                $('#' + container).append(
                    "<div class='user-category-selection-field' title='Select the user category'>" 
                    + "<h2>Category</h2>"
                    + "<select id='user-category-select' name='user-category'></select></div>" 
                );
                $.ajax({
                    url : me.config.licenseCheckerConfig.pythonServer + 'user-categories',
                    type : 'get',
                    dataType : 'json',
                    error : function(XMLHttpRequest, textStatus, errorThrown) {
                        if (XMLHttpRequest.status == 0) {
                            me.editor.getErrorBox().show("Error while trying to retrieve information about user categories. You may be offline");
                        } else {
                            me.editor.getErrorBox().show("Dataset Request: HTTP Status: " + XMLHttpRequest.status + "; " + XMLHttpRequest.responseText);
                        }
                    },
                    success: function(data){
                        $.each(data, function(index, item) {
                            $('#user-category-select').append('<option value="' + item + '">' + item + '</option>');
                        });
                    }
                });
            };
        };
        this.categorySelectionField.editor = editor;
        this.categorySelectionField.config = config;
        return this.categorySelectionField;
    };

    this.setButtonAction = function(resultsArea, errorBox, config, cm, datasetItems, datasetMimeTypeItem) {
        var me = this;
        var licenseCheckAction = function() {
            try {
                if (!$.browser.msie) {
                    resultsArea.setResults("");
                    resultsArea.showLoading(true);
                }
                // Collect query parameters
                var paramsData = {};
                var paramsDataItem = config.defaultEndpointParameters.queryParameters.query;
                if (cm.getQueryType() == 'UPDATE') {
                    paramsDataItem = config.defaultEndpointParameters.queryParameters.update;
                }
                paramsData[paramsDataItem] = cm.getCodeMirror().getValue();
                paramsData['service-uri'] = datasetItems.getEndpoint();
                paramsData['user_category'] = $('#user-category-select').val();
                var mimeType = datasetMimeTypeItem.getMimeType();
                $.ajax({
                    url : config.licenseCheckerConfig.pythonServer,
                    type : 'get',
                    data : paramsData,
                    headers : {
                        "Accept" : mimeType
                    },
                    dataType : 'text',
                    error : function(XMLHttpRequest, textStatus, errorThrown) {
                        if (XMLHttpRequest.status == 0) {
                            errorBox.show("The request was not sent. You may be offline");
                        } else {
                            errorBox.show("Dataset Request: HTTP Status: " + XMLHttpRequest.status + "; " + XMLHttpRequest.responseText);
                        }
                        resultsArea.showLoading(false);
                    },
                    success : function(data) {
                        resultsArea.showLoading(false);
			            var aboutBox = new me.LicenseResultsArea(me.editorId);
				        aboutBox.show("License Check/Verification Results", data);
                    }
                });
            } catch (e) {
                errorBox.show("Cannot send dataset query: " + e);
            }
        };
        this.licenseCheckButton.setSubmitAction(licenseCheckAction)
    };

	this.LicenseResultsArea = function(editorId) {

        this.show = function(title, text) {
            
            $('<div/>', {
                id: 'license-results-area',
                css: {
                    position: 'absolute',
                    padding: '10px 10px 60px 10px',
                    left: '50%',
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '90%',
                    height: '80%',
                    background: '#f5f5f5',
                    border: '1px solid #bbb',
                    'border-radius': '3px',
                    'font-family': 'sans-serif',
                    'font-size': 'small',
                    'box-shadow': '3px 3px 15px #333, -3px 0px 15px #333',
                    color: '#333'
                }
            }).appendTo('#'+editorId);
            
            $('<h1/>', {
                id: 'license-results-area-title',
                text: title,
                css: {
                    float: 'left'
                }
            }).appendTo('#license-results-area');

            $('<button/>', {
                id: 'license-results-area-close-button',
                text: 'X',
                css: {
                    background: 'none',
                    color: '#444',
                    border: '1px solid #bbb',
                    'font-weight': 'bold',
                    'border-radius': '3px',
                    //margin: '2px'
                    float: 'right'
                }
            }).appendTo('#license-results-area')
            .hover(
                function(){
                    $(this).css("border","1px solid #4D90FE");
                }, 
                function(){
                    $(this).css("border","1px solid #bbb");
                })
            .click(function() {
                $('#license-results-area').remove();
            });

            $('<button/>', {
                id: 'license-results-area-close-button',
                text: 'PDF',
                css: {
                    background: 'none',
                    color: '#444',
                    border: '1px solid #bbb',
                    'font-weight': 'bold',
                    'border-radius': '3px',
                    //margin: '2px'
                    float: 'right'
                }
            }).appendTo('#license-results-area')
            .hover(
                function(){
                    $(this).css("border","1px solid #4D90FE");
                }, 
                function(){
                    $(this).css("border","1px solid #bbb");
                })
            .click(function() {

                var newWindow = window.open();
                newWindow.document.write($('#license-results-area-content').html());
                newWindow.document.close(); // necessary for IE >= 10
                newWindow.focus(); // necessary for IE >= 10
    
                newWindow.print();
                newWindow.close();

            });

            $('<div/>', {
                id: 'license-results-area-content',
                html: text,
                css: {
                    position: 'relative',
                    'border-top': '2px solid #666',
                    top: '-15px',
                    overflow: 'auto',
                    height: '100%',
                    width: '100%'
                }
            }).appendTo('#license-results-area');

            $('#license-results-area div[name="final_license"] h2').before('<br><hr>');

            $('.expand').click(function(){
                var elementToCollapse = this.attributes['data-target'].nodeValue;
                $(elementToCollapse).toggle();
            });

            $('ul.tabs li').click(function(){
                var tab_id = $(this).attr('data-tab');

                $('ul.tabs li').removeClass('current');
                $('.tab-content').removeClass('current');

                $(this).addClass('current');
                $("#"+tab_id).addClass('current');
            })
        };
	}
}
