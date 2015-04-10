function postMarker(section_id, video_id, day, timestamp, direction, duration){
    //event handler functions, currently the Failed function isn't called on error, not sure why
	function addComplete(evt) {
		console.log("added");
	}
	function addFailed(evt){
		alert("The scenario was not added");
	}
	//let's build our data object for POSTing
	//get section_id for posting
	if( direction > 0){
		start_time = new Date(timestamp._d.getTime() + duration);
		end_time = timestamp;
	} else if (duration <0 ){
		start_time = timestamp;
		end_time = new Date( timestamp._d.getTime() + duration);
	}
	//turn timestamp into string for POSTing
	timestamp = timestamp.format("YYYY-MM-DD HH:mm:ss");
	data = {
		"video_id": video_id,
		"timestamp": timestamp,
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
}

function updateVideo(){
	//first let's check the schedule and then get the appropriate video id
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
			try{
				saver.schedule_id = data.objects[0].id;
			} catch (err){
				//use the ad hoc section idea of 100, could add some other options here on user input?
				//also I don't have to automatically start the video here, and could ask the user to do it.
				if(saver.schedule!==100){
					saver.schedule_id = 100;
					startNewVideo(schedule_id);
				}
				getVideo();
			}
		},
		error: function(xhr) {
			alert('Something went wrong getting the section this recording is related to.'); //or whatever
		}
	});
}

function startNewVideo(schedule_id){
	if(schedule_id===100){
		current_timestamp = moment().format("YYYY-MM-DD HH:mm:ss");
		//turn camera on, get new video filename and create and commit a video data obj
		$.ajax({
			url: 'camera/',
			type: 'GET',
			data: {"state": "on",
			"schedule_id":schedule_id,
			"timestamp":current_timestamp},
			success: function(data){
				console.log(data + "is now recording");
				saver.video_id = data;
			},
			error: function(xhr){
				alert('Something went wrong with creating a new video');
			}
		});
	}
}

function getVideo(){
	//retrieve the video id of the file already being recorded
	$.ajax({
		url: 'camera/',
		type: 'GET',
		data: {"state": "current"},
		success: function(data) { saver.video_id = data;},
		error: function(xhr) {
			alert("something went wrong getting the video id.");
		}
	});
}