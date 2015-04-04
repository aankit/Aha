var cursor; //cursor obj
var sliderBar; //slider bar obj
var scale; //scale of the slider
var saver; //saves the marked time!!
var highlight, release_time, prev_millis, redo_time, countdown; //time selection variables

function setup() {
	canvas = createCanvas(205, 350);
	canvas.position(windowWidth/2-125, windowHeight/7);
	canvas.style("border", "1px solid");
	sliderBar = {
		x1 : canvas.width-40,
		y1 : 20,
		x2 : canvas.width/2-21,
		y2 : canvas.height/3,
		x3 : canvas.width/2-21,
		y3 : 2*canvas.height/3,
		x4 : canvas.width-40,
		y4 : canvas.height-20
	};
	resetCursor();
	resetSaver();
	scale = 0.016;
	highlight = {
		begin: 0,
		end: 0
	};
	countdown = false;
	textFont("Helvetica");
}

function draw() {
	background(0);
	bar(sliderBar); //draw the bar
	//draw highlighted time segment if one exists
	for(var i=highlight.begin;i<highlight.end;i+=scale){
		hp = bezXY(sliderBar, i);
		noStroke();
		if (countdown){
			fill(255);
		} else {
			fill(30, 223, 184);
		}
		ellipse(hp.cx, hp.cy, 14, 14);
	}
	//hold a highlighted time segment if one exists
	if (countdown){
		if (prev_millis - release_time < redo_time){
			prev_millis = millis();
			fill(86);
			boxY  = 3 * canvas.height/4;
			rect(0, boxY, canvas.width, boxY/3);
			textAlign(CENTER);
			fill(255);
			textSize(16);
			noStroke();
			text("Recorded", canvas.width/2, boxY+20);
			textSize(13);
			save_text = '';
			if (saver.direction === -1){
				save_text = "From " + saver.duration + " min ago to Now.";
			} else if (saver.direction === 1){
				save_text = "From Now to " + saver.duration + " min from Now.";
			}
			text(save_text, canvas.width/2, boxY+50);

		} else if (prev_millis - release_time > redo_time){
			highlight.begin = 0;
			highlight.end = 0;
			//POST our data!!
			// postMarker(saver.timestamp, saver.direction, saver.duration);
			resetSaver();
			countdown = false;
		} else if (saver.duration > 0){

		}
	} else {
		if (saver.duration >0 ){
			//text is still showing because saver.duration hasn't been reset, maybe i can use that.
			fill(30, 223, 184);
			textSize(14);
			// textMode()
			text(saverDirection() + " " + saver.duration + " min", cursor.cx-75, cursor.cy);
		}
	}

	//draw the cursor
	noStroke();
	fill(cursor.fillColor);
	ellipse(cursor.cx, cursor.cy, cursor.radius, cursor.radius);

}

function resetCursor(){
	oldVals = cursor;
	cursor = {
		ox : canvas.width/2,
		oy : canvas.height/2,
		cx : canvas.width/2,
		cy : canvas.height/2,
		radius: 30,
		fillColor: color(55, 171, 134),
	};
	return oldVals;
}

function resetSaver(){
	oldVals = saver;
	saver = {
		day: '', //to check against database to find section
		timestamp: '', //to check against database to find section
		direction: 0,	//forward, back, around
		duration: 0	//seconds selected
	};
}

function saverDirection(){
	dir = '';
	if(saver.direction>0){
		dir = "+";
	}
	else if(saver.direction<0){
		dir = "-";
	} else {
		//both directions here!
	}
	return dir;
}

function touchMoved(){
	cursor.radius = 40;
	if(abs(mouseX-cursor.cx)<cursor.radius && abs(mouseY-cursor.cy)<cursor.radius && !countdown)
		for(t=0;t<1;t+=scale){
			bp = bezXY(sliderBar, t);
			if(abs(mouseX - bp.cx) < 8 && abs(mouseY - bp.cy)<2){
				cursor.cx = bp.cx;
				cursor.cy = bp.cy;
				if((t - 0.5)<0){
					saver.direction = 1; //we are going forwards in time
					highlight.begin = t;
					highlight.end = 0.5;
				} else if((t - 0.5)>0){
					saver.direction = -1; //are we going backwards in time	
					highlight.begin = 0.5;
					highlight.end = t;
				}
				saver.day = moment().format('d'); //based on recurring events, so  day is important
				saver.timestamp = "1900-01-01T" + moment().format('HH:mm:ss'); //database doesn't contain dates, just times
				saver.duration = Math.floor(abs(t-0.5)/(0.5*scale*4));
				// console.log(saver.duration);
			}
		}
	else {
		resetCursor();
	}
}

function touchEnded() {
	release_time = millis(); //this is initial value when waiting before posting
	if(!countdown){
		prev_millis = 0;
		redo_time = 0;
		if(saver.duration>0){
			redo_time = 3000;
			countdown = true;
		}
		resetCursor();
	}

}

function postMarker(timestamp, direction, duration){
    //event handler functions, currently the Failed function isn't called on error, not sure why
	function addComplete(evt) {
		console.log("added");
	}
	function addFailed(evt){
		alert("The scenario was not added");
	}
	section_id = getSection();


	var xmlhttp = new XMLHttpRequest();   // new HttpRequest instance 
	xmlhttp.addEventListener("load", addComplete, false);
	xmlhttp.addEventListener("error", addFailed, false);
	xmlhttp.open("POST", "/api/marker", true);
	xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
	xmlhttp.send(JSON.stringify(data));
}

function getSection(day, timestamp){
	//get date info first to search the schedule table
	filters = [{"name":"start_time", "op" : "lte", "val": timestamp},{"name":"end_time", "op": "gte", "val": timestamp}];
	schedule_data = {};
	$.get('api/schedule', {"q": JSON.stringify({"filters": filters})}, function(data) { schedule_data = data;});
	section_id = schedule_data.objects[0].section_id;
	return section_id;
}


function bar(b){
	//the slide
	stroke(107,116,114);
	strokeWeight(12.0);
	strokeCap(ROUND);
	noFill();
	bezier(b.x1, b.y1, b.x2, b.y2, b.x3, b.y3, b.x4, b.y4);
	strokeWeight(5.0);
	line(canvas.width/2-15, canvas.height/2, canvas.width/2+15, canvas.height/2); //center line
	//upper 10 minute line
	//lower 10 minute line
}

function bezXY(b, t, x, y){
	x = Math.pow(1-t, 3) * b.x1 + 3 * Math.pow(1 - t, 2) * t * b.x2 + 3 * (1 - t) * Math.pow(t,2) * b.x3 + Math.pow(t,3) * b.x4;
	y = Math.pow(1-t, 3) * b.y1 + 3 * Math.pow(1 - t, 2) * t * b.y2 + 3 * (1 - t) * Math.pow(t,2) * b.y3 + Math.pow(t,3) * b.y4;
	return {'t': t, 'cx': x, 'cy': y};
}






