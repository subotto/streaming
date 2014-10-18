var system = require('system');
var page = require('webpage').create();

var isPageLoaded=false;


page.viewportSize = { width: 1280, height: 720 };
page.open('images/4gears-no-css.svg', function() {
    t=0;
    
    /*
    render_function =  function() {
	//page.render('/dev/stdout',{format: 'jpg'});
	system.stderr.write(' '+t++);
	if (t>400) {phantom.exit();}
	setTimeout(render_function, 1);
    }
    render_function();
    */    
    
    interval = setInterval(function(){
	page.render('/dev/null',{format: 'render-only'});
        t++;
	//system.stderr.write(' '+t++);
	if (t>400) {phantom.exit();}
    }, 10);
    
    interval2 = setInterval(function(){
        system.stderr.write(' '+t);
    }, 1000);
});




/*
    interval = setInterval(function(){
	page.render('/dev/stdout',{format: 'jpg'});
	system.stderr.write(' '+t++);
	//if (t>400) {phantom.exit();}
    }, 10);
*/

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
