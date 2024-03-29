var TableData = function() {
	//function to initiate DataTable
	//DataTable is a highly flexible tool, based upon the foundations of progressive enhancement,
	//which will add advanced interaction controls to any HTML table
	//For more information, please visit https://datatables.net/
	/*var runDataTable = function() {
		var oTable = $('#sample_1').dataTable({
			"aoColumnDefs" : [{
				"aTargets" : [0]
			}],
			"oLanguage" : {
				"sLengthMenu" : "Show _MENU_ Rows",
				"sSearch" : "",
				"oPaginate" : {
					"sPrevious" : "",
					"sNext" : ""
				}
			},
			"aaSorting" : [[1, 'asc']],
			"aLengthMenu" : [[5, 10, 15, 20, -1], [5, 10, 15, 20, "All"] // change per page values here
			],
			// set the initial value
			"iDisplayLength" : 10,
		});
		//$('#sample_1_wrapper .dataTables_filter input').addClass("form-control input-sm").attr("placeholder", "Search");
		// modify table search input
		//$('#sample_1_wrapper .dataTables_length select').addClass("m-wrap small");
		// modify table per page dropdown
		//$('#sample_1_wrapper .dataTables_length select').select2();
		// initialzie select2 dropdown
		//$('#sample_1_column_toggler input[type="checkbox"]').change(function() {
		//	 Get the DataTables object again - this is not a recreation, just a get of the object 
		//	var iCol = parseInt($(this).attr("data-column"));
		//	var bVis = oTable.fnSettings().aoColumns[iCol].bVisible;
		//	oTable.fnSetColumnVis(iCol, ( bVis ? false : true));
		//});
	};*/

	var runEditableTable = function() {

		var newRow = false;
		var actualEditingRow = null;

		function restoreRow(oTable, nRow) {
			var aData = oTable.fnGetData(nRow);
			var jqTds = $('>td', nRow);

			for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
				oTable.fnUpdate(aData[i], nRow, i, false);
			}

			oTable.fnDraw();
		}

		function editRow(oTable, nRow) {
			var aData = oTable.fnGetData(nRow);
			var jqTds = $('>td', nRow);
			var rowNum = oTable.fnSettings().fnRecordsTotal() - 1;
			
			

			jqTds[0].innerHTML = '<input type="hidden" id="locations-' + rowNum + '-stop_number" name="locations-' + rowNum + '-stop_number" class="form-control" value="' + (rowNum + 1) + '">' + (rowNum + 1);
			jqTds[1].innerHTML = '<select class="form-control location-type" id="locations-' + rowNum + '-stop_type" name="locations-' + rowNum + '-stop_type" data-rule-required="true"><option value=""></option><option value="Pickup">Pickup</option><option value="Drop Off">Drop Off</option></select>';
			jqTds[2].innerHTML = '<input type="text" id="locations-' + rowNum + '-address1" name="locations-' + rowNum + '-address1" class="form-control" value="' + aData[2] + '" data-rule-required="true">';
			jqTds[3].innerHTML = '<input type="text" id="locations-' + rowNum + '-city" name="locations-' + rowNum + '-city" class="form-control" value="' + aData[2] + '" data-rule-required="true">';
			jqTds[4].innerHTML = '<input type="text" id="locations-' + rowNum + '-state" name="locations-' + rowNum + '-state" class="form-control" value="' + aData[3] + '" data-rule-required="true">';
			jqTds[5].innerHTML = '<input type="text" id="locations-' + rowNum + '-postal_code" name="locations-' + rowNum + '-postal_code" class="form-control" value="' + aData[4] + '" data-rule-required="true">';
			jqTds[6].innerHTML = '<input type="text" id="locations-' + rowNum + '-arrival_date" name="locations-' + rowNum + '-arrival_date" data-date-format="mm/dd/yyyy" data-date-viewmode="years" class="form-control date-picker" value="' + aData[7] + '" data-rule-required="true">';
			jqTds[7].innerHTML = '<a class="delete-row" href="">Delete</a>';

			

		}

		function saveRow(oTable, nRow) {
			var jqInputs = $('input', nRow);
			oTable.fnUpdate(jqInputs[0].value, nRow, 0, false);
			oTable.fnUpdate(jqInputs[1].value, nRow, 1, false);
			oTable.fnUpdate(jqInputs[2].value, nRow, 2, false);
			oTable.fnUpdate(jqInputs[3].value, nRow, 3, false);
			oTable.fnUpdate(jqInputs[4].value, nRow, 4, false);
			oTable.fnUpdate(jqInputs[5].value, nRow, 5, false);
			oTable.fnUpdate('<a class="edit-row" href="">Edit</a>', nRow, 6, false);
			//oTable.fnUpdate('<a class="delete-row" href="">Delete</a>', nRow, 7, false);
			oTable.fnDraw();
			newRow = false;
			actualEditingRow = null;
		}

		$('body').on('click', '.add-row', function(e) {
			e.preventDefault();
		
			newRow = true;
			var aiNew = oTable.fnAddData(['', '', '', '', '', '', '', '', '', '']);
			var nRow = oTable.fnGetNodes(aiNew[0]);
			editRow(oTable, nRow);
			actualEditingRow = nRow;
		});
		$('#sample_2').on('click', '.cancel-row', function(e) {

			e.preventDefault();
			if (newRow) {
				newRow = false;
				actualEditingRow = null;
				var nRow = $(this).parents('tr')[0];
				oTable.fnDeleteRow(nRow);

			} else {
				restoreRow(oTable, actualEditingRow);
				actualEditingRow = null;
			}
		});
		$('#sample_2').on('click', '.delete-row', function(e) {
			e.preventDefault();
			/*if (newRow && actualEditingRow) {
				oTable.fnDeleteRow(actualEditingRow);
				newRow = false;

			}*/
			var nRow = $(this).parents('tr')[0];
			var deletedStopNumber = $(this).parent().siblings(":first").children("input").val()
			alert(deletedStopNumber);
			$('#sample_2 tbody tr').each(function(index) {
				var thisStopNumber = $(this).children(':first').children("input").val();
				alert(thisStopNumber);
				if(thisStopNumber > deletedStopNumber) {
					$(this).children(':first').html('<input type="hidden" id="locations-' + index + '-stop_number" name="locations-' + index + '-stop_number" class="form-control" value="' + (thisStopNumber - 1) + '">' + (thisStopNumber - 1));
				} else if(thisStopNumber == deletedStopNumber) {
					$('#locations-' + index + '-stop_type').val('Pickup');	
					if($('#wrapper-' + index).length) {
						$('#wrapper-' + index).hide()
						$('#locations-' + index + '-retired').val("1");
					}
				}
			});			

			$(this).parent().parent().hide()

			//oTable.fnDeleteRow(nRow);
							

		});
		$('#sample_2').on('click', '.save-row', function(e) {
			e.preventDefault();

			var nRow = $(this).parents('tr')[0];
			$.blockUI({
				message : '<i class="fa fa-spinner fa-spin"></i> Do some ajax to sync with backend...'
			});
			$.mockjax({
				url : '/tabledata/add/webservice',
				dataType : 'json',
				responseTime : 1000,
				responseText : {
					say : 'ok'
				}
			});
			$.ajax({
				url : '/tabledata/add/webservice',
				dataType : 'json',
				success : function(json) {
					$.unblockUI();
					if (json.say == "ok") {
						saveRow(oTable, nRow);
					}
				}
			});
		});
		$('#sample_2').on('click', '.edit-row', function(e) {
			e.preventDefault();
			if (actualEditingRow) {
				if (newRow) {
					oTable.fnDeleteRow(actualEditingRow);
					newRow = false;
				} else {
					restoreRow(oTable, actualEditingRow);

				}
			}
			var nRow = $(this).parents('tr')[0];
			editRow(oTable, nRow);
			actualEditingRow = nRow;

		});
		var oTable = $('#sample_2').dataTable({
			"aoColumnDefs" : [{
				"aTargets" : [0]
			}],
			"oLanguage" : {
				"sLengthMenu" : "Show _MENU_ Rows",
				"sSearch" : "",
				"oPaginate" : {
					"sPrevious" : "",
					"sNext" : ""
				}
			},
			"bSort" : false,
			"aaSorting" : [[0, 'asc']],
			"aLengthMenu" : [[5, 10, 15, 20, -1], [5, 10, 15, 20, "All"] // change per page values here
			],
			// set the initial value
			"iDisplayLength" : 10,
		});
		$('#sample_2_wrapper .dataTables_filter input').addClass("form-control input-sm").attr("placeholder", "Search");
		// modify table search input
		$('#sample_2_wrapper .dataTables_length select').addClass("m-wrap small");
		// modify table per page dropdown
		//$('#sample_2_wrapper .dataTables_length select').select2();
		// initialzie select2 dropdown
		$('#sample_2_column_toggler input[type="checkbox"]').change(function() {
			/* Get the DataTables object again - this is not a recreation, just a get of the object */
			var iCol = parseInt($(this).attr("data-column"));
			var bVis = oTable.fnSettings().aoColumns[iCol].bVisible;
			oTable.fnSetColumnVis(iCol, ( bVis ? false : true));
		});

	};

	return {
		//main function to initiate template pages
		init : function() {
			//runDataTable();
			runEditableTable();
		}
	};
}(); 