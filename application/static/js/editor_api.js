function postMarker(video_id, timestamp, direction, duration){
    //event handler functions, currently the Failed function isn't called on error, not sure why
	function addComplete(evt) {
		console.log("added");
	}
	function addFailed(evt){
		alert("The marker was not added");
	}
	// console.log("v", video_id);
	// console.log("d", day);
	console.log("t", timestamp);
	// console.log("dir: ", direction);
	// console.log("duration: ", duration);
	//let's build our data object for POSTing
	//get section_id for posting
	if( direction > 0){
		start_time = moment(timestamp).format("YYYY-MM-DD HH:mm:ss");
		end_time = moment(timestamp).add(duration, 'minutes');
		console.log("t", timestamp);
	} else if (direction < 0 ){
		start_time = moment(timestamp).subtract(duration, 'minutes');
		end_time = moment(timestamp).format("YYYY-MM-DD HH:mm:ss");
		console.log("t", timestamp);
	}
	//turn timestamp into string for POSTing
	console.log("t", timestamp);
	timestamp = timestamp.format("YYYY-MM-DD HH:mm:ss");
	data = {
		"video_id": video_id,
		"timestamp": timestamp,
		"start_time": start_time,
		"end_time": end_time
	};
	console.log(data);
	// POST the data!!!
	var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
	xmlhttp.addEventListener("load", addComplete, false);
	xmlhttp.addEventListener("error", addFailed, false);
	xmlhttp.open("POST", "/api/marker", true);
	xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	xmlhttp.send(JSON.stringify(data));
}

function getSchedule(){
	timestamp = "1900-01-01T" + moment().format("HH:mm:ss"); //ONLY USE THE WEIRD 1900 timestamp to look up in sched
	day = moment()._d.getDay()-1;
	filters = [{"name": "start_time", "op" : "lte", "val": timestamp},
	{"name": "end_time", "op": "gte", "val": timestamp},
	{"name": "day", "op": "eq", "val": day}];
	$.ajax({
		url: 'api/schedule',
		type: 'GET',
		data: {"q": JSON.stringify({"filters": filters})},
		success: function(data){
			if(data.objects.length===0){
				saver.schedule_id=100;
			} else{
				saver.schedule_id=data.objects[0].id;
			}
			sectionTimeoutID = setTimeout(getSchedule, 10000); //setTimeout
		},
		error: function(error){
			alert('Something went wrong getting the section this recording is related to.');
		}
	});
}

function startNewVideo(){
	//could I have different types of new videos?
	current_timestamp = moment().format("YYYY-MM-DD HH:mm:ss");
	//turn camera on, get new video filename and create and commit a video data obj
	console.log("making a new video, this should only happen once.");
	$.ajax({
		url: 'camera/',
		type: 'GET',
		data: {"state": "on",
		"schedule_id":100,
		"timestamp":current_timestamp},
		success: function(data){
			console.log(data + " is now recording");
			saver.video_id = data;
			console.log(saver.video_id);
			videoTimeoutID = setTimeout(getVideo, 10000); //setTimeout
		},
		error: function(xhr){
			alert('Something went wrong with creating a new video');
		}
	});
}

function getVideo(){
	//retrieve the video id of the file already being recorded
	$.ajax({
		url: 'camera/',
		type: 'GET',
		data: {"state": "current"},
		success: function(data) {
			video_id = parseInt(data, 10);
			if(video_id === -1){
				console.log("here!");
				console.log(video_id);
				startNewVideo();
			} else {
				saver.video_id = video_id;
				console.log(saver.video_id);
				clearTimeout(videoTimeoutID);
				videoTimeoutID = setTimeout(getVideo, 10000);
			}
		},
		error: function(xhr) {
			alert("something went wrong getting the video id.");
		}
	});
}