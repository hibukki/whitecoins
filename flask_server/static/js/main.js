var matrix = document.getElementById("matrix");
var ctx = matrix.getContext("2d");

matrix.height = window.innerHeight;
matrix.width = window.innerWidth;

var matrix_chars = "01234567890-=+_`~[]{}<>?/!@#$%^&*()";
//converting the string into an array of single characters
matrix_chars = matrix_chars.split("");

var font_size = 10;
var columns = matrix.width/font_size; //number of columns for the rain
//an array of drops - one per column
var drops = [];
for(var x = 0; x < columns; x++)
drops[x] = 100000;

//drawing the characters
function draw()
{
    ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
    ctx.fillRect(0, 0, matrix.width, matrix.height);

    ctx.fillStyle = "#0F0"; //green text
    ctx.font = font_size + "px arial";
    //looping over drops
    for(var i = 0; i < drops.length; i++)
    {
      var text = matrix_chars[Math.floor(Math.random()*matrix_chars.length)];
      //x = i*font_size, y = value of drops[i]*font_size
      ctx.fillText(text, i*font_size, drops[i]*font_size);

      //sending the drop back to the top randomly after it has crossed the screen
      //adding a randomness to the reset to make the drops scattered on the Y axis
      if(drops[i]*font_size > matrix.height && Math.random() > 0.975)
        drops[i] = 0;

      drops[i]++;
    }
}

setInterval(draw, 70);

$(document).ready(function() {
    //connect to the socket server.
    // var socket = io.connect('http://' + document.domain + ':' + location.port + '/monitor_mode');

    //receive details from server
    // socket.on('monitor', function(msg) {
        // $('#lte_sensor').html(`LTE Sensor: ${msg.sensor_status}`);
    // });
});


var Utils = {
    renderFieldErrorTooltip: function (selector, msg, placement) {
        var elem;
        if (typeof placement === 'undefined') {
            placement = 'right'; // default to right-aligned tooltip
        }
        elem = $(selector);
        elem.tooltip({'title': msg, 'trigger': 'manual', 'placement': placement});
        elem.tooltip('show');
        elem.addClass('error');
        elem.on('focus click', function(e) {
            elem.removeClass('error');
            elem.tooltip('hide');
        });
    }
};