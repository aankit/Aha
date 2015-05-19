var videoMarker = {

  req: null,
  // videos: document.getElementById("videos"),
  past: document.getElementById("past"),
  around: document.getElementById("around"),
  future: document.getElementById("future"),

//  filter_types: {
//    "investigation": display_investigations,
//    "conjecture": display_conjectures,
//    "marker": display_markers
//  },

  initialize: function(){
    this.bindEvents();
    //filter_types(requestedObj)(requestedObjId);
    // console.log(requestedObj);
    // console.log(requestedObjId);
    
  },

  bindEvents: function(){
    // document.addEventListener("onload", this.onPageReady);
    this.past.addEventListener("click", this.mark_moment);
    this.around.addEventListener("click", this.mark_moment);
    this.future.addEventListener("click", this.mark_moment);
  },

  mark_moment: function(e){
    var timestamp = moment();
    var delta = e.target.dataset.savetime;
    var date = moment().format("YYYY-MM-DD");
    var day = ((moment(timestamp).day()-1>=0) ? moment(timestamp).day()-1 : 6);
    var start_time = null;
    var end_time = null;
    if (delta<0){
      end_time = timestamp
      start_time = end_time.subtract(10, 'seconds').format("YYYY-MM-DD HH:MM:SS");
    } else if (delta===0){
      start_time = timestamp.subtract(5, 'seconds').format("YYYY-MM-DD HH:MM:SS");
      end_time = start_time.add(10, 'seconds').format("YYYY-MM-DD HH:MM:SS");
    } else if (delta>0){
      start_time = timestamp()
      end_time = start_time.add(10, 'seconds').format("YYYY-MM-DD HH:MM:SS");
    } else{
      console.log("err...");
    }
    var data = {
      "timestamp": timestamp,
      "date": date,
      "day": day,
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
}
