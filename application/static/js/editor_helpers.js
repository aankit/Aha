function saverDirection(s){
	dir = '';
	if(s.direction>0){
		dir = "+";
	}
	else if(s.direction<0){
		dir = "-";
	} else {
		//both directions here!
	}
	return dir;
}

function postMarker(timestamp, direction, duration){
    //event handler functions, currently the Failed function isn't called on error, not sure why
	function addComplete(evt) {
		console.log("added");
	}
	function addFailed(evt){
		alert("The scenario was not added");
	}
	//let's build our data object for POSTing
	//get section_id for posting
	// section_id = getSection();
	
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
		"timestamp": timestamp,
		"start_time": start_time,
		"end_time": end_time
	};

	var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
	xmlhttp.addEventListener("load", addComplete, false);
	xmlhttp.addEventListener("error", addFailed, false);
	xmlhttp.open("POST", "/api/marker", true);
	xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	xmlhttp.send(JSON.stringify(data));
}

function getSection(day, timestamp){
	//get date info first to search the schedule table
	//need to add day to the filters
	filters = [{"name":"start_time", "op" : "lte", "val": timestamp},{"name":"end_time", "op": "gte", "val": timestamp}];
	schedule_data = {};
	$.get('api/schedule', {"q": JSON.stringify({"filters": filters})}, function(data) { schedule_data = data;});
	section_id = schedule_data.objects[0].section_id;
	return section_id;
}


function bar(c, b){
	//the slide
	stroke(107,116,114);
	strokeWeight(12.0);
	strokeCap(ROUND);
	noFill();
	bezier(b.x1, b.y1, b.x2, b.y2, b.x3, b.y3, b.x4, b.y4);
	strokeWeight(5.0);
	line(c.width/2-15, c.height/2, c.width/2+15, c.height/2); //center line
	//upper 10 minute line
	//lower 10 minute line
}

function bezXY(b, t, x, y){
	x = Math.pow(1-t, 3) * b.x1 + 3 * Math.pow(1 - t, 2) * t * b.x2 + 3 * (1 - t) * Math.pow(t,2) * b.x3 + Math.pow(t,3) * b.x4;
	y = Math.pow(1-t, 3) * b.y1 + 3 * Math.pow(1 - t, 2) * t * b.y2 + 3 * (1 - t) * Math.pow(t,2) * b.y3 + Math.pow(t,3) * b.y4;
	return {'t': t, 'cx': x, 'cy': y};
}

function confirmBox(c, s){
	//draw the confirm box!
	fill(86);
	boxY  = 3 * c.height/4;
	rect(0, boxY, c.width, boxY/3);
	textAlign(CENTER);
	//informational text in the undo box
	fill(255);
	textSize(15);
	noStroke();
	text("Recorded", c.width/2, boxY+17);
	textSize(13);
	save_text = '';
	if (s.direction === -1){
		save_text = "From " + s.duration + " min ago to Now.";
	} else if (s.direction === 1){
		save_text = "From Now to " + s.duration + " min from Now.";
	}
	text(save_text, c.width/2, boxY+38);
	rectMode(CENTER);
	fill(107,116,114);
	stroke(107,116,114);
	//draw undo button
	rect(c.width/2, boxY+65, c.width-20, 20);
	//make it rounded
	strokeCap(ROUND);
	strokeWeight(5);
	undoLeftX = c.width/2-(c.width-20)/2;
	undoRightX = c.width/2+(c.width-20)/2;
	undoTop = boxY+54;
	undoBottom = boxY+77;
	line(undoLeftX, undoTop, undoRightX , undoTop);
	line(undoLeftX, undoBottom,  undoRightX, undoBottom);
	//put text in it
	undo_time = 3-Math.floor((prev_millis - release_time)/1000);
	noStroke();
	fill(255,0,0, 200);
	textSize(15);
	undo_text = "Undo (" + undo_time + ")";
	text(undo_text, c.width/2, undoTop+15);
	return {minX: undoLeftX, maxX: undoRightX, minY: undoTop, maxY: undoBottom};
}