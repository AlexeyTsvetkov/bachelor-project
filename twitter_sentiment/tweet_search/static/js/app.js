function InitSpinner(){
    var opts = {
        lines: 13, length: 35, width: 8, radius: 32,
        corners: 1, rotate: 0, direction: 1, color: '#bdc3c7',
        speed: 1, trail: 60, shadow: false, hwaccel: false,
        className: 'spinner', zIndex: 15, top: 0, left: 0
    };
    var target = document.getElementById('spinner');
    var spinner = new Spinner(opts).spin(target);
}

function ShowAlert(alert_id, message){
    $('#'+alert_id+' > span').text(message);
    var div = $('#'+alert_id);
    div.show();
    return function(){
        div.hide();
    }
}

function InfoMessage(message){
    return ShowAlert('alert-info', message);
}

function ErrorMessage(message){
    return ShowAlert('alert-error', message);
}

function Summary(freqs){
    var summary = $('#summary');
    var summary_pos = $(summary.children('p.positive')[0]);
    var summary_neg = $(summary.children('p.negative')[0]);
    summary_pos.empty();
    summary_neg.empty();
    var fontSize = d3.scale.log().range([10, 60]);

    freqs.sort(function(a, b) {
        a = a[1]
        b = b[1]
        if(a > 0){
            if(b > 0) {
                if(Math.abs(a) > Math.abs(b)){
                    return -1;
                } else {
                    return 1;
                }
            } else {
                return -1;
            }
        } else {
            if(b > 0){
                return 1;
            } else {
                if(Math.abs(a) > Math.abs(b)){
                    return -1;
                } else {
                    return 1;
                }
            }

        }
    });

    for(var i = 0; i < freqs.length; i++) {
        var freq = freqs[i][1];
        var absolute_freq = Math.abs(freq);
        var color = freq > 0 ? '#2ecc71' : '#e74c3c';
        var span = $('<span>' + freqs[i][0] + ' </span>');
        span.css({'font-size': fontSize(absolute_freq), 'color': color});

        var summary = (freq > 0)?summary_pos:summary_neg;
        summary.append(span);
    }

}

function Statistics(counts){
    //pie chart code was taken from https://gist.github.com/enjalot/1203641

    $('#positive-count').text(counts.positive);
    $('#negative-count').text(counts.negative);
    $('#neutral-count').text(counts.neutral);
    var sum = counts.positive+counts.negative+counts.neutral;

    var data = [];

    var add_data = function(color, value) {
        var percent = (100. * value / sum).toFixed(2);
        if(value > 0){
            data.push({'color': color, 'label':percent + '%', 'value':value});
        }
    }

    add_data('#2ecc71', counts.positive);
    add_data('#e74c3c', counts.negative);
    add_data('#34495e', counts.neutral);

    var w = 300, h = 300, r = 150;

    $('#statistics svg').remove();
    var vis = d3.select('#statistics')
        .insert('svg:svg', '#counts')
        .data([data])
        .attr('width', w)
        .attr('height', h)
        .append('svg:g')
        .attr('transform', 'translate(' + r + ',' + r + ')');

    var arc = d3.svg.arc()
        .outerRadius(r);

    var pie = d3.layout.pie()
        .value(function(d) { return d.value; });

    var arcs = vis.selectAll('g.slice')
        .data(pie)
        .enter()
        .append('svg:g')
        .attr('class', 'slice');

    arcs.append('svg:path')
        .attr('fill', function(d, i) { return d.data.color; } )
        .attr('d', arc);

    arcs.append('svg:text')
        .attr('transform', function(d) {
            d.innerRadius = 0;
            d.outerRadius = r;
            return 'translate(' + arc.centroid(d) + ')';
        })
        .attr('text-anchor', 'middle')
        .attr('fill', '#fff')
        .text(function(d, i) { return data[i].label; });
}

function Tweets(tweets){
    var counts = {positive: 0, neutral: 0, negative: 0}
    var container = $('#tweets');
    container.empty();
    for(var i = 0, l = tweets.length; i < l; i++){
        var tweet = tweets[i];
        counts[tweet.label]++;
        var tweet_node = '<div class="tweet ' + tweet.label + ' ">' +
            '<p>' + tweet.text + '</p></div>';
        container.append(tweet_node);
    }
    Statistics(counts);
}

var clicked = false;
function SearchTweets(spinner, tabs){
    var query = $('#search-input').val();
    if(query.length == 0){
        return;
    }

    if(!clicked){
        parallax = -$('#search-input').offset().top + 20;
        $('#main-div').animate({top: parallax}, 800, 'easeInOutQuart');
        tabs.hide();
        tabs.removeClass('hidden');
        clicked = true;
    }

    tabs.hide();
    spinner.show();
    var hide_info = InfoMessage('Wait... It could take some time')
    $.ajax({
        type: 'GET',
        url: '/search_tweets',
        data: {q: query},
        success: function(data){
            var tweets = data.tweets;
            Tweets(tweets);
            Summary(data.most_frequent);
            spinner.hide();
            tabs.show();
            hide_info();
        },
        error: function(data){
            hide_info();
            spinner.hide();
            ErrorMessage('Something went wrong... Please, retry later');
        }
    });
}

$(function(){
    InitSpinner();
    var spinner = $('#spinner');
    var tabs = $('#tabs');

    $('#search-btn').click(function(){
        SearchTweets(spinner, tabs);
    });

    $('#search-input').keydown(function(e) {
        if(e.keyCode == 13) {
            SearchTweets(spinner, tabs);
        }
    });
})