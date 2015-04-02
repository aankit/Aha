var cursor; //cursor obj
var sliderBar; //slider bar obj
var scale; //scale of the slider
var highlight, release_time, prev_millis, redo_time, countdown;

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
	setCursor();
	scale = 0.016;
	highlight = {
		begin: 0,
		end: 0
	};
	countdown = false;
}

function draw() {
	background(0);
	bar(sliderBar); //draw the bar
	for(var i=highlight.begin;i<highlight.end;i+=scale){
		hp = bezXY(sliderBar, i);
		noStroke();
		fill(30, 223, 184);
		ellipse(hp.cx, hp.cy, 14, 14);
	}
	noStroke();
	fill(cursor.fillColor);
	ellipse(cursor.cx, cursor.cy, cursor.radius, cursor.radius);
	if((prev_millis - release_time < redo_time) && countdown){
		prev_millis = millis();
		rectMode(CENTER);
		fill(128);
		rect(canvas.width/2, 4*canvas.height/5, 150, 75);
		// textMode(CENTER);
		// text()
	} else if((prev_millis - release_time > redo_time) && countdown){
		highlight.begin = 0;
		highlight.end = 0;
		countdown = false;
	}
	if (cursor.duration > 0){
		if(cursor.direction>0){
			dir = "+";
		}
		else if(cursor.direction<0){
			dir = "-";
		} else {
			//something else here?
		}
		textSize(14);
		// textMode()
		text(dir + " " + cursor.duration + " min", cursor.cx-75, cursor.cy);
	}

}

function setCursor(){
	oldVals = cursor;
	cursor = {
		ox : canvas.width/2,
		oy : canvas.height/2,
		cx : canvas.width/2,
		cy : canvas.height/2,
		radius: 30,
		direction: 0,	//forward, back, around
		duration: 0,	//seconds selected
		fillColor: color(55, 171, 134),
	};
	return oldVals;
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
					cursor.direction = 1; //we are going forwards in time
					highlight.begin = t;
					highlight.end = 0.5;
				} else if((t - 0.5)>0){
					cursor.direction = -1; //are we going backwards in time	
					highlight.begin = 0.5;
					highlight.end = t;
				}
				cursor.duration = Math.floor(abs(t-0.5)/(0.5*scale*4));
				// console.log(cursor.duration);
			}
		}
	else {
		setCursor();
	}
}

function touchEnded() {
	if(!countdown){
		release_time = millis();
		prev_millis = 0;
		redo_time = 0;
		if(cursor.duration>0){
			redo_time = 3000;
			countdown = true;
		}
		setCursor();
		//start the reset countdown...
	}
	//post to the server!
	var xmlhttp = new XMLHttpRequest();
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






