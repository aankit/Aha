editor = {
    cursor: resetCursor(),

    sliderBar: {
        x1 : canvas.width-40,
        y1 : 20,
        x2 : canvas.width/2-21,
        y2 : canvas.height/3,
        x3 : canvas.width/2-21,
        y3 : 2*canvas.height/3,
        x4 : canvas.width-40,
        y4 : canvas.height-20
    },

    scale: 0.016, //scale of the slider

    saver: resetSaver(),

    highlight: { begin: 0, end: 0},

    release_time: null,
    prev_millis: null,
    redo_time: null,
    countdown: null,

    resetCursor: function (){
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
    },

    resetSaver: function (){
        var oldVals = saver;
        saver = {
            timestamp: '', //what time did the human try to save from or starting from
            direction: 0,   //forward, back, around
            duration: 0,    //seconds selected
            undo: {}, //the undo box object passed back from confirm box function
        };
    },

    updateSaver: function(t){
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
    },

    saverDirection: function(){
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
    },

    bar: function(c, b){
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
    },

    bezXY: function(b, t){
        x = Math.pow(1-t, 3) * b.x1 + 3 * Math.pow(1 - t, 2) * t * b.x2 + 3 * (1 - t) * Math.pow(t,2) * b.x3 + Math.pow(t,3) * b.x4;
        y = Math.pow(1-t, 3) * b.y1 + 3 * Math.pow(1 - t, 2) * t * b.y2 + 3 * (1 - t) * Math.pow(t,2) * b.y3 + Math.pow(t,3) * b.y4;
        return {'t': t, 'cx': x, 'cy': y};
    },

    confirmBox: function (c, s){
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
            save_text = "From " + s.duration + " min Ago to Now.";
        } else if (s.direction === 1){
            save_text = "From Now to " + s.duration + " min from Now.";
        } else if (s.direction === 0){
            save_text = s.duration + "min Ago to " + s.duration + " min from Now.";
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
    },

    videoWait: function(c){
        fill(128);
        rect(0,0,c.width, c.height);
        waitText = "Please wait while the\ncurrent video is\n accessed or a new\n video is created.";
        textAlign(CENTER);
        fill(255);
        textSize(20);
        noStroke();
        textLeading(20);
        text(waitText, c.width/2, c.height/3);

    }
}