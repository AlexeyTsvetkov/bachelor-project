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
    var hide_div = function(){div.hide();}
    return hide_div;
}

function ShowInfo(message){
    return ShowAlert('alert-info', message);
}

function ShowError(message){
    return ShowAlert('alert-error', message);
}

function ShowStats(counts){
    $('#positive-count').text(counts.positive);
    $('#negative-count').text(counts.negative);
    $('#neutral-count').text(counts.neutral);
}

function ShowTweets(tweets){
    var counts = {positive: 0, neutral: 0, negative: 0}
    var container = $('#div-tweets');
    container.empty();
    for(var i = 0, l = tweets.length; i < l; i++){
        var tweet = tweets[i];
        counts[tweet.label]++;
        var tweet_node = '<div class="tweet ' + tweet.label + ' ">' +
            '<p>' + tweet.text + '</p></div>';
        container.append(tweet_node);
    }
    ShowStats(counts);
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
    var hide_info = ShowInfo('Wait... It could take some time')
    $.ajax({
        type: 'GET',
        url: '/search_tweets',
        data: {q: query},
        success: function(data){
            var tweets = data.tweets;
            ShowTweets(tweets);
            spinner.hide();
            tabs.show();
            hide_info();
        },
        error: function(data){
            ShowError('Something went wrong... Please, retry later')
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
});