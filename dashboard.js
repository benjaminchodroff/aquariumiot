window.targetThing = "";
window.userEmailAddress = "";
window.currentMachine = "";
window.LEDstore = [];
$.support.cors = true;

setTimeout(function(){	
	var presetThing = freeboard.getDatasourceSettings("DemoBoard").thing_id;
	if (presetThing !=='') {
		window.setThing(presetThing);
		$("#thingfield").val(presetThing);
		//$("#thingfield").prop('disabled', true);
	    //$('button#thingsubmit').prop("disabled",true);
	}
	
	$('button#thingsubmit').click(function(e){
		window.setThing($("#thingfield").val());
		freeboard.setDatasourceSettings("DemoBoard", {"thing_id":window.targetThing});
	    $("#thingfield").prop('disabled', true);
	    $('button#thingsubmit').prop("disabled",true);
	});	

	$('button#lcdsubmit').click(function(e){
		var lcdtext = $("#lcdtextfield").val();
	    //$("#lcdtextfield").prop('disabled', true);
	    $('button#lcdsubmit').prop("disabled",true);	
	    window.setRL78Text(lcdtext);
 		$("#lcdtextfield").val('');
	});
	
	$('button#buzzerButton').click(function(e){
		window.sendBuzz();	
	});
	
	$('button#led').click(function(e){
		var lednum = $(this).attr('name');
		if (window.LEDstore[lednum]) {
			//dweetio.dweet_for(window.targetThing+'-send', {lednum:false}, function(err, dweet){console.log(dweet);});	
			window.LEDoff(lednum);
		} 
		else {
			//dweetio.dweet_for(window.targetThing+'-send', {lednum:true}, function(err, dweet){console.log(dweet);});	
			window.LEDon(lednum);
		}
		
	});	
/*	
	$('button#emailsubmit').click(function(e){
			var emailaddy = $("#emailfield").val();
	    	console.log(emailaddy);
	    	window.setEmailAddress(emailaddy);
	    	$("#emailfield").prop('disabled', true);
	    	$('button#emailsubmit').prop("disabled",true);	
	}); 
*/	

	$('button#alertButton').click(function(e){
			var emailaddy = $("#emailfield").val();
	    	$('button#alertButton').prop("disabled",true);
	    	window.sendEmailAlert();
	});	
	$('select#deviceSelect').on('change', function (e) {
			var optionSelected = $("option:selected", this);
    		var valueSelected = this.value;
   			populateStoreList(valueSelected);
	});
	$('select#reportSelect').on('change', function (e) {
			var optionSelected = $("option:selected", this);
    		var valueSelected = this.value;
			freeboard.showLoadingIndicator(true);
			setTimeout(function(){	
				freeboard.showLoadingIndicator(false);
				window.location = valueSelected; 
			},1000);
	});
	$('#alertdiv input').change(function () {
        // The one that fires the event is always the
        // checked one; you don't need to test for this
        var newSelection = $(this).val();
		if (newSelection == "mix_out" || newSelection == "mix_low") {
			$('#alertthresh').prop('disabled', true);
		}
		else $('#alertthresh').prop('disabled', false);
    });
		
},3000);


window.setEmailAddress = function(email) {
	window.userEmailAddress = email;
}

window.sendEmailAlert = function() {
	window.emailActive = true;
	if (window.userEmailAddress !== '') {
		$.ajax({
		  type: "POST",
		  url: "https://mandrillapp.com/api/1.0/messages/send.json",
		  data: {
		    'key': 'gNeJtNdrBCy42EZp3dsMbw',
		    'message': {
		      'from_email': 'alerts@bugswarm.com',
		      'to': [
		          {
		            'email': window.userEmailAddress,
		            'type': 'to'
		          }
		        ],
		      'autotext': 'true',
		      'subject': 'Food Service Machine Alert!',
		      'html': 'Mix out on Machine 1 at Store 1111.'
		    }
		  }
		 }).done(function(response) {
		 });
	}
}

window.resetEmail = function() {
	window.emailActive = false;
}
window.setThing = function(thingname) {
	window.targetThing = thingname;
}
window.LEDoff = function(num) {
	var convert = {};
	convert[num] = false;
	if (window.targetThing == "") {
		freeboard.showDialog($("<div align='center'>Error: Please set thing name!</div>"),"Error!","OK",null,function(){}); 	
		return;	
	}
	dweetio.dweet_for(window.targetThing+'-send', convert, function(err, dweet){console.log(dweet);});
	freeboard.showLoadingIndicator(true);
	setTimeout(function(){	
		freeboard.showLoadingIndicator(false);
	},1000);	
}
window.LEDon = function(num) {
	var convert = {};
	convert[num] = true;
	if (window.targetThing == "") {
		freeboard.showDialog($("<div align='center'>Error: Please set thing name!</div>"),"Error!","OK",null,function(){}); 	
		return;	
	}
	dweetio.dweet_for(window.targetThing+'-send', convert, function(err, dweet){console.log(dweet);});	
	freeboard.showLoadingIndicator(true);
	setTimeout(function(){	
		freeboard.showLoadingIndicator(false);
	},1000);	
}

window.setRL78Text = function(text) {
	if (window.targetThing == "") {
		freeboard.showDialog($("<div align='center'>Error: Please set thing name!</div>"),"Error!","OK",null,function(){}); 	
		return;	
	}
	dweetio.dweet_for(window.targetThing+'-send', {"lcd_text4":text}, function(err, dweet){ if(!err) $('button#lcdsubmit').prop("disabled",false);});
 	freeboard.showLoadingIndicator(true);
		setTimeout(function(){	
			freeboard.showLoadingIndicator(false);
			freeboard.showDialog($("<div align='center'>Text sent to RL78 "+window.targetThing+" LCD!</div>"),"Success!","OK",null,function(){}); 
		},750);	
}

window.sendBuzz = function() {
	if (window.targetThing == "") {
		freeboard.showDialog($("<div align='center'>Error: Please set thing name!</div>"),"Error!","OK",null,function(){}); 	
		return;	
	}
	dweetio.dweet_for(window.targetThing+'-send', {"beep":true}, function(err, dweet){});
 	freeboard.showLoadingIndicator(true);
	setTimeout(function(){	
		freeboard.showLoadingIndicator(false);
		freeboard.showDialog($("<div align='center'>Buzzer activated on RL78 "+window.targetThing+"</div>"),"Success!","OK",null,function(){}); 
	},750);	
}

