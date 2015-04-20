camera = {
	postMarker: function (timestamp, direction, duration){
		//event handler functions, currently the Failed function isn't called on error, not sure why
		function addComplete(evt) {
			console.log("added");
		}
		function addFailed(evt){
			alert("The marker was not added");
		}
		//let's build our data object for POSTing
		//get section_id for posting
		var date = moment().format("YYYY-MM-DD");
		var day = ((moment(timestamp).day()-1>=0) ? moment(timestamp).day()-1 : 6);
		var start_time = null;
		var end_time = null;
		if( direction > 0){
			start_time = moment(timestamp).format("HH:mm:ss");
			end_time = moment(timestamp).add(duration, 'minutes').format("HH:mm:ss");
		} else if (direction < 0 ){
			start_time = moment(timestamp).subtract(duration, 'minutes').format("HH:mm:ss");
			end_time = moment(timestamp).format("HH:mm:ss");
		} else if (direction===0){
			start_time = moment(timestamp).subtract(duration, 'minutes').format("HH:mm:ss");
			end_time = moment(timestamp).add(duration, 'minutes').format("HH:mm:ss");
		}
		//turn timestamp into string for POSTing
		// timestamp = timestamp.format("YYYY-MM-DD HH:mm:ss");
		var data = {
			"timestamp": timestamp,
			"date": date,
			"day": day,
			"start_time": start_time,
			"end_time": end_time
		};
		// POST the data!!!
		var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
		xmlhttp.addEventListener("load", addComplete, false);
		xmlhttp.addEventListener("error", addFailed, false);
		xmlhttp.open("POST", "/api/marker", true);
		xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
		xmlhttp.send(JSON.stringify(data));
	},

	control: function (state){
		//turn camera on, get new video filename and create and commit a video data obj
		$.ajax({
			url: 'camera/',
			type: 'GET',
			data: {"state": state},
			success: function(data){
				console.log(data);
			},
			error: function(xhr){
				alert('Something went wrong with creating a new video');
			}
		});
	}
};