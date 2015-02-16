var system = require('system');
var page = require('webpage').create();
var fs = require('fs');

function output_image(page, filename, format) {

    if (format == "svg") {
        var outfile = fs.open(filename, 'w');
        var length = page.content.length;
        outfile.writeLine(length);
        outfile.writeLine(page.content);
        outfile.close();
    } else {
        var outfile = fs.open(filename, 'w');
        var imdata = page.render('test.png',format);
        var length = imdata.length;
        outfile.writeLine(length);
        outfile.writeLine(imdata);
        outfile.close();
    }
}

page.viewportSize = { width: 1280, height: 720 };
page.open('html/animation_test.html', function() {
    t=0;

    interval = setInterval(function(){
	      output_image(page, '/dev/stdout', 'png');
        t++;
	      //system.stderr.write(' '+t++);
	      //if (t>400) {phantom.exit();}
    }, 3000);

    interval2 = setInterval(function(){
        system.stderr.write(' '+t);
    }, 1000);
});

/*
function pack_uint32(num){
  var s='';

  var n = num & 0xffffffff;

  s+=String.fromCharCode((n & 0xff000000) >>> 24);
  s+=String.fromCharCode((n & 0x00ff0000) >>> 16);
  s+=String.fromCharCode((n & 0x0000ff00) >>>  8);
  s+=String.fromCharCode((n & 0x000000ff));

  return s;
}
*/

//data=atob(page.renderBase64());
//data=page.renderBase64();
//system.stdout.write(pack_uint32(data.length));
//system.stdout.write(data);
//page.render('./test_true.png');
//console.log(page.renderBase64('BMP'));
