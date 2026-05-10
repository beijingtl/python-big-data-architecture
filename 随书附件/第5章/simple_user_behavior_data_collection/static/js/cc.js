function guid() {
    function S4() {
       return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    }
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
}
function setCookie(cname,cvalue,exdays) {
  var d = new Date();
  d.setTime(d.getTime()+(exdays*24*60*60*1000));
  var expires = "expires="+d.toGMTString();
  document.cookie = cname + "=" + cvalue + "; " + expires;
  return cvalue;
}
function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for(var i=0; i<ca.length; i++) {
    var c = ca[i].trim();
    if (c.indexOf(name)==0) return c.substring(name.length,c.length);
  }
  return "";
}
var _zhangws_tracker = {};
var _ccid = getCookie("_zhangws_ccid");
_ccid ? _zhangws_tracker["ccid"] = _ccid : _zhangws_tracker["ccid"] = setCookie("_zhangws_ccid", guid(), 365*2)
_zhangws_tracker["dh"] = document.location.href;


function _zhangws_arrayToStr(_r){
    var _rr = [];
    for(i in _r){ _rr.push(i + "=" + _r[i])}
    return encodeURI(_rr.join("&"))
}
function _zhangws_report(params){
    var request = new XMLHttpRequest();
    request.open('GET', '/api/collect/?' + params);
    request.send();
}
function _zhangws_report_pageview(){
    var _r =  JSON.parse(JSON.stringify(_zhangws_tracker));
    _r["t"] = "pageview"; 
    _r["st"] = new Date().getTime();
    return _zhangws_report(_zhangws_arrayToStr(_r));
}
_zhangws_report_pageview();


