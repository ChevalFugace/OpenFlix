const PORT = location.port ? ':'+location.port : '';
const API_PREFIX = "http://api." + document.domain + PORT;
const POSTER_URL = "https://image.tmdb.org/t/p/w220_and_h330_face";

var current_page_num = 1;
var current_path = null;
var current_query = null;
var has_scroll_listener = false;

var scrollbar = window.Scrollbar;;

window.fadeIn = function(obj) {

    obj.parentElement.parentElement.style.opacity=1;
    obj.parentElement.parentElement.style.transform="scale(1)";
}

function is_scrolled_near_bottom() {
    
    return (scrollbar.limit.y - scrollbar.offset.y < 400);
    // return $(window).scrollTop()+$(window).height() > $(document).height()-400;
}

function load_medias_grid(data, status) {
    
    if (!("content" in document.createElement("template")))
        return;
    
    var grid = $("#video_grid_view");

    var current_date = new Date();
    
    for (var i = 0; i<data.length; i++) {
        
        const media_info = data[i];
        
        const template = document.querySelector("#grid_item_template");
        var clone = $(document.importNode(template.content, true));
        
        if (media_info.hasOwnProperty("title")) { // a movie
            var type = "movie";
            var title = media_info.title;
            var date = media_info.release_date;
        } else { // a tv show
            var type = "show";
            var title = media_info.name;
            var date = media_info.first_air_date;
        }
        
        clone.find(".title").text(title);

        if (date != null) {

            date = date.split("-");
            let media_date = new Date(date[0],date[1],date[2]);

            if (media_date > current_date) {
                delete clone;
                continue;
            }
            
            clone.find(".year").text(date[0]);
        }

        if (media_info.poster_path == null) {
            var poster_url = "/static/images/missing_poster.jpg";
        } else {
            var poster_url = POSTER_URL + media_info.poster_path;
        }
        
        clone.find("img").attr("src", poster_url);
        clone.find("form").attr("action", type);
        clone.find(".poster_button").attr("value", media_info.id);
        clone.prop("id", media_info.id);
        
        const width = $('.empty-rating').width();
        clone.find('.fill-rating').width(width * (media_info.vote_average/10));
        
        grid.append(clone);
    }

    if (data.length > 0 && is_scrolled_near_bottom()) {
        scrollbar.addListener(scroll_event);
        load_grid();
    }
}

function start_grid_load(path, query) {

    $("#video_grid_view").empty();

    current_page_num = 1;
    current_path = path;
    current_query = query;

    load_grid();
}

function load_grid() {
    
    if (current_query != null && current_path != null) {
        current_query["page"] = current_page_num++;
        let url = API_PREFIX + current_path + "?" + jQuery.param(current_query);
        $.get(url, load_medias_grid);
    }
}

function state_change(event) {

    var search_string = $("#search").val();

    if (search_string)
        search_media(event);
    else
        start_grid_load("/popular", {name: search_string, 
            type: $('input[name="video_type_tab"]:checked').val()});
}

function search_media(event) {

    if (!(event instanceof KeyboardEvent) || !event.key.startsWith("Arrow")) {

        start_grid_load("/search", {name: $("#search").val(), 
            type: $('input[name="video_type_tab"]:checked').val(),
            sort_by: "popularity"});
    }
}

function scroll_event(event) {

    if (is_scrolled_near_bottom()) {
        console.log("ok");
        scrollbar.removeListener(scroll_event);
        load_grid();
    }
}

$(document).ready(function() {

    state_change();
    
    var options = {
        // onScroll: scroll_event
    };
    
    scrollbar.use(OverscrollPlugin);
    scrollbar = scrollbar.init(document.getElementById("main-scrollbar"), {
        plugins: { overscroll: options || false,}
    },);    
});



