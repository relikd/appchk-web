#!/usr/bin/env python3

import math
import lib_common as mylib
import lib_html as HTML


def fill_bar(percent):
    return '<div class="fillbar"><i style="width: {0}%">{0}%</i></div>'.format(round(percent * 100))


def percent_bar(percent):
    return '<div class="pcbar"><i style="left: {}%"></i></div>'.format(round(percent * 100))


def rank_tile(title, value, additional=None, attr={},
              percent=0.5, rank='?', best='?', worst='?'):
    if additional:
        value += '<i class="snd mg_lr">({})</i>'.format(additional)
    attr = HTML.attr_and(attr, {'class': 'rank'})
    return HTML.div('''
<h4>{}</h4>
{} <b class="mg_lr">{}</b>
<p class="snd">Rank:&nbsp;<b>{}</b>, best:&nbsp;<i>{}</i>, worst:&nbsp;<i>{}</i></p>
'''.format(title, percent_bar(percent), value, rank, best, worst), attr)


def dotgraph(arr):
    ''' Needs list of (title, count, attr_str) tuples '''
    def D(title, count, attr_str=''):
        return '<span{0} title="{1}"><p>{1}</p>{2}</span>'.format(
            attr_str, title, '<i></i>' * count)
    return '<div class="dot-graph">' + ''.join([D(*x) for x in arr]) + '</div>'


def pie_chart(parts, stroke=0.6):
    ''' Needs list of (percent, css_class) tuples '''
    size = 1000
    stroke *= size * 0.5
    stroke_p = '{:.0f}'.format(stroke)
    r = (0.99 * size - stroke) / 2
    r_p = '{:.0f},{:.0f}'.format(r, r)
    mid = '{:.0f}'.format(size / 2)

    def arc(deg):
        deg -= 90
        x = r * math.cos(math.pi * deg / 180)
        y = r * math.sin(math.pi * deg / 180)
        return '{:.0f},{:.0f}'.format(size / 2 + x, size / 2 + y)

    src = ''
    total = 0
    for percent, clss in parts:
        deg = percent * 360
        if percent == 0:
            continue
        elif percent == 1:
            src += f'<circle fill="transparent" class="{clss}" stroke-width="{stroke_p}" cx="{mid}" cy="{mid}" r="{r}"/>'
        else:
            src += f'<path fill="transparent" class="{clss}" stroke-width="{stroke_p}" d="M{arc(total)}A{r_p},0,{1 if deg > 180 else 0},1,{arc(total + deg)}" />'
        total += deg
    return '<svg viewBox="0 0 {0} {0}" width="100" height="100">{1}</svg>'.format(size, src)


def pie_chart_tracker(percent):
    return pie_chart([(1 - percent, 'cs0'), (percent, 'cs1')])
