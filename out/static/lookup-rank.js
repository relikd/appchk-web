function lookup_rank_js(bundle_id) {
  loadJSON('/stats/rank.json', function(response) {
    let json = JSON.parse(response);
    if (!json) { return; }
    let rank = json[bundle_id];
    let rank_max = json['_ranks'];
    if (!rank || !rank_max) { return; }

    let best = json['_min'];
    let worst = json['_max'];

    function update(i, id, fmt=String) {
      let r = (rank[i] - 1) / (rank_max - 1);
      let target = document.getElementById(id);
      let bar = target.querySelector('.pcbar');
      bar.classList.add(r < 0.5 ? 'g' : 'b');
      bar.firstChild.style.left = r * 100 + '%';
      let meta = target.lastElementChild.children;
      meta[0].innerHTML = rank[i];
      meta[1].innerHTML = fmt(best[i]);
      meta[2].innerHTML = fmt(worst[i]);
    }
    // formatting
    function dot1(x) { return Math.round(x * 10) / 10; }
    function as_percent(x) { return dot1(x * 100) + '%'; }
    function as_pm(x) { return dot1(x) + '/min'; }
    function HHmmss(seconds) {
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      const s = Math.round(seconds % 60);
      return (h<10?'0'+h:h)+':'+(m<10?'0'+m:m)+':'+(s<10?'0'+s:s);
    }
    // order is important!
    update(0, 'sum_rec');
    update(1, 'avg_time', HHmmss);
    update(2, 'sum_time', HHmmss);
    update(3, 'avg_logs_pm', as_pm);
    update(4, 'sum_logs_pm', as_pm);
    update(5, 'pardom');
    update(6, 'subdom');
    update(7, 'tracker_percent', as_percent);
  });
}