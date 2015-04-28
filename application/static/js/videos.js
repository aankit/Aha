var req;
var filter_types = {
  "investigation": display_investigations,
  "conjecture": display_conjectures,
  "marker": display_markers
};

$(".filter").on("click", function(e){
    $( "#videos").empty();
    var id_name = $(this).attr('id');
    filter_types[id_name]();
});

function display_investigations(filter){
  retrieve_data("investigation", filter, function(){
    if (req.readyState==4 && req.status==200){
      var investigations = JSON.parse(req.responseText);
      for( var i in investigations.objects ){
        var investigation_obj = investigations.objects[i];
        var div_id = JSON.stringify(investigation_obj.id);
        create_thumbnail_div(div_id, investigation_obj.question);
        var schedule_filter = [{"name": "id", "op": "eq", "val": investigation_obj.id}];
        display_schedule(div_id, schedule_filter);
      }
    }
  });
}

function display_schedule(parent_div, filter){
  retrieve_data("schedule", filter, function(){
    if (req.readyState==4 && req.status==200){
      var schedule = JSON.parse(req.responseText);
      for( var i in schedule.objects ){
        var schedule_obj = schedule.objects[i];
        for (var j=0; j<schedule_obj.videos.length; j++){
          var video = schedule_obj.videos[i]
          var thumbnail_src = video.media_path+"/thumbnail.jpg";
          var target = video.media_oath+"/final.jpg";
          // var target = "/video/?vid="+video.id+"&investigation_id="+filter[0]["val"]
          display_thumbnail(parent_div, thumbnail_src, target);
        }
      }
    }
  });
}

function display_conjectures(filter){
  retrieve_data("conjecture", filter, function(){
    if (req.readyState==4 && req.status==200){
      data = JSON.parse(req.responseText);
    }
  });
}

function display_markers(filter){
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
}

function retrieve_data(endpoint, filter, callback_func){
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


function create_thumbnail_div(div_id, heading){
    $("#videos").append("<div class=row></div>")
    $("#videos").append('<div class="col-sm-6 col-md-4" id="'+div_id+'"></div>');
    $("#"+div_id).append("<h4>"+heading+"</h4>");
}

function display_thumbnail(parent_div, video){
    $("#"+parent_div).append("<div class='thumbnail'><a href=" + 
      target + "><img src='" + thumbnail_src + "' alt='No Video Found.''></a>")
}