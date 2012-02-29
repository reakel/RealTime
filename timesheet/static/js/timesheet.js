
var apiData = null;
var list = null;
var form = null;
var apiUrl = "api/v1/entry/";
var apiLimit = 27;
var apiUrlSuffix = "?limit=" + apiLimit;
var currApiUrl = apiUrl + apiUrlSuffix;
$(document).ready(function() {
		list = $("#list").first();
		list.addEntry = addEntry;
		list.getChecked = getChecked;
		list.updateRowClasses = updateRowClasses;
		updateList();
		$('form').find('[name="date"]').datepicker({ dateFormat:'yy-mm-dd' }).datepicker("setDate", new Date());

		$('form').find('[name="start_time"]').timepicker({}).timepicker("setTime", new Date());
		var now = new Date();
		now.setHours(now.getHours()+1);
		$('form').find('[name="end_time"]').timepicker({}).timepicker("setTime", now);
		$('form').first().entry=null;

		$('#dltsbut').button({ text: "Make Timesheet"}).click(function() {
			var chkstr = list.getChecked();
			window.location.href = "maketimesheet?"+chkstr;
			});
		});

function updateList() {
	$.getJSON(currApiUrl, function(data) {
			apiData = data;
			for (var i = 0; i < data.objects.length; i++) {
				list.addEntry(data.objects[i]);
			}
			if (data.meta.next != null) {
				currApiUrl = data.meta.next;
				updateList();
			} else currApiUrl = apiUrl + apiUrlSuffix;
			});
}


function addEntry(data,fade) {
	fade = typeof fade !== 'undefined' ? fade : false;
	var entry = $("<tr></tr>").get(0);
	entry.data = data;
	entry.getTimeDiff = function() {
		//var startTime = new Date(this.data.date + " " + this.data.start_time);
		//var endTime = new Date(this.data.date + " " + this.data.end_time);
		return timeDiff(this.data.end_time,this.data.start_time);
	};
	entry.deleteEntry = deleteEntry;
	entry.updateEntry = function() {
		$('form').entry = this.data;
	};
	entry.update = function() {
		var str = "";
		$(this).html("");
		this.billCB = $('<input type="checkbox"/>');
		this.billCB.attr("checked",true);
		$(this)
			.append($('<td></td>').append(this.billCB))
			.append("<td>" + this.data.date + "</td>")
			.append("<td>" + this.data.start_time  + "</td>")
			.append("<td>" + this.data.end_time + "</td>")
			.append("<td>" + this.getTimeDiff() + "</td>")
			.append(
					$('<td></td>').append(
						$('<div class="delbutton"></div>')
						.button({ icons: { primary: 'ui-icon-trash' }, text: false, background: false})
						.click(function() { 
							$(this).attr("disabled","disabled")
							.fadeOut("fast")
							.parent().parent().get(0).deleteEntry(); 
							})
						.css('height', '90%')
						)
			       );
	};
	entry.update();
	$(entry).hide();
	$(this).find("tbody").prepend(entry);
	this.updateRowClasses();
	if (fade) $(entry).fadeIn("slow");
	else $(entry).fadeIn("slow");
	$(entry).css("display","table-row");
}

function updateRowClasses() {
	$(this).find("tr:even").removeClass("odd even").addClass("even");
	$(this).find("tr:odd").removeClass("odd even").addClass("odd");
}

function deleteEntry() {
	$.ajax({
		context: this,
		url: apiUrl + this.data.id + "/",
		type: 'DELETE',
		contentType: 'application/json',
		data: "",
		dataType: 'html',
		processData: false,
		complete: function(jqXHR,statusText) {
				if (statusText == 'success') {
					$(this).fadeOut("fast", function() {  $(this).remove(); list.updateRowClasses();});
				} else {
					$(this).find(".delbutton").removeAttr("disabled").fadeIn("fast");
				}
			}
		});
}

function getChecked() {
	var ids = [];
	var foundUnChecked = false;
	this.find('tr').not(':eq(0)').each(
			function(key,obj) {
				if (obj.billCB.attr("checked")) {
					ids.push(obj.data.id);
				} else foundUnChecked = true;
			});
	if (foundUnChecked) return "entries=" + JSON.stringify(ids);
	else return "";
}

function timeDiff(endTime, startTime) {
	startTime = startTime.split(':');
	endTime = endTime.split(':');
	var diff = parseInt(endTime[0])*60+parseInt(endTime[1])-parseInt(startTime[0])*60-parseInt(startTime[1]);
	var hourDiff = diff/60;
	if (hourDiff<0) hourDiff += 24;
	diff -= hourDiff*60*60;
	var minDiff = Math.floor(diff/60);
	return hourDiff.toFixed(2);
}	

function sendEntry(form) {
	var type;
	if (form.entry == null || form.entry.id == 0) {
		form.entry = {  };
		type = 'POST';
	} else type = 'PUT';
	form.oldentry = form.entry;
	form.entry.date = $(form).find('[name="date"]').val();
	form.entry.start_time = $(form).find('[name="start_time"]').val() + ":00";
	form.entry.end_time = $(form).find('[name="end_time"]').val() + ":00";
	var data = JSON.stringify(form.entry);
	$(form).find('input[type="submit"]').attr("disabled","disabled");
	$.ajax({
		url: apiUrl,
		type: 'POST',
		contentType: 'application/json',
		data: data,
		dataType: 'json',
		processData: false,
		complete: function(jqXHR,statusText) {
			if (statusText=='success') {
				var uri = jqXHR.getResponseHeader('Location');
				$.getJSON(uri, function(newObj) {
						list.addEntry(newObj,true);
					}
				);
			} else {
				showMessage(form, "error", jqXHR.responseText);
			}
			$(form).find('input[type="submit"]').removeAttr("disabled");

		}	
	}
	);  
	return;

}
function showMessage(parentEle, type, text) {
	var messageTypes = [ "error", "info", "warning" ];
	if (!type in messageTypes) return;
	var message = $(parentEle).find(".message");
	message
		.hide()
		.removeClass(messageTypes.join(" "))
		.addClass(type)
		.html(text)
		.fadeIn("fast")
	setTimeout(function() { message.fadeOut("slow") }, 3000);
}
$(document).ready(function() { $(".message").hide(); });
