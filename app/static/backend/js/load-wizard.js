var FormWizard = function() {
	var wizardContent = $('#wizard');
	var wizardForm = $('#form');
	var initWizard = function() {
		// function to initiate Wizard Form
		wizardContent.smartWizard({
			selected : 0,
			keyNavigation : false,
			onLeaveStep : leaveAStepCallback,
			onShowStep : onShowStep
		});
		var numberOfSteps = 0;
		animateBar();
		initValidator();
	};
	var animateBar = function(val) {
		if (( typeof val == 'undefined') || val == "") {
			val = 1;
		};
		numberOfSteps = $('.swMain > ul > li').length;
		var valueNow = Math.floor(100 / numberOfSteps * val);
		$('.step-bar').css('width', valueNow + '%');
	};
	var initValidator = function() {
		//$.validator.addMethod("cardExpiry", function() {
		//	//if all values are selected
		//	if ($("#card_expiry_mm").val() != "" && $("#card_expiry_yyyy").val() != "") {
		//		return true;
		//	} else {
		//		return false;
		//	}
		//}, 'Please select a month and year');
		$.validator.setDefaults({
			errorElement : "span", // contain the error msg in a span tag
			errorClass : 'help-block',
			errorPlacement : function(error, element) {// render error placement for each input type
				if (element.attr("type") == "radio" || element.attr("type") == "checkbox") {// for chosen elements, need to insert the error after the chosen container
					error.insertAfter($(element).closest('.form-group').children('div').children().last());
				} else if (element.attr("name") == "card_expiry_mm" || element.attr("name") == "card_expiry_yyyy") {
					error.appendTo($(element).closest('.form-group').children('div'));
				} else {
					error.insertAfter(element);
					// for other inputs, just perform default behavior
				}
			},
			ignore : ':hidden',
			rules : {
				name : {
					minlength : 2,
					required : true
				},
				load_type : {
					required : true
				},
				trailer_type : {
					required : true
				},
				total_miles : {
					required : true
				},
				max_weight : {
					required : true
				},
				max_length : {
					required : true
				},
				max_width : {
					required : true
				},
				max_height : {
					required : true
				},
				max_length_type : {
					required : true
				},
				max_width_type : {
					required : true
				},
				max_height_type : {
					required : true
				}/*,
				card_number : {
					minlength : 16,
					maxlength : 16,
					required : true
				},
				card_cvc : {
					digits : true,
					required : true,
					minlength : 3,
					maxlength : 4
				},
				card_expiry_yyyy : "cardExpiry",
				payment : {
					required : true,
					minlength : 1
				}*/
			},
			messages : {
				/*name : "Please specify your first name"*/
			},
			highlight : function(element) {
				$(element).closest('.help-block').removeClass('valid');
				// display OK icon
				$(element).closest('.form-group').removeClass('has-success').addClass('has-error').find('.symbol').removeClass('ok').addClass('required');
				// add the Bootstrap error class to the control group
			},
			unhighlight : function(element) {// revert the change done by hightlight
				$(element).closest('.form-group').removeClass('has-error');
				// set error class to the control group
			},
			success : function(label, element) {
				label.addClass('help-block valid');
				// mark the current input as valid and display OK icon
				$(element).closest('.form-group').removeClass('has-error').addClass('has-success').find('.symbol').removeClass('required').addClass('ok');
			}
		});
	};
	var displayConfirm = function() {
		$('.display-value', form).each(function() {
			var input = $('[name="' + $(this).attr("data-display") + '"]', form);
			if (input.attr("type") == "text" || input.attr("type") == "email" || input.is("textarea")) {
				$(this).html(input.val());
			} else if (input.is("select")) {
				$(this).html(input.find('option:selected').text());
			} else if (input.is(":radio") || input.is(":checkbox")) {

				$(this).html(input.filter(":checked").closest('label').text());
			} else if ($(this).attr("data-display") == 'card_expiry') {
				$(this).html($('[name="card_expiry_mm"]', form).val() + '/' + $('[name="card_expiry_yyyy"]', form).val());
			}
		});
	};
	var onShowStep = function(obj, context) {
		$(".next-step").unbind("click").click(function(e) {
			e.preventDefault();
			wizardContent.smartWizard("goForward");
		});
		$(".back-step").unbind("click").click(function(e) {
			e.preventDefault();
			wizardContent.smartWizard("goBackward");
		});
		$(".finish-step").unbind("click").click(function(e) {
			e.preventDefault();
			onFinish(obj, context);
		});
	};
	var leaveAStepCallback = function(obj, context) {
		return validateSteps(context.fromStep, context.toStep);
		// return false to stay on step and true to continue navigation
	};
	var onFinish = function(obj, context) {
		if (validateAllSteps()) {
			$('.anchor').children("li").last().children("a").removeClass('wait').removeClass('selected').addClass('done');
			wizardForm.submit();
		}
	};
	var validateSteps = function(stepnumber, nextstep) {
		var isStepValid = false;
		if (numberOfSteps > nextstep && nextstep > stepnumber) {
			// cache the form element selector
			if (wizardForm.valid() && validateCurStep(stepnumber)) {// validate the form
				wizardForm.validate().focusInvalid();
				$('.anchor').children("li:nth-child(" + stepnumber + ")").children("a").removeClass('wait');
				//focus the invalid fields
				animateBar(nextstep);
				isStepValid = true;
				return true;
			};
		} else if (nextstep < stepnumber) {
			$('.anchor').children("li:nth-child(" + stepnumber + ")").children("a").addClass('wait');
			animateBar(nextstep);
			return true;
		} else {
			if (wizardForm.valid() && validateCurStep(stepnumber)) {
				$('.anchor').children("li:nth-child(" + stepnumber + ")").children("a").removeClass('wait');
				displayConfirm();
				animateBar(nextstep);
				return true;
			}
		}
	};
	var validateCurStep = function(stepnumber) {
		if(stepnumber == 1) {
			return true;
		}
		else if(stepnumber == 2) {
			return validateLocations();
		} else if (stepnumber == 3) {
			return validateBOLs();
		} else {
			return true;
		}
	}
	var validateAllSteps = function() {
		var isStepValid = validateCurStep(3);
		/*for(i = 1; i < 5; i++) {
			if(!validateCurStep(i)) {
				isStepValid = false;
			}
		}*/
		// all step validation logic
		return isStepValid;
	};

	var validateLocations = function() {
		var message = "";
		var lastLocations = $('#sample_2 tbody tr').length - 1;
		var prevDate = "";
		var dateOrderCorrect = true;
		var index = 0;
		$('#sample_2 tbody tr').each(function(i) {
			//alert(i);
			if(!$(this).is(':hidden')) {
				if(index == 0) {
					if($('#locations-' + i + '-stop_type').val() != "Pickup") {
						message += "The first location must be a \"Pickup\" location.";
					}
				} else if(i == lastLocations && $('#locations-' + i + '-stop_type').val() != "Drop Off") {
					if(message != "") {
						message += "\n";
					}
					message += "The last location must be a \"Drop Off\" location.";
				}

				if(prevDate != "") {
					if($('#locations-' + i + '-arrival_date').datepicker("getDate") < prevDate) {
						dateOrderCorrect = false;
					}
				}
				prevDate = $('#locations-' + i + '-arrival_date').datepicker("getDate");
				index++;
			}
		});
		if(!dateOrderCorrect) {
			if(message != "") {
				message += "\n";
			}
			message += "The arrival dates must be in ascending order.";
		}
		if(message == "") {
			return true;
		} else {
			alert(message);
			return false;
		}
	}
	var validateBOLs = function() {
		var validDrops = 0;
		//need to filter all BOLs where they have not been hidden/removed.
		var orderedBOLs = [];
		var message = "";
		var passesValidation = false;
		$('#sample_2 tbody tr').each(function(i) {
			if($('#locations-' + i + '-retired').val() != "1") {
				$('#locations-' + i + '-bol-wrapper').children('.bol-wrapper').each(function(bol) {
					if($(this).find('.retire-bol-input').val() != "1") {
						cur_index = orderedBOLs.length;
						orderedBOLs[cur_index] = [];
						orderedBOLs[cur_index].push($(this).find('.bol-number').val());
						orderedBOLs[cur_index].push(i);
						orderedBOLs[cur_index].push($('#locations-' + i + '-stop_type').val());
					}
				});
			}
		});
		var pickupBOLs = [];
		var dropoffBOLs = [];
		var matched = 0;
		for (i = 0; i < orderedBOLs.length; i++) {
			if(orderedBOLs[i][2] == "Pickup") {
				var index = pickupBOLs.length;
				pickupBOLs[index] = [];
				for(j = 0; j < orderedBOLs[i].length; j++) {
					pickupBOLs[index][j] = orderedBOLs[i][j];
				}
			} else {
				var index = dropoffBOLs.length;
				dropoffBOLs[index] = [];
				for(j = 0; j < orderedBOLs[i].length; j++) {
					dropoffBOLs[index][j] = orderedBOLs[i][j];
				}
			}
		}
		if (pickupBOLs.length == dropoffBOLs.length) {
			var BOLNumbers = [];
			for (i = 0; i < dropoffBOLs.length; i++) {
				if ( $.inArray(dropoffBOLs[i][0], BOLNumbers) >= 0 ) {
			        message = "All drop off numbers must be unique";
			        passesValidation = false;
			    }  else {
			    	BOLNumbers.push(dropoffBOLs[i][0]);
			    }
			}
			BOLNumbers = [];
			for (i = 0; i < pickupBOLs.length; i++) {
			    if ( $.inArray(pickupBOLs[i][0], BOLNumbers) >= 0 ) {
			    	if (message != "") {
			    		message += "\n";
			    	}
			        message += "All pickup off numbers must be unique";
			        passesValidation = false; // <-- stops the loop
			    }  else {
			    	BOLNumbers.push(pickupBOLs[i][0]);
			    }
			}
			for (i = 0; i < orderedBOLs.length; i++) {
				if(orderedBOLs[i][2] == "Pickup") {
					for (j = orderedBOLs.length - 1; j > i; j--) {
						if(orderedBOLs[i][0] == orderedBOLs[j][0] && orderedBOLs[j][2] != "Pickup") {
							matched++;
							break;
						}
					}
				}
			}
			if(!(matched * 2 == pickupBOLs.length + dropoffBOLs.length)) {
				if (message != "") {
		    		message += "\n";
		    	}
				message += "One or more BOLs is missing a pick/drop location";
			}
			if(message != "") {
				alert(message);
			} else {
				passesValidation = true;
			}
		} else {
			alert('You must have the same number of pickup and dropoff BOLs.');
		}
		return passesValidation;
	}
	return {
		init : function() {
			initWizard();
		}
	};
}();
