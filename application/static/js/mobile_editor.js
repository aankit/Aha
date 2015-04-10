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
	var timeoutID = 0;
	// getSection(); //will be called every ten seconds
	getVideo();
}

function draw() {
	//
	//get or start recording of a video
	background(0);
	bar(canvas, sliderBar); //draw the bar
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
			saver.undo = confirmBox(canvas, saver);
		} else if (prev_millis - release_time > redo_time){
			highlight.begin = 0;
			highlight.end = 0;
			//POST our data!!

			postMarker(saver.timestamp, saver.direction, saver.duration);
			resetSaver();
			countdown = false;
		}
	} else {
		if (saver.duration >0 ){
			//text is still showing because saver.duration hasn't been reset, maybe i can use that.
			fill(30, 223, 184);
			textSize(14);
			// textMode()
			text(saverDirection(saver) + " " + saver.duration + " min", cursor.cx-75, cursor.cy);
		}
	}

	//draw the cursor
	noStroke();
	fill(cursor.fillColor);
	ellipse(cursor.cx, cursor.cy, cursor.radius, cursor.radius);
	//check if the video needs to be changed

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
		duration: 0,	//seconds selected
		undo: {}, //the undo box object passed back from confirm box function
		schedule_id: 0,
		video_id: 0
	};
}

function updateSaver(t){
	//we use the cursor position at this point to set the saver parameters
	//this means that the saver is not tied to the interface
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
	saver.timestamp =  moment(); //database doesn't contain dates, just times
	saver.duration = Math.floor(abs(t-0.5)/(0.5*scale*4));
	// console.log(saver.duration);
}

function touchMoved(){
	cursor.radius = 40;
	if(abs(mouseX-cursor.cx)<cursor.radius && abs(mouseY-cursor.cy)<cursor.radius && !countdown)
		//t is the way we move along the curve of the bezier, between zero and one.
		//the scale is used to step through the bezier and is equivalent to one minute.
		for(t=0;t<1;t+=scale){
			bp = bezXY(sliderBar, t);
			if(abs(mouseX - bp.cx) < 8 && abs(mouseY - bp.cy)<2){
				cursor.cx = bp.cx;
				cursor.cy = bp.cy;
				updateSaver(t);
			}
		}
	else {
		resetCursor();
	}
}

function touchEnded() {
	if(!countdown){
		release_time = millis(); //this is initial value when waiting before posting
		prev_millis = 0;
		redo_time = 0;
		if(saver.duration>0){
			redo_time = 3000;
			countdown = true;
		}
		resetCursor();
	}

}

function touchStarted() {
	if(countdown){
		if((mouseX > saver.undo.minX && mouseX < saver.undo.maxX) && (mouseY > saver.undo.minY && mouseY < saver.undo.maxY)){
			highlight.begin = 0;
			highlight.end = 0;
			resetSaver();
			countdown = false;
		}
	}
}
