var displayVideos = {

  req: null,
  videos: document.getElementById("videos"),
  investigation: document.getElementById("investigation"),
  conjecture: document.getElementById("conjecture"),
  marker: document.getElementById("marker"),

//  filter_types: {
//    "investigation": display_investigations,
//    "conjecture": display_conjectures,
//    "marker": display_markers
//  },

  initialize: function(requestedObj, requestedObjId){
    this.bindEvents();
    //filter_types(requestedObj)(requestedObjId);
    console.log(requestedObj);
    console.log(requestedObjId);
    
  },

  bindEvents: function(){
    // document.addEventListener("onload", this.onPageReady);
    this.investigation.addEventListener("click", this.display_investigations);
    this.conjecture.addEventListener("click", this.display_conjectures);
    this.marker.addEventListener("click", this.display_markers);
  },

  retrieve_data: function(endpoint, filter, callback_func){
      endpoint = typeof endpoint !== 'undefined' ? endpoint : 'investigation';
      filter = typeof filter !== 'undefined' ? filter : '';
      //not sending filter yet
      url = "/api/" + endpoint;
      req = new XMLHttpRequest();
      req.open("GET", url);
      req.setRequestHeader("Content-type", "application/json");
      req.onreadystatechange = callback_func;
      req.send();
  },
  // onPageReady: function()

  display_investigations: function(filter){
     displayVideos.retrieve_data("investigation", filter, function(){
       if (req.readyState==4 && req.status==200){
         var investigations = JSON.parse(req.responseText);
         for( var i in investigations.objects ){
          var investigation_obj = investigations.objects[i];
          investigation_div = displayVideos.create_thumbnail_container(investigation_obj);
          // create_thumbnail_div(div_id, investigation_obj.question);
          var schedule_filter = [{"name": "id", "op": "eq", "val": investigation_obj.id}];
          displayVideos.display_schedule(investigation_div, schedule_filter);
         }
       }
     });
  },

  display_schedule: function(investigation_div, filter){
    this.retrieve_data("schedule", filter, function(){
      if (req.readyState==4 && req.status==200){
        var schedule = JSON.parse(req.responseText);
        for( var i in schedule.objects ){
          var schedule_obj = schedule.objects[i];
          for (var j=0; j < schedule_obj.videos.length; j++){
            var video = schedule_obj.videos[j];
            displayVideos.display_video_thumbnail(video, investigation_div);
          }
        }
      }
    });
  },

  display_conjectures: function(filter){
    this.retrieve_data("conjecture", filter, function(){
      if (req.readyState==4 && req.status==200){
        data = JSON.parse(req.responseText);
      }
    });
  },

  display_markers: function(filter){
    //filters are powerful for ordering, filtering, grouping content
    displayVideos.retrieve_data("marker", filter, function(){
      if (req.readyState==4 && req.status==200){
        markers = JSON.parse(req.responseText);
        for(var i in markers.objects){
          var marker_obj = markers.objects[i];
          console.log(marker_obj);
          marker_div = displayVideos.create_thumbnail_container(marker_obj);
          var pretty_time = moment(marker_obj.timestamp).format("MM/DD hh:MM a");
          //create_thumbnail_div(div_id, pretty_time);
          for(var j=0;j<marker_obj.videos.length;j++){
            var video = marker_obj.videos[j];
            displayVideos.display_video_thumbnail(video, marker_div);
            // var target = "/video/?vid="+video.id+"&marker_id="+marker.id
            //display_thumbnail(div_id, thumbnail_src, target);
          }
        }
      }
    });
  },

  create_thumbnail_container: function(container_obj){
      var container_div = document.createElement("div");
      var div_id = JSON.stringify(container_obj.id);
      container_div.setAttribute("id", div_id);
      container_div.setAttribute("class", "row");
      return container_div;
  },


  display_video_thumbnail: function(video_obj, container_div){
      var target = video_obj.media_path+"/video.mp4";
      var thumbnail_src = video_obj.media_path+"/thumbnail.jpg";
      // var target = "/video/?vid="+video.id+"&investigation_id="+filter[0]["val"]
      var thumbnail_container = document.createElement("div");
      thumbnail_container.setAttribute("class", "col-sm-6 col-md-4");
      var video_thumbnail = document.createElement("div");
      var div_id = JSON.stringify(video_obj.id);
      video_thumbnail.setAttribute("id", div_id);
      video_thumbnail.setAttribute("class", "thumbnail");
      var a = document.createElement("a");
      var thumbnail_img = document.createElement("img");
      thumbnail_img.src = thumbnail_src;
      a.appendChild(thumbnail_img);
      a.href = target;
      video_thumbnail.appendChild(a);
      thumbnail_container.appendChild(video_thumbnail);
      container_div.appendChild(thumbnail_container);
      displayVideos.videos.appendChild(container_div);
  }

};
