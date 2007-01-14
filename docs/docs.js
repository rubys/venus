window.onload=function() {
  var vindex = document.URL.lastIndexOf('venus/');
  if (vindex<0) vindex = document.URL.lastIndexOf('planet/');
  var base = document.URL.substring(0,vindex+6);

  var body = document.getElementsByTagName('body')[0];
  var div = document.createElement('div');
  div.setAttribute('class','z');
  var h1 = document.createElement('h1');
  var span = document.createElement('span');
  span.appendChild(document.createTextNode('\u2640'));
  span.setAttribute('class','logo');
  h1.appendChild(span);
  h1.appendChild(document.createTextNode(' Planet Venus'));

  var inner2=document.createElement('div');
  inner2.setAttribute('class','sectionInner2');
  inner2.appendChild(h1);

  var p = document.createElement('p');
  p.appendChild(document.createTextNode("Planet Venus is an awesome \u2018river of news\u2019 feed reader. It downloads news feeds published by web sites and aggregates their content together into a single combined feed, latest news first."));
  inner2.appendChild(p);

  p = document.createElement('p');
  var a = document.createElement('a');
  a.setAttribute('href',base);
  a.appendChild(document.createTextNode('Download'));
  p.appendChild(a);
  p.appendChild(document.createTextNode(" \u00b7 "));
  a = document.createElement('a');
  a.setAttribute('href',base+'docs/index.html');
  a.appendChild(document.createTextNode('Documentation'));
  p.appendChild(a);
  p.appendChild(document.createTextNode(" \u00b7 "));
  a = document.createElement('a');
  a.setAttribute('href',base+'tests/');
  a.appendChild(document.createTextNode('Unit tests'));
  p.appendChild(a);
  p.appendChild(document.createTextNode(" \u00b7 "));
  a = document.createElement('a');
  a.setAttribute('href','http://lists.planetplanet.org/mailman/listinfo/devel');
  a.appendChild(document.createTextNode('Mailing list'));
  p.appendChild(a);
  inner2.appendChild(p);

  var inner1=document.createElement('div');
  inner1.setAttribute('class','sectionInner');
  inner1.setAttribute('id','inner1');
  inner1.appendChild(inner2);

  div.appendChild(inner1);

  body.insertBefore(div, body.firstChild);
}
