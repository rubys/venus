var entries = []; // list of news items

var days   = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday",
              "Friday", "Saturday"];
var months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"];

// event complete: stop propagation of the event
function stopPropagation(event) {
  if (event.preventDefault) {
    event.preventDefault();
    event.stopPropagation();
  } else {
   event.returnValue = false;
  }
}

// scroll back to the previous article
function prevArticle(event) {
  for (var i=entries.length; --i>=0;) {
    if (!entries[i].anchor) continue;
    if (entries[i].anchor.offsetTop < document.documentElement.scrollTop) {
      window.location.hash=entries[i].anchor.id;
      stopPropagation(event);
      break;
    }
  }
}

// advance to the next article
function nextArticle(event) {
  for (var i=1; i<entries.length; i++) {
    if (!entries[i].anchor) continue;
    if (entries[i].anchor.offsetTop-20 > document.documentElement.scrollTop) {
      window.location.hash=entries[i].anchor.id;
      stopPropagation(event);
      break;
    }
  }
}

// process keypresses
function navkey(event) {
  var checkbox = document.getElementById('navkeys');
  if (!checkbox || !checkbox.checked) return;

  if (!event) event=window.event;
  if (event.originalTarget &&
    event.originalTarget.nodeName.toLowerCase() == 'input' &&
    event.originalTarget.id != 'navkeys') return;

  if (!document.documentElement) return;
  if (!entries[0].anchor || !entries[0].anchor.offsetTop) return;

  key=event.keyCode;
  if (key == 'J'.charCodeAt(0)) nextArticle(event);
  if (key == 'K'.charCodeAt(0)) prevArticle(event);
}

// create (or reset) a cookie
function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else expires = "";
  document.cookie = name+"="+value+expires+"; path=/";
}

// read a cookie
function readCookie(name) {
  var nameEQ = name + "=";
  if (!document.cookie) return;
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

// each time the value of the option changes, update the cookie
function selectOption() {
  var checkbox = document.getElementById('navkeys');
  if (!checkbox) return;
  createCookie("navkeys", checkbox.checked?'true':'false', 365);
}

// add navkeys option to sidebar
function addOption(event) {
  var sidebar = document.getElementById('sidebar');
  if (!sidebar) return;

  var h2 = null;
  for (var i=entries.length; --i>=0;) {
    if (document.getElementById("news-" + i)) break;
    if (entries[i].parent.offsetTop > 0) {
      var a = entries[i].anchor = document.createElement('a');
      a.id = "news-" + i;
      entries[i].parent.insertBefore(a, entries[i].parent.firstChild);
      if (h2 == null) h2 = document.createElement('h2');
    }
  }

  if (h2 != null && !document.getElementById("navkeys")) {
    h2.appendChild(document.createTextNode('Options'));
    sidebar.appendChild(h2);

    var form = document.createElement('form');
    var p = document.createElement('p');
    var input = document.createElement('input');
    input.type = "checkbox";
    input.id = "navkeys";
    p.appendChild(input);
    var a = document.createElement('a');
    a.title = "Navigate entries";
    a.appendChild(document.createTextNode('Enable '));
    var code = document.createElement('code');
    code.appendChild(document.createTextNode('J'));
    a.appendChild(code);
    a.appendChild(document.createTextNode(' and '));
    code = document.createElement('code');
    code.appendChild(document.createTextNode('K'));
    a.appendChild(code);
    a.appendChild(document.createTextNode(' keys'));
    p.appendChild(a);
    form.appendChild(p);
    sidebar.appendChild(form);

    var cookie = readCookie("navkeys");
    if (cookie && cookie == 'true') input.checked = true;
    input.onclick = selectOption;
    document.onkeydown = navkey;
  }
}

// Parse an HTML5-liberalized version of RFC 3339 datetime values
Date.parseRFC3339 = function (string) {
    var date=new Date();
    date.setTime(0);
    var match = string.match(/(\d{4})-(\d\d)-(\d\d)\s*(?:[\sT]\s*(\d\d):(\d\d)(?::(\d\d))?(\.\d*)?\s*(Z|([-+])(\d\d):(\d\d))?)?/);
    if (!match) return;
    if (match[2]) match[2]--;
    if (match[7]) match[7] = (match[7]+'000').substring(1,4);
    var field = [null,'FullYear','Month','Date','Hours','Minutes','Seconds','Milliseconds'];
    for (var i=1; i<=7; i++) if (match[i]) date['setUTC'+field[i]](match[i]);
    if (match[9]) date.setTime(date.getTime()+
        (match[9]=='-'?1:-1)*(match[10]*3600000+match[11]*60000) );
    return date.getTime();
}

// convert datetime to local date
var localere = /^(\w+) (\d+) (\w+) \d+ 0?(\d\d?:\d\d):\d\d ([AP]M) (EST|EDT|CST|CDT|MST|MDT|PST|PDT)/;
function localizeDate(element) {
  var date = new Date();
  date.setTime(Date.parseRFC3339(element.getAttribute('datetime')));
  if (!date.getTime()) return;

  var local = date.toLocaleString();
  var match = local.match(localere);
  if (match) {
    element.innerHTML = match[4] + ' ' + match[5].toLowerCase();
    element.title = match[6] + " \u2014 " + 
      match[1] + ', ' + match[3] + ' ' + match[2];
    return days[date.getDay()] + ', ' + months[date.getMonth()] + ' ' +
      date.getDate() + ', ' + date.getFullYear();
  } else {
    element.title = element.innerHTML + ' GMT';
    element.innerHTML = local;
    return days[date.getDay()] + ', ' + date.getDate() + ' ' +
      months[date.getMonth()] + ' ' + date.getFullYear();
  }

}

// find entries (and localizeDates)
function findEntries() {

  var times = document.getElementsByTagName('time');
   
  for (var i=0; i<times.length; i++) {
    if (times[i].title == "GMT") {
      var date = localizeDate(times[i]);

      var parent = times[i];
      while (parent && 
        (!parent.className || parent.className.split(' ')[0] != 'news')) {
        parent = parent.parentNode;
      }

      if (parent) {
        var info = entries[entries.length] = new Object();
        info.parent   = parent;
        info.date     = date;
        info.datetime = times[i].getAttribute('datetime').substring(0,10);
      }
    }
  }

}

// insert/remove date headers to indicate change of date in local time zone
function moveDateHeaders() {
  var lastdate = ''
  for (var i=0; i<entries.length; i++) {
    var parent = entries[i].parent;
    var date = entries[i].date;

    sibling = parent.previousSibling;
    while (sibling && sibling.nodeType != 1) {
       sibling = sibling.previousSibling;
    }

    if (sibling && sibling.nodeName.toLowerCase() == 'h2') {
      if (lastdate == date) {
        sibling.parentNode.removeChild(sibling);
      } else {
        sibling.childNodes[0].innerHTML = date;
        sibling.childNodes[0].setAttribute('datetime',entries[i].datetime);
        lastdate = date;
      }
    } else if (lastdate != date) {
      var h2 = document.createElement('h2');
      var time = document.createElement('time');
      time.setAttribute('datetime',entries[i].datetime);
      time.appendChild(document.createTextNode(date));
      h2.appendChild(time);
      parent.parentNode.insertBefore(h2, parent);
      lastdate = date;
    }
  }
}

function moveSidebar() {
  var sidebar = document.getElementById('sidebar');
  if (sidebar.currentStyle && sidebar.currentStyle['float'] == 'none') return;
  if (window.getComputedStyle && document.defaultView.getComputedStyle(sidebar,null).getPropertyValue('float') == 'none') return;

  var h1 = sidebar.previousSibling;
  while (h1.nodeType != 1) h1=h1.previousSibling;
  if (h1.nodeName.toLowerCase() == 'h1') h1.parentNode.removeChild(h1);

  var footer = document.getElementById('footer');
  var ul = footer.lastChild;
  while (ul.nodeType != 1) ul=ul.previousSibling;

  var twisty = document.createElement('a');
  twisty.appendChild(document.createTextNode('\u25bc'));
  twisty.title = 'hide';
  twisty.onclick = function() {
    var display = 'block';
    if (this.childNodes[0].nodeValue == '\u25ba') {
      this.title = 'hide';
      this.childNodes[0].nodeValue = '\u25bc';
    } else {
      this.title = 'show';
      this.childNodes[0].nodeValue = '\u25ba';
      display = 'none';
    }
    ul.style.display = display;
    createCookie("subscriptions", display, 365);
  }

  var cookie = readCookie("subscriptions");
  if (cookie && cookie == 'none') twisty.onclick();

  for (var node=footer.lastChild; node; node=footer.lastChild) {
    if (twisty && node.nodeType == 1 && node.nodeName.toLowerCase() == 'h2') {
      node.appendChild(twisty);
      twisty = null;
    }
    footer.removeChild(node);
    sidebar.insertBefore(node, sidebar.firstChild);
  }

  var body = document.getElementById('body');
  sidebar.parentNode.removeChild(sidebar);
  body.parentNode.insertBefore(sidebar, body);
}

// adjust dates to local time zones, optionally provide navigation keys
function personalize() {
  moveSidebar();
  findEntries(); 
  addOption();
  moveDateHeaders();
}

// hook event
window.onload = personalize;
if (document.addEventListener) {
    onDOMLoad = function() {
      window.onload = undefined;
      personalize();
    };
    document.addEventListener("DOMContentLoaded", onDOMLoad, false);
}
