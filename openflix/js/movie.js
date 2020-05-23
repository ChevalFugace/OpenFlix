const PORT = location.port ? ':'+location.port : '';
const API_PREFIX = "http://api." + document.domain + PORT;
const POSTER_URL = "https://image.tmdb.org/t/p/w300_and_h450_bestv2";
const BACKDROP_URL = "https:/image.tmdb.org/t/p/w1920_and_h800_multi_faces";
const PEERFLIX_PREFIX = "http://localhost:9000";
const PROBE_FILE = "http://ovh.net/files/10Mio.dat"

window.fadeIn = function(obj) {
    obj.parentElement.parentElement.style.opacity=1;
    obj.parentElement.parentElement.style.transform="scale(1)";
}

function load_data(data, status) {

    if (data.backdrop_path != null) {

        const backdrop_url = BACKDROP_URL + data.backdrop_path;
        $(".backdrop_image").attr("src", backdrop_url);

        const poster_url = POSTER_URL + data.poster_path;
        $(".poster").attr("src", poster_url);

        $(".title").text(data.title);
        $(".overview").text(data.overview);
    }
}


function measure_speed(data, status) {

    endTime = (new Date()).getTime();
    var fileSize = data.length;
    var speed = fileSize / ((endTime - startTime)/1000);

}

// Snap back; here's where we start the timer


function load_peerflix(data, status) {
    
    console.log(navigator.connection.downlinkMax);
}

$(document).ready(function() {

    const cur_url = new URL(document.location);
    
    if (cur_url.searchParams.has("id")) {
        
        let id = cur_url.searchParams.get("id");
        let query = {type: cur_url.pathname.substr(1)};
        let url = API_PREFIX + "/details/" + id + "?" + jQuery.param(query);
        $.get(url, load_data);
    }

    // All set, let's hit it!
    // startTime = (new Date()).getTime();
    // $.get(PROBE_FILE, measure_speed);
    
});