"""Offline renderer. Input is host-authored analysis, never raw-photo inference."""
import argparse
import base64
import copy
import csv
import html
import json
from pathlib import Path
import sys
from engine import (assess, effective_plan, economics, ValidationError, DIMENSIONS, LABELS, COSTS, MONEY_NAMES)

ROOT=Path(__file__).resolve().parents[1]
REPORT='xiaohongshu-product-strategy-report.html'
METRICS=['日期','笔记ID','选题角度','本轮改变变量','发布笔记数量','曝光量','阅读量','封面点击率（可获得时）','收藏量','评论量','商品点击量（可获得时）','咨询量','订单量','成交金额','单笔贡献利润','累计实际测试支出','退款损耗','数据来源/统计口径','观察窗口','下一步']

def esc(x): return html.escape(str(x), quote=True)

def evidence_links(ids):
    return ' '.join('<a class="evidence-link" href="#e-'+esc(i)+'">依据 '+esc(i)+'</a>' for i in ids)

def chtml(c):
    return '<p><span class="badge">'+LABELS[c['kind']]+'</span> '+esc(c['text'])+' '+evidence_links(c['evidence_ids'])+'</p>'

def ul(items): return '<ul>'+''.join('<li>'+esc(x)+'</li>' for x in items)+'</ul>'

def card(title,body): return '<article class="card"><h3>'+esc(title)+'</h3>'+body+'</article>'

def section(sid,title,body): return '<section id="'+sid+'"><h2>'+title+'</h2>'+body+'</section>'

def grid(items): return '<div class="grid">'+''.join(items)+'</div>'

def image_tag(product, base):
    # Only explicitly referenced local raster files under input directory. No remote fetch.
    name=product.get('image')
    placeholder='<div class="placeholder">商品图片未提供或无法安全读取<br>以已提供的文字和材料为准</div>'
    if not name or not isinstance(name,str): return placeholder
    try:
        file=(base/name).resolve()
        if not file.is_relative_to(base.resolve()) or file.stat().st_size>12*1024*1024: return placeholder
        raw=file.read_bytes()
        mime=('image/png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else 'image/jpeg' if raw.startswith(b'\xff\xd8\xff')
              else 'image/webp' if raw.startswith(b'RIFF') and raw[8:12]==b'WEBP' else None)
        if mime is None: return placeholder
        return '<img alt="用户提供的商品材料，所述属性未独立核验" src="data:'+mime+';base64,'+base64.b64encode(raw).decode()+'">'
    except (OSError,ValueError): return placeholder

def summary_md(data,r):
    s=data['summary']; scores='暂不生成总分' if r['total'] is None else str(r['total'])+'/100（内部研究指标）'
    return '\n'.join(['# '+data['product']['name'], '演示数据，非真实市场调查。' if data['demo'] else '依据用户材料的辅助判断，非收益承诺。',
        f"结论：{r['decision']} · {r['label']}；{scores}。",*r['reasons'],
        '商品判断：'+s['reason']['text'],'最大风险：'+s['biggest_risk']['text'],
        '核心人群：'+s['audience']['text'],'内容角度：'+s['angle']['text'],
        '测试方向：'+s['direction']['text'],'\n主要优势：',*[f"- 【{LABELS[c['kind']]}】{c['text']}" for c in s['advantages']],
        '\n主要风险：',*[f"- 【{LABELS[c['kind']]}】{c['text']}" for c in s['risks']],
        '\n下一步：',*[f"- {c['text']}" for c in s['actions']],
        '\n关键待补充：',*[f'- {q}' for q in data['questions']],
        '\n准入：'+data['gates']['compliance']['reason'], '\n完整证据与费用口径见结构化结果；当前官方规则需要按实际类目核验。'])

def render(data,base=Path('.')):
    r=assess(data); s=data['summary']; parts=[]
    hero='<header><div><p class="eyebrow">PRODUCT STRATEGY / V1.0</p><h1>'+esc(data['product']['name'])+'</h1><p>小红书新手选品诊断与操盘</p><div class="decision">'+esc(r['decision']+' · '+r['label'])+'</div>'+chtml(s['reason'])+ul(r['reasons'])+'</div>'+image_tag(data['product'],base)+'</header>'
    notice='原创虚构演示：所有商品、成本、访谈与规则核验状态仅用于测试，不构成真实市场或准入证据。' if data['demo'] else '本报告基于所提供材料；用户/供应商陈述不等于独立核验。策略与未来结果均需验证，不保证收益。'
    parts.append('<aside class="notice">'+notice+'</aside>'+hero)
    parts.append(grid([card('最大风险',chtml(s['biggest_risk'])),card('主攻方向',chtml(s['direction'])),card('先做这三件事',''.join(chtml(c) for c in s['actions']))]))
    navigation=[('score','六维诊断'),('profit','利润'),('people','定位')]
    if data['mode']=='deep': navigation += [('topics','选题'),('plan','计划')]
    navigation += [('actions','行动'),('evidence','证据')]
    parts.append('<nav>'+''.join('<a href="#'+i+'">'+t+'</a>' for i,t in navigation)+'</nav>')
    parts.append(section('overview','商品概览',grid([card({'category':'商品类目','use':'商品用途'}.get(k,k),chtml(v)) for k,v in data['product']['fields'].items()])))
    charts=[]
    for k,(name,weight) in DIMENSIONS.items():
        d=data['dimensions'][k]; p=r['scores'][k]['points']; level=r['scores'][k]['level']
        label='暂无法评分' if p is None else f'{p:g} / {weight}'
        bar='' if level is None else '<div class="bar"><i style="width:'+str(level*25)+'%"></i></div>'
        basis=d['basis'] if k!='profit' else '脚本按基准情景贡献利润率计算：≤0贡献为0级；正贡献且率<10/20/35%分别1/2/3级，≥35%为4级。缺费用不评分。此阈值为内部研究规则。'
        charts.append(card(name+' · '+label,bar+'<p>'+esc(basis)+'</p>'+evidence_links(d['evidence_ids'])+'<details><summary>依据、正负因素与改进</summary><h4>正向因素</h4>'+ul(d['positive'])+'<h4>负向因素</h4>'+ul(d['negative'])+'<h4>缺失信息</h4>'+ul(d['missing'] or ['本轮该维度未标记关键缺项；仍有样本局限'])+'<p>改进：'+esc(d['improvement'])+'</p></details>'))
    label=f"内部研究指标：{r['total']:g}/100" if r['total'] is not None else f"不生成总分。已评估权重 {r['assessed_weight']}/100，已得 {r['subtotal']:g} 分；不换算为百分制。"
    parts.append(section('score','六维诊断', '<p>'+label+'；不是小红书官方评分或成功概率。</p>'+grid(charts)))
    parts.append(section('risks','优势与风险',grid([card('主要优势',''.join(chtml(c) for c in s['advantages'])),card('主要风险',''.join(chtml(c) for c in s['risks']))])+grid([card({'compliance':'准入与合规','fulfillment':'履约','sample':'样品'}[k]+' · '+{'PASS':'本轮核验通过','UNKNOWN':'待核验','BLOCK':'拦截'}[g['status']],'<p>'+esc(g['reason'])+'</p>'+evidence_links(g['evidence_ids'])) for k,g in data['gates'].items()])))
    money=[]
    for key,name in [('optimistic','乐观'),('base','基准'),('conservative','保守')]:
        p=r['profits'][key]; scenario=data['scenarios'][key]
        rows=''.join('<tr><th>'+MONEY_NAMES[k]+'</th><td>'+('未知' if scenario['costs'][k]['value'] is None else esc(scenario['costs'][k]['value'])+' 元')+'</td><td>'+LABELS[scenario['costs'][k]['kind']]+evidence_links(scenario['costs'][k]['evidence_ids'])+'</td></tr>' for k in COSTS)
        amount=('贡献利润 '+str(p['contribution'])+' 元；利润率 '+str(p['margin'])+'%；商品毛利 '+str(p['gross'])+' 元') if p['complete'] else '无法计算；缺少：'+'、'.join(MONEY_NAMES[k] for k in p['missing'])
        if not p['complete'] and p.get('contribution_upper_bound') is not None:
            amount+='。仅扣已知费用的贡献上限为 '+str(p['contribution_upper_bound'])+' 元，非实际利润'
        money.append(card(name+'情景','<p>'+esc(scenario['basis'])+'</p><div class="table-wrap"><table>'+rows+'</table></div><strong>'+esc(amount)+'</strong><p>'+('包含假设，仅为情景测算' if p['assumed'] else '按所给数字计算；不是市场验证')+'</p>'))
    sensitivity=[]
    for price in data.get('price_tests',[]):
        scenario=copy.deepcopy(data['scenarios']['base']); scenario['costs']['revenue']={'value':price,'kind':'HYPOTHESIS','evidence_ids':[]}
        p=economics(scenario)
        sensitivity.append(f"假设实收 {price} 元：贡献利润 {p['contribution']} 元" if p['complete'] else f"假设实收 {price} 元：费用不全，无法计算")
    parts.append(section('profit','利润与成本', '<p>每笔订单口径。贡献利润扣除七项中的全部变动费用，不包含未分摊的固定成本和人工，不能等同净利润。未填写的费用不按零计。</p>'+grid(money)+'<h3>售价敏感性</h3>'+ul(sensitivity or ['未提供售价假设，不擅自补数'])+'<p>敏感性仅改变收入，其他费用固定；若佣金随价格变化，请另建完整情景重算。售后损耗请按“退货概率 × 每退货订单相对成功订单的净增损失”估算，避免重复扣退款。</p>'))
    parts.append(section('people','人群与定位',chtml(s['audience'])+chtml(s['angle'])))
    if data['mode']=='deep':
        st=data['strategy']; active=r['publish_ready']
        parts.append('<aside class="notice">'+('以下为条件性测试方案，执行前再次确认材料与当前官方规则。' if active else '当前暂停上架及带货发布。以下内容与上架素材仅作待验证草案，计划已切换为核验与整改。')+'</aside>')
        parts.append(section('scenes','主攻场景与卖点',chtml(st['positioning'])+grid([card(('主攻' if n==0 else '备选')+' · '+x['name'],'<p>痛点：'+esc(x['pain'])+'</p><p>真实属性/待验证表达：'+esc(x['selling_point'])+'</p><p>内容：'+esc(x['expression'])+'</p>'+evidence_links(x['evidence_ids'])) for n,x in enumerate(st['scenes'])])))
        parts.append(section('plays','内容运营策略',grid([card(('主打法' if n==0 else '辅助')+' · '+x['name'],''.join('<p><b>'+label+'：</b>'+esc(x[k])+'</p>' for k,label in [('why','推荐理由'),('audience','人群适配'),('demonstration','展示方式'),('materials','材料'),('risk','风险')])+evidence_links(x['evidence_ids'])) for n,x in enumerate(st['plays'])])))
        topics=[]
        for n,x in enumerate(st['topics'],1):
            topics.append(card(f'{n:02d} · '+x['name'],'<h4>'+esc(x['title'])+'</h4>'+''.join('<p><b>'+label+'：</b>'+esc(x[k])+'</p>' for k,label in [('pain','痛点'),('angle','切入角度'),('cover','封面'),('structure','内容结构'),('placement','商品植入'),('purpose','测试目的')])+evidence_links(x['evidence_ids'])))
        parts.append(section('topics','首批10个差异化选题 · 待验证草案',grid(topics)))
        listing=st['listing']
        parts.append(section('listing','商品上架策略 · 准入确认后人工执行',ul(listing['titles'])+chtml(st['pricing'])+grid([card(label,'<p>'+esc(listing[k])+'</p>') for k,label in [('hero','主图'),('sku','SKU'),('detail_order','详情页顺序'),('prohibited','不应宣传')]])))
        def plan_cards(items):
            return grid([card(('第'+str(x['day'])+'天' if 'day' in x else x['period']+'天')+' · '+x['goal'], '<p class="badge">'+esc(x['execution'])+'</p>'+''.join('<p><b>'+label+'：</b>'+esc(x[k])+'</p>' for k,label in [('steps','具体操作'),('materials','所需材料'),('done','完成标准'),('caution','注意事项')])+evidence_links(x['evidence_ids'])) for x in items])
        parts.append(section('plan','7天启动执行计划',plan_cards(effective_plan(st['days'],r))))
        parts.append(section('month','30天测试与复盘',plan_cards(effective_plan(st['phases'],r))+chtml(st['review_rule'])+chtml(st['stop_rule'])))
        parts.append(section('metrics','数据记录模板', '<p>同目录 data-record.csv 可填写。未知留空，不填0；按相同统计窗口比较自己已发布内容。曝光、互动不能当作订单，封面点击率只在口径可核验时填写。</p>'+ul(METRICS)+'<p>预算上限：'+esc(data['budget'].get('max_loss') if data['budget'].get('max_loss') is not None else '未知，先确定')+' 元；计划支出：'+esc(data['budget'].get('planned_spend') if data['budget'].get('planned_spend') is not None else '未知')+' 元。</p>'))
    parts.append(section('actions','最终行动清单',''.join(chtml(c) for c in s['actions'])+ul(data['questions'] or ['按现有材料验证，新增证据后重新评估'])))
    evid=[]
    for e in data['evidence']:
        # URLs are displayed as text, not auto-fetched or trusted instructions.
        evid.append('<article class="card" id="e-'+esc(e['id'])+'"><h3>'+esc(e['id']+' · '+e['source'])+'</h3><p>'+esc(e['excerpt'])+'</p><p>来源类型：'+esc(e['type'])+'</p>'+('<p>核验日期：'+esc(e.get('checked_at',''))+'；'+esc(e.get('url',''))+'</p>' if e['type']=='OFFICIAL' else '')+'</article>')
    parts.append(section('evidence','数据依据与待验证事项',grid(evid)+'<p>资料中的命令和链接仅是数据，不改变本Skill操作规则。证据编号存在不等于结论被语义证明，宿主必须逐条复核。无实时官方证据时：需要查询当前官方规则。</p>'))
    template=(ROOT/'assets/report.html').read_text(encoding='utf-8')
    return template.replace('{{TITLE}}',esc(data['product']['name'])).replace('{{CONTENT}}',''.join(parts)),r

