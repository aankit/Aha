var cursor; //cursor obj
var sliderBar; //slider bar obj

function setup() {
	canvas = createCanvas(205, 350);
	canvas.position(windowWidth/2-125, windowHeight/7);
	canvas.style("border", "1px solid");
	console.log(canvas.width/2, canvas.height/2);
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
	cursor = {
		ox : canvas.width/2,
		oy : canvas.height/2,
		cx : canvas.width/2,
		cy : canvas.height/2,
		select: 0
	};
}

function draw() {
	background(0);
	bar(sliderBar); //draw the bar
	checkSaving();
	//slider
	noStroke();
	fill(55,171,134);
	ellipse(cursor.cx, cursor.cy, 40, 40);

}

function mouseDragged(){
	for(t=0;t<1;t+=0.016){
		bp = bezXY(sliderBar, t);
		if(abs(mouseX - bp.cx) < 15 && abs(mouseY - bp.cy)<15){
			cursor.cx = bp.cx;
			cursor.cy = bp.cy;
			cursor.select = t;
			dir = cursor.select - 0.5; //are we going up or down?
			// minutes = 
		}
	}
}

function mouseReleased() {
	cursor.cx = cursor.ox;
	cursor.cy = cursor.oy;
	//post to the server!

}


function bar(b){
	//the slide
	stroke(107,116,114);
	strokeWeight(12.0);
	strokeCap(ROUND);
	noFill();
	bezier(b.x1, b.y1, b.x2, b.y2, b.x3, b.y3, b.x4, b.y4);
}

function checkSaving(){
	console.log("got to do a check to see if we need to be saving?");
}

function bezXY(b, t, x, y){
	x = Math.pow(1-t, 3) * b.x1 + 3 * Math.pow(1 - t, 2) * t * b.x2 + 3 * (1 - t) * Math.pow(t,2) * b.x3 + Math.pow(t,3) * b.x4;
	y = Math.pow(1-t, 3) * b.y1 + 3 * Math.pow(1 - t, 2) * t * b.y2 + 3 * (1 - t) * Math.pow(t,2) * b.y3 + Math.pow(t,3) * b.y4;
	return {'t': t, 'cx': x, 'cy': y};
}






