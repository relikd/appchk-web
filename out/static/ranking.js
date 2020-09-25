function th(cur_col, cur_asc, names) {
  var txt = '<tr>';
  for (var i = 0; i < names.length; i++) {
    var v = names[i];
    txt += '\n<th>' + v;
    if (v) {
      let cls = (i == cur_col) ? ' class="active"' : '';
      txt += ' <span><a' + (cur_asc == -1 ? cls : '') + ' onClick="sort_by('+i+', -1)">';
      txt += '<svg viewBox="0 0 16 14" width="12"><g><polygon points="8,14 0,0 16,0"/></g></svg>';
      txt += '</a><a' + (cur_asc == 1  ? cls : '') + ' onClick="sort_by('+i+', 1)">';
      txt += '<svg viewBox="0 0 16 14" width="12"><g><polygon points="8,0 0,14 16,14"/></g></svg>';
      txt += '</a></span>';
    }
    txt += '</th>';
  }
  return txt + '</tr>';
}
function td(cols, id) {
  var txt = '\n<tr id="' + id + '">';
  for (var i = 0; i < cols.length; i++) {
    txt += '<td>' + cols[i] + '</td>';
  }
  return txt + '</tr>';
}
function prep(x, i) {
  return [
    i+1 + '. <img class="lozad" data-src="/app/'+x[0]+'/icon.png"/>',  '<a href="/app/'+x[0]+'/">' + x[1] + '</a>', 
    x[2], HHmmss(x[3]), HHmmss(x[4]), as_pm(x[5]), as_pm(x[6]), x[7], x[8], 
    as_percent(x[9]), x[10], dot1(x[11]), new Date(x[12] * 1000).toISOString().slice(0, 16).replace('T',' ')
  ];
}
function update(col, asc) {
  let table = document.getElementById('rank-list');
  let len = _data.length;
  let txt = '';
  for (var i = 0; i < len; i++) {
    txt += td(prep(_data[i], i), _data[i][0])
  }
  table.innerHTML = th(col, asc, [
    '', 'Application', 'Number of recordings', 'Average recording time', 
    'Cumulative recording time', 'Average requests per minute', 
    'Total requests per minute', 'Number of domains', 'Number of subdomains', 
    'Tracker percentage', 'Total number of requests', 'Average number of requests', 
    'Last Update'
  ]) + txt;
  const observer = lozad(); observer.observe();
}
function sort_by(col, asc) {
  let i = col;
  let o = asc;
  _data.sort(function(a, b){ return a[i] < b[i] ? -o : a[i] > b[i] ? o : 0; });
  update(col, asc);
}
function rank_js(fname) {
  loadJSON(fname, function(response) {
    _data = JSON.parse(response);
    update(12,-1);
  });
}