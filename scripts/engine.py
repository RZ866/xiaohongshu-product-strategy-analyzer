"""Deterministic validation, unit economics and gated decisions; no network or AI."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from datetime import date
from urllib.parse import urlparse

DIMENSIONS = {'demand': ('用户需求与痛点', 20), 'profit': ('利润空间', 20),
              'operations': ('新手操作难度', 20), 'content': ('内容表现潜力', 15),
              'competition': ('竞争与差异化', 15), 'risk': ('合规与售后风险', 10)}
LABELS = {'FACT': '已确认（材料所述）', 'INFERENCE': '初步判断', 'HYPOTHESIS': '待验证', 'UNKNOWN': '信息不足'}
DECISIONS = {'A': '优先小规模测试', 'B': '谨慎测试', 'C': '暂不推荐', 'D': '信息不足，暂缓决策'}
COSTS = ('revenue', 'purchase', 'shipping_packaging', 'platform_payment', 'acquisition', 'after_sales', 'other')
MONEY_NAMES = dict(zip(COSTS, ('实际成交收入', '进货成本', '运费及包装', '平台及支付费用', '推广获客成本', '售后与退货损耗', '其他单笔变动费用')))

class ValidationError(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise ValidationError(message)

def number(value):
    require(not isinstance(value, bool), '数字不能为布尔值')
    try:
        n = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValidationError('无效数字') from None
    require(n.is_finite() and n >= 0, '数字必须有限且非负')
    return n

def rounded(n):
    return float(n.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

def text(value, name):
    require(isinstance(value, str) and bool(value.strip()), name + '需要非空文字')

def refs(ids, known, required=False):
    require(isinstance(ids, list) and all(isinstance(x, str) and x in known for x in ids), '证据编号不存在')
    require(not required or bool(ids), '已确认或已评分内容必须有证据')

def claim(c, known):
    require(isinstance(c, dict), '结论需要对象')
    text(c.get('text'), '结论')
    require(c.get('kind') in LABELS, '结论类型无效')
    refs(c.get('evidence_ids'), known, c['kind'] == 'FACT')

def validate(data):
    require(isinstance(data, dict) and data.get('schema_version') == '1.0', 'schema_version需要1.0')
    require(data.get('mode') in ('quick', 'deep'), 'mode必须quick或deep')
    require(isinstance(data.get('demo'), bool), 'demo必须布尔值')
    evidence = data.get('evidence')
    require(isinstance(evidence, list), 'evidence需要列表')
    known = set()
    for e in evidence:
        require(isinstance(e, dict), '证据需要对象')
        text(e.get('id'), '证据id'); text(e.get('source'), '来源'); text(e.get('excerpt'), '材料摘录')
        require(re.fullmatch(r'[A-Za-z0-9_-]{1,64}', e['id']) is not None, '证据id格式无效')
        require(e['id'] not in known, '证据id重复')
        require(e.get('type') in ('USER', 'IMAGE', 'OFFICIAL', 'SAMPLE'), '证据type无效')
        require(e['type'] != 'SAMPLE' or data['demo'], '真实报告不能用演示证据')
        if e['type'] == 'OFFICIAL':
            text(e.get('checked_at'), '官方规则核验日期'); text(e.get('url'), '官方来源URL')
            try: date.fromisoformat(e['checked_at'])
            except ValueError: raise ValidationError('核验日期需要YYYY-MM-DD') from None
            parsed=urlparse(e['url'])
            require(parsed.scheme=='https' and bool(parsed.hostname), '官方证据需要HTTPS来源')
            require(data['demo'] or not parsed.hostname.endswith(('.invalid','.example')), '真实报告不能引用演示官方地址')
        known.add(e['id'])
    product = data.get('product')
    require(isinstance(product, dict), '缺少product')
    text(product.get('name'), '商品名称（可为未知商品）')
    require(isinstance(product.get('fields'), dict), '商品fields需要对象')
    for c in product['fields'].values(): claim(c, known)
    summary = data.get('summary')
    require(isinstance(summary, dict), '缺少summary')
    for key in ('reason', 'biggest_risk', 'direction', 'audience', 'angle'):
        claim(summary.get(key), known)
    for key in ('advantages', 'risks', 'actions'):
        require(isinstance(summary.get(key), list) and len(summary[key]) == 3, key + '需要三项（缺证据可写UNKNOWN）')
        for c in summary[key]: claim(c, known)
    require(isinstance(data.get('questions'), list) and len(data['questions']) <= 3, '最多三个问题')
    for q in data['questions']: text(q, '问题')
    ds = data.get('dimensions')
    require(isinstance(ds, dict) and set(ds) == set(DIMENSIONS), '必须提供六个维度')
    for key, d in ds.items():
        require(isinstance(d, dict), '维度需要对象')
        require(d.get('level') is None or (type(d['level']) is int and 0 <= d['level'] <= 4), '等级须为0至4整数或null')
        for f in ('basis', 'improvement'): text(d.get(f), f)
        for f in ('positive', 'negative', 'missing'):
            require(isinstance(d.get(f), list) and all(isinstance(x, str) and x.strip() for x in d[f]), f+'需要文字列表')
        refs(d.get('evidence_ids'), known, d['level'] is not None)
        require(not d['missing'] or d['level'] is None, '关键证据缺失时必须暂无法评分')
    gates = data.get('gates')
    require(isinstance(gates, dict), '缺少gates')
    for key in ('compliance', 'fulfillment', 'sample'):
        g = gates.get(key)
        require(isinstance(g, dict) and g.get('status') in ('PASS', 'UNKNOWN', 'BLOCK'), '风险门状态无效')
        text(g.get('reason'), '风险门理由'); refs(g.get('evidence_ids'), known, g['status'] != 'UNKNOWN')
    compliance = gates['compliance']
    if compliance['status'] == 'PASS':
        require(any(e['id'] in compliance['evidence_ids'] and e['type'] == 'OFFICIAL' for e in evidence), '准入通过必须引用带核验日期的官方证据')
    budget = data.get('budget')
    require(isinstance(budget, dict), '缺少budget')
    for key in ('max_loss', 'planned_spend'):
        if budget.get(key) is not None: number(budget[key])
    refs(budget.get('evidence_ids'), known, any(budget.get(k) is not None for k in ('max_loss','planned_spend')))
    scenarios = data.get('scenarios')
    require(isinstance(scenarios, dict) and set(scenarios) == {'optimistic','base','conservative'}, '必须有乐观/基准/保守三个情景')
    for s in scenarios.values():
        text(s.get('basis'), '情景依据')
        require(isinstance(s.get('costs'), dict) and set(s['costs']) == set(COSTS), '必须列出所有收入费用项目')
        for cell in s['costs'].values():
            require(isinstance(cell, dict) and cell.get('kind') in ('FACT','HYPOTHESIS','UNKNOWN'), '费用类型无效')
            refs(cell.get('evidence_ids'), known, cell.get('value') is not None and cell['kind']=='FACT')
            if cell.get('value') is not None:
                number(cell['value']); require(cell['kind'] != 'UNKNOWN', '未知费用不能带数字')
            else: require(cell['kind']=='UNKNOWN', '缺失费用必须UNKNOWN')
    require(isinstance(data.get('price_tests', []), list), 'price_tests需要列表')
    for p in data.get('price_tests', []): number(p)
    if data['mode'] == 'deep': validate_strategy(data.get('strategy'), known)
    return data

def validate_strategy(s, known):
    require(isinstance(s, dict), '深度模式必须有strategy')
    for key in ('positioning','pricing','stop_rule','review_rule'):
        claim(s.get(key), known)
    for key, count, fields in (
        ('scenes',3,('name','pain','selling_point','expression')),
        ('plays',3,('name','why','audience','demonstration','materials','risk')),
        ('topics',10,('name','title','pain','angle','cover','structure','placement','purpose')),
        ('days',7,('goal','steps','materials','done','caution')),
        ('phases',4,('period','goal','steps','materials','done','caution'))):
        require(isinstance(s.get(key),list) and len(s[key])==count, key+'数量错误')
        for item in s[key]:
            require(isinstance(item,dict), key+'项目需要对象')
            for f in fields: text(item.get(f), key+'.'+f)
            refs(item.get('evidence_ids'), known)
            if key in ('days','phases'):
                require(item.get('action') in ('VERIFY','PREPARE','PUBLISH','REVIEW'), '计划action无效')
                for f in ('blocked_steps','blocked_done'): text(item.get(f), key+'.'+f)
    require([d.get('day') for d in s['days']]==list(range(1,8)), '必须覆盖第1至7天')
    require([p['period'] for p in s['phases']]==['1-7','8-14','15-21','22-30'], '30天分期必须完整覆盖')
    for f in ('title','angle','purpose'):
        vals=[re.sub(r'\s+','',t[f]) for t in s['topics']]
        require(len(set(vals))==10, '十个选题的'+f+'重复；仍须人工检查语义差异')
    listing=s.get('listing')
    require(isinstance(listing,dict), '缺少listing')
    require(isinstance(listing.get('titles'),list) and len(listing['titles'])==3, '上架标题需要三项')
    for t in listing['titles']: text(t,'上架标题')
    for f in ('hero','sku','detail_order','prohibited'): text(listing.get(f),'listing.'+f)

def economics(s):
    c=s['costs']; missing=[k for k in COSTS if c[k]['value'] is None]
    if missing:
        return {'complete':False,'missing':missing,'contribution':None,'margin':None,'gross':None,
                'contribution_upper_bound': rounded(number(c['revenue']['value'])-sum((number(c[k]['value']) for k in COSTS[1:] if c[k]['value'] is not None),Decimal(0))) if c['revenue']['value'] is not None else None,
                'assumed':any(x['kind']=='HYPOTHESIS' for x in c.values()), 'basis':s['basis']}
    nums={k:number(v['value']) for k,v in c.items()}
    contribution=nums['revenue']-sum((nums[k] for k in COSTS[1:]),Decimal(0))
    return {'complete':True,'missing':[], 'contribution':rounded(contribution),
            'gross':rounded(nums['revenue']-nums['purchase']),
            'margin':rounded(contribution/nums['revenue']*100) if nums['revenue'] else None,
            'assumed':any(x['kind']=='HYPOTHESIS' for x in c.values()), 'basis':s['basis']}

def return_loss(rate, net_loss_per_return):
    """Expected incremental return loss per original order, not a double refund."""
    r=number(rate); require(r<=1,'退货率必须0至1')
    return rounded(r*number(net_loss_per_return))

def order_revenue(unit_price, paid_units=1, discount=0):
    require(type(paid_units) is int and paid_units>0, '付费件数必须正整数')
    value=number(unit_price)*paid_units-number(discount)
    require(value>=0,'优惠不能超过收入'); return rounded(value)

def assess(data):
    validate(data)
    profits={k:economics(v) for k,v in data['scenarios'].items()}
    base=profits['base']; conservative=profits['conservative']
    scores={}
    for k,d in data['dimensions'].items():
        level=d['level']
        if k=='profit':
            if not base['complete']: level=None
            else:
                m=base['margin']; p=base['contribution']
                level=0 if p<=0 else 1 if m<10 else 2 if m<20 else 3 if m<35 else 4
        scores[k]={'level':level,'points':DIMENSIONS[k][1]*level/4 if level is not None else None}
    assessed=sum(DIMENSIONS[k][1] for k,v in scores.items() if v['level'] is not None)
    subtotal=sum(v['points'] for v in scores.values() if v['points'] is not None)
    total=subtotal if assessed==100 else None
    reasons=[]; gates=data['gates']; budget=data['budget']
    if any(g['status']=='BLOCK' for g in gates.values()):
        decision='C'; reasons.append('存在明确风险拦截：'+ '；'.join(g['reason'] for g in gates.values() if g['status']=='BLOCK'))
    elif base['complete'] and base['contribution']<=0:
        decision='C'; reasons.append('基准情景单笔贡献利润不为正；当前条件不适合经营')
    elif base.get('contribution_upper_bound') is not None and base['contribution_upper_bound']<=0:
        decision='C'; reasons.append('仅已知费用已不低于收入；即使未知费用为零也不能获得正贡献。完整利润仍未知')
    elif budget.get('planned_spend') is not None and budget.get('max_loss') is not None and number(budget['planned_spend'])>number(budget['max_loss']):
        decision='C'; reasons.append('计划投入超过用户可承受损失，先缩减测试方案')
    elif not base['complete'] or gates['compliance']['status']=='UNKNOWN' or gates['fulfillment']['status']=='UNKNOWN' or any(k not in data['product']['fields'] or data['product']['fields'][k]['kind']=='UNKNOWN' for k in ('category','use')):
        decision='D'; reasons.append('关键成本、产品用途、准入或履约证据不足，暂缓经营决策')
    elif scores['operations']['level'] is not None and scores['operations']['level']<=1:
        decision='C'; reasons.append('新手操作维度过低，当前执行条件不适合')
    elif total is not None and total<50:
        decision='C'; reasons.append('完整内部评分低于50，当前条件暂不推荐')
    elif (total is not None and total>=75 and conservative['complete'] and conservative['contribution']>0
          and all(g['status']=='PASS' for g in gates.values()) and budget.get('max_loss') is not None
          and budget.get('planned_spend') is not None and scores['demand']['level']>=2):
        decision='A'; reasons.append('完整内部评分达到75，保守情景正贡献且核验门与预算条件具备')
    else:
        decision='B'; reasons.append('基本经营条件具备，但证据覆盖、保守利润、样品或预算仍需谨慎验证')
    publish=decision in ('A','B') and all(g['status']=='PASS' for g in gates.values())
    return {'decision':decision,'label':DECISIONS[decision],'reasons':reasons,'scores':scores,
            'assessed_weight':assessed,'subtotal':subtotal,'total':total,'profits':profits,'publish_ready':publish}

def effective_plan(items, result):
    """All plans become validation-only under C/D or a non-passing gate."""
    return [dict(item,steps=item['steps'] if result['publish_ready'] else item['blocked_steps'],
                 done=item['done'] if result['publish_ready'] else item['blocked_done'],
                 execution='条件具备后执行' if result['publish_ready'] else '仅核验与整改；暂停上架及带货发布') for item in items]
