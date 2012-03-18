
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
		$('form').find('[name="date"]').datepicker({ dateFormat:'yy-mm-dd', firstDay: 1 }).datepicker("setDate", new Date());

		times = findTimes(new Date());
		$('form').find('[name="start_time"]').timepicker({}).timepicker("setTime", times[0]);
		$('form').find('[name="end_time"]').timepicker({}).timepicker("setTime", times[1]);
		$('form').first().entry=null;

		$('#dltsbut').button({ text: "Make Timesheet"}).click(function() {
			var ids = list.getChecked();
			$.ajax({
				url:  'maketimesheet/',
				type: 'POST',
				contentType: 'application/json',
				data: JSON.stringify({ 'entries': ids }),
				dataType: 'json',
				processData: false,
				success: function(data) {
					window.location = data.url;
				}
			});
			});
		});

function updateList() {
	$.ajax({
		url: currApiUrl, 
		dataType: 'json',
		cache: false,
		success: function(data) {
				apiData = data;
				for (var i = 0; i < data.objects.length; i++) {
					list.addEntry(data.objects[i]);
				}
				if (data.meta.next != null) {
					currApiUrl = data.meta.next;
					updateList();
				} else {
					currApiUrl = apiUrl + apiUrlSuffix;
				}
			},
		error:	function(jqXHR, textStatus, errorThrown) {
				$(list).append("Connection error");
			}
		});
}

function updateHoursSum() {
	var sum = 0;
	$(list).find('tbody').find('tr').each(function (key, obj) {
		sum += parseFloat(obj.getTimeDiff());
	});
	$('#hourssum span').html(sum.toFixed(2));
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
		this.billCB.attr("checked",true).val(this.data.id);
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
	$(list).fadeIn("slow");
	$("#dltsbut").fadeIn("slow");
	updateHoursSum();
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
					if ($(list).find("tbody tr").size() <= 1) {
						$(list).fadeOut("fast");
						$("#dltsbut").fadeOut("fast");

					}
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
					ids.push(obj.billCB.val());
				} else foundUnChecked = true;
			});
	return ids;
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

function findTimes(now) {
	var h_now = now.getHours();

	var h_start;
	var m_start = 0;
	var h_end;
	var m_end = 0;
	if (now.getDay() == 1 && (h_now == 14 || h_now == 15) ) {
		//One hour meeting on mondays from 14 to 15
		h_start = h_now;
		h_end = h_now + 1;
	} else if (isExams()) {
	       //Different working hours during exams
		h_start = 10;
		m_start = 30;
		h_end = 13;	
		m_end = 0;
	} else {
		//normal hours
		var h_start = h_now - h_now%2;
		var h_end = h_start + 2;
	}
	var times = [
		formatTime(h_start,m_start),
		formatTime(h_end, m_end)
		];
	return times;
}

function isExams() {
	return false;
}


function formatTime(hours,mins) {
	hours += ''; //convert to string
	mins += '';
	while (hours.length < 2) hours = '0' + hours;
	while (mins.length < 2) mins = '0' + mins;
	return hours + ':' + mins;
}
