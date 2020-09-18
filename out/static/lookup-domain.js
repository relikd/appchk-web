function lookup_domain_fragment(fname_a, fname_b, id1, id2, id3) {
  let dom = window.location.hash.substr(1);
  document.getElementById(id1).innerHTML = dom;

  // load reverse domains json
  loadJSON(fname_a, function(response) {
    let elem = JSON.parse(response)[dom];
    if (!elem || elem.length == 0) {
      document.getElementById(id2).innerHTML = '0 applications';
      document.getElementById(id3).innerHTML = '– None –';
      return;
    }
    document.getElementById(id2).innerHTML = elem.length + ' applications';

    // load app name json
    loadJSON(fname_b, function(response) {
      let name_list = JSON.parse(response);
      var apps = [];
      for (var i = elem.length - 1; i >= 0; i--) {
        let bndl = name_list[elem[i]];
        if (!bndl) { continue; }
        apps.push([bndl[0], bndl[1], bndl[1].toLowerCase()]);
      }
      apps.sort(function(a, b){return a[2] < b[2] ? -1 : a[2] > b[2] ? 1 : 0});
      var content = '';
      for (var i = 0; i < apps.length; i++) {
        content += `
    <a href="/app/` + apps[i][0] + `/">
    <div>
    <img src="/app/` + apps[i][0] + `/icon.png" width="100" height="100">
    <span class="name">` + apps[i][1] + `</span><br />
    <span class="detail">` + apps[i][0] + `</span>
    </div>
    </a>`;
      }
      document.getElementById(id3).innerHTML = '<div id="app-toc" class="no_ul_all">' + content + '</div>';
    });
  });
}