var displayVideos = {

  req: null,
  videos: document.getElementById("videos"),
  investigation: document.getElementById("investigation"),
  conjecture: document.getElementById("conjecture"),
  marker: document.getElementById("marker"),

  filter_types: {
    "investigation": display_investigations,
    "conjecture": display_conjectures,
    "marker": display_markers
  },

  initialize: function(requestedObj, requestedObjId){
    filter_types(requestedObj)(requestedObjId);
    this.bindEvents();
  },

  bindEvents: function(){
    // document.addEventListener("onload", this.onPageReady);
    investigation.addEventListener("click", this.display_investigations);
    conjecture.addEventListener("click", this.display_conjectures);
    marker.addEventListener("click", this.display_markers);
  },

  // onPageReady: function()

  display_investigations: function(filter){
    retrieve_data("investigation", filter, function(){
      if (req.readyState==4 && req.status==200){
        var investigations = JSON.parse(req.responseText);
        for( var i in investigations.objects ){
          var investigation_obj = investigations.objects[i];
          var investigation_div = document.createElement("div");
          var div_id = JSON.stringify(investigation_obj.id);
          investigation_div.setAttribute("id", div_id);
          investigation_dib.setAttribute("class", "row");
          // create_thumbnail_div(div_id, investigation_obj.question);
          var schedule_filter = [{"name": "id", "op": "eq", "val": investigation_obj.id}];
          display_schedule(investigation_div, schedule_filter);
        }
      }
    });
  },

  display_schedule: function(investigation_div, filter){
    retrieve_data("schedule", filter, function(){
      if (req.readyState==4 && req.status==200){
        var schedule = JSON.parse(req.responseText);
        for( var i in schedule.objects ){
          var schedule_obj = schedule.objects[i];
          for (var j=0; j<schedule_obj.videos.length; j++){
            var video_obj = schedule_obj.videos[i];
            var target = video_obj.media_oath+"/final.jpg";
            var thumbnail_src = video_obj.media_path+"/thumbnail.jpg";
            // var target = "/video/?vid="+video.id+"&investigation_id="+filter[0]["val"]
            var video_thumbnail = document.createElement("div");
            var div_id = JSON.stringify(video_obj.id);
            video_thumbnail.setAttribute("id", div_id);
            video_thumbnail.setAttribute("class", "col-sm-6 col-md-4");
            investigation_div.appendChild(video_thumbnail);
            var a = document.createElement("a");
            var thumbnail_img = document.createElement("img");
            thumbnail_img.src = thumbnail_src;
            a.appendChild(video_thumbnail);
            a.href = target;
            video_thumbnail.appendChild(a);
          }
        }
      }
    });
  },

  display_conjectures: function(filter){
    retrieve_data("conjecture", filter, function(){
      if (req.readyState==4 && req.status==200){
        data = JSON.parse(req.responseText);
      }
    });
  },

  display_markers: function(filter){
    //filters are powerful for ordering, filtering, grouping content
    retrieve_data("marker", filter, function(){
      if (req.readyState==4 && req.status==200){
        markers = JSON.parse(req.responseText);
        for(var i in markers.objects){
          var marker = markers.objects[i];
          var div_id = JSON.stringify(marker.id);
          var pretty_time = moment(marker.timestamp).format("MM/DD hh:MM a");
          create_thumbnail_div(div_id, pretty_time);
          for(var j=0;j<marker.videos.length;j++){
            var video = marker.videos[i];
            var thumbnail_src = video.media_path+"/thumbnail.jpg";
            var target = video.media_path+"/final.jpg";
            // var target = "/video/?vid="+video.id+"&marker_id="+marker.id
            display_thumbnail(div_id, thumbnail_src, target);
          }
        }
      }
    });
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
  }
};