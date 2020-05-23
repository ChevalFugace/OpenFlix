const PORT = location.port ? ':'+location.port : '';
const API_PREFIX = location.protocol + "//api." + document.domain + PORT;
const POSTER_URL = "https://image.tmdb.org/t/p/w220_and_h330_face";
const BACKDROP_URL = "https:/image.tmdb.org/t/p/w1920_and_h800_multi_faces";

var current_page_num = 1;
var current_path = null;
var current_query = null;

window.fadeIn = function(obj) {
    obj.parentElement.parentElement.style.opacity=1;
    obj.parentElement.parentElement.style.transform="scale(1)";
}

function set_rating(obj, rating) {

    console.log(obj);
    var width = obj.find('.empty-rating').width();
    obj.find('.fill-rating').width(width * (rating/10));
}

function is_scrolled_bottom() {

    return $(window).scrollTop()+$(window).height() == $(document).height();
}

function is_scrolled_near_bottom() {

    return $(window).scrollTop()+$(window).height() > $(document).height()-400;
}

function load_medias_grid(data, status) {
    
    if (!("content" in document.createElement("template")))
        return;
    
    var grid = $("#video_grid_view");

    var current_date = new Date();
    
    for (var i = 0; i<data.length; i++) {
        
        var media_info = data[i];
        
        var template = document.querySelector("#grid_item_template");
        var clone = $(document.importNode(template.content, true));
        
        if (media_info.hasOwnProperty("title")) { // a movie
            var title = media_info.title;
            var date = media_info.release_date;
        } else { // a tv show
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
            var poster_url = "/static/missing_poster.jpg";
        } else {
            var poster_url = POSTER_URL + media_info.poster_path;
        }
        
        clone.find("img").attr("src", poster_url);
        clone.prop("id", media_info.id);
        
        var width = $('.empty-rating').width();
        clone.find('.fill-rating').width(width * (media_info.vote_average/10));
        
        grid.append(clone);
    }

    if (data.length > 0 && is_scrolled_near_bottom())
        load_grid();
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

$(document).ready(function() {

    var id = window.sessionStorage.getItem("id");
    var query = {type: window.sessionStorage.getItem("type")};
    var url = API_PREFIX + "/constent/" + id + "?" + jQuery.param(query);
    var media_info = $.get(url);
    
    if (media_info.backdrop_path != null) {
        var backdrop_url = BACKDROP_URL + media_info.backdrop_path;
        $(".backdrop_image").attr(backdrop_url);
    }
});