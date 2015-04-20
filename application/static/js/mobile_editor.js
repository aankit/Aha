var cursor; //cursor obj
var sliderBar; //slider bar obj
var scale; //scale of the slider
var saver; //saves the marked time!!
var highlight, release_time, prev_millis, redo_time, countdown; //time selection variables

function setup() {
	canvas = createCanvas(205, 350);
	// canvas.position(windowWidth/2-125, windowHeight/7);
	canvas.style("border", "1px solid");
	canvas.parent("canvas-holder");
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
			camera.postMarker(saver.timestamp, saver.direction, saver.duration);
			resetSaver();
			countdown = false;
		}
	} else {
		if (saver.duration > 0 && saver.direction !== 0 ){
			//text is still showing because saver.duration hasn't been reset, maybe i can use that.
			fill(255);
			textSize(14);
			if (saver.direction !== 0){
				// textMode()
				text(saverDirection(saver) + " " + saver.duration + " min", cursor.cx-75, cursor.cy);
			}
		} else {
			if(abs(touchX-cursor.cx)<cursor.radius && abs(touchY-cursor.cy)<cursor.radius && saver.timestamp){
				saver.direction = 0;
				time_since_touch = moment().unix() - saver.timestamp.unix();
				console.log(time_since_touch);
				select = scale * 4.8 * time_since_touch;
				if (select<0.5) {
					highlight.begin = 0.5 - select;
					highlight.end = 0.5 + select;
				} else {
					highlight.begin = 0;
					highlight.end = 1;
				}
				saver.duration = Math.floor(Math.abs(select)/(0.5*scale*4));
				noStroke();
				fill(255);
				textSize(14);
				futureText = bezXY(sliderBar, highlight.begin);
				pastText = bezXY(sliderBar, highlight.end);
				text(saverDirection(saver)[0] + " " + saver.duration + "min", futureText.cx-75, futureText.cy);
				text(saverDirection(saver)[1] + " " + saver.duration + "min", pastText.cx-75, pastText.cy);
			}
		}
	}

	//draw the cursor
	noStroke();
	fill(cursor.fillColor);
	ellipse(cursor.cx, cursor.cy, cursor.radius, cursor.radius);
	//check if the video needs to be changed
	// var camera_state = camera.control("state");
	// if(camera_state !== "state"){
	// 	videoWait(canvas);
	// }
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
	var oldVals = saver;
	saver = {
		timestamp: '', //what time did the human try to save from or starting from
		direction: 0,	//forward, back, around
		duration: 0,	//seconds selected
		undo: {}, //the undo box object passed back from confirm box function
	};
}

function updateSaver(t){
	//we use the cursor position at this point to set the saver parameters
	//this means that the saver is not tied to the interface
	var select = t - 0.5;
	var duration = Math.floor(Math.abs(select)/(0.5*scale*4));
	if(duration>0){
		if(select<0){
			saver.direction = 1; //we are going forwards in time
			highlight.begin = t;
			highlight.end = 0.5;
		} else if(select>0){
			saver.direction = -1; //are we going backwards in time	
			highlight.begin = 0.5;
			highlight.end = t;
		}
		saver.duration = duration;
	}
	

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
		dir = "+-";
	}
	return dir;
}


function touchMoved(){
	cursor.radius = 40;
	if(abs(touchX-cursor.cx)<cursor.radius && abs(touchY-cursor.cy)<cursor.radius && !countdown)
		//t is the way we move along the curve of the bezier, between zero and one.
		//the scale is used to step through the bezier and is equivalent to one minute.
		for(t=0;t<1;t+=scale){
			bp = bezXY(sliderBar, t);
			if(abs(touchX - bp.cx) < 8 && abs(touchY - bp.cy)<2){
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
	saver.timestamp =  moment(); //database doesn't contain dates, just times
	if(countdown){
		if((touchX > saver.undo.minX && touchX < saver.undo.maxX) && (touchY > saver.undo.minY && touchY < saver.undo.maxY)){
			highlight.begin = 0;
			highlight.end = 0;
			resetSaver();
			countdown = false;
		}
	}
}
