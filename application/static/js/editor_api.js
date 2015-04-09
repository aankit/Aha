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
	timestamp = "1900-01-01T" + timestamp.format("HH:mm:ss");
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

function updateVideoFile(){
	section_id = getSection();
	video_id = getVideo(section_id);
	console.log(video_id);
}


function getSection(){
	timestamp = "1900-01-01T" + moment().format("HH:mm:ss");
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
				saver.section_id = data.objects[0].section_id;
			} catch (err){
				//use the ad hoc section idea
				saver.section_id = 100;
			}
		},
		error: function(xhr) {
			alert('Something went wrong getting the section this recording is related to.'); //or whatever
		}
	});
}

function getVideo(section_id){
	if(section_id===100){
		timestamp = "1900-01-01 " + moment().format("HH:mm:ss");
		params = { };
		//turn camera on, get new video filename and create and commit a video data obj
		$.ajax({
			url: 'camera/on/',
			type: 'GET',
			data: {"section_id":section_id,
			"timestamp":timestamp},
			success: function(data){
				console.log(data + "is now recording");
			},
			error: function(xhr){
				alert('Something went wrong with creating a new video');
			}
		});
	}
	filters = [{"name": "section_id", "op": "eq", "val": section_id}];
	video_data = {};
	$.ajax({
		url: 'api/video',
		type: 'GET',
		data: {"q": JSON.stringify({"filters": filters})},
		success: function(data) { video_data = data;},
		error: function(xhr) {
			alert("something went wrong getting the video id.");
		}
	});
	video_id = video_data.objects[0].id;
	return video_id;
}