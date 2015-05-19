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

  addComplete: function(data){
      console.log(data);
      // url = "/api/marker";
      // req = new XMLHttpRequest();
      // req.open("GET", url);
      // req.setRequestHeader("Content-type", "application/json");
      // req.onreadystatechange =;
      // req.send();
  },

  addFailed: function(data){
    alert(data);
  },

  mark_moment: function(e){
    var timestamp = moment();
    var delta = e.target.dataset.saveTime;
    delta = parseInt(delta, 10);
    var date = moment().format("YYYY-MM-DD");
    var day = ((moment(timestamp).day()-1>=0) ? moment(timestamp).day()-1 : 6);
    var start_time = null;
    var end_time = null;
    if( delta > 0){
      start_time = moment(timestamp).format("HH:mm:ss");
      end_time = moment(timestamp).add(delta, 'seconds').format("HH:mm:ss");
    } else if (delta < 0 ){
      start_time = moment(timestamp).subtract(delta, 'seconds').format("HH:mm:ss");
      end_time = moment(timestamp).format("HH:mm:ss");
    } else if (delta===0){
      start_time = moment(timestamp).subtract(delta, 'seconds').format("HH:mm:ss");
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
    req.onreadystatechange = videoMarker.addComplete;
    xmlhttp.addEventListener("error", videoMarker.addFailed, false);
    xmlhttp.open("POST", "/api/marker", true);
    xmlhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xmlhttp.send(JSON.stringify(data));
  }
};