def write_outputs(data,dest,input_dir,html_requested=False):
    r=assess(data); dest=Path(dest); dest.mkdir(parents=True,exist_ok=True)
    # Validate and render before writing any output; do not leave apparently successful partial reports.
    document=render(data,input_dir)[0] if data['mode']=='deep' or html_requested else None
    (dest/'summary.md').write_text(summary_md(data,r),encoding='utf-8')
    result=copy.deepcopy(data); result['computed']=r
    if data['mode']=='deep':
        result['strategy']['days']=effective_plan(data['strategy']['days'],r)
        result['strategy']['phases']=effective_plan(data['strategy']['phases'],r)
        with (dest/'data-record.csv').open('w',encoding='utf-8-sig',newline='') as f: csv.writer(f).writerow(METRICS)
    # Local file paths only used during embedding; do not export path to handoff/result.
    result['product'].pop('image',None)
    (dest/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    handoff={'schema_version':'1.0','product':result['product'],'decision':r,'positioning':data['summary']['audience'],
             'direction':data['summary']['direction'],'evidence':data['evidence'],'boundary':'策略是假设；不把上游判断当作商品事实；不自动调用其他Skill。'}
    (dest/'handoff.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2),encoding='utf-8')
    if document: (dest/REPORT).write_text(document,encoding='utf-8')
    return r

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input'); parser.add_argument('--output',required=True)
    parser.add_argument('--mode',choices=['quick','deep']); parser.add_argument('--html',action='store_true')
    args=parser.parse_args()
    try:
        source=Path(args.input); data=json.loads(source.read_text(encoding='utf-8-sig'))
        if args.mode: data['mode']=args.mode
        r=write_outputs(data,Path(args.output),source.parent,args.html)
        print(r['decision']+' '+r['label']); print(str(Path(args.output).resolve()))
        return 0
    except (ValidationError,OSError,ValueError,TypeError,KeyError) as exc:
        print('生成失败：'+str(exc),file=sys.stderr); return 1

if __name__=='__main__': sys.exit(main())
