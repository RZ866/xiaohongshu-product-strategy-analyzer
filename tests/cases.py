"""Original synthetic teaching cases, not market research or live platform rules."""
import copy

def c(text,kind='HYPOTHESIS',ids=None): return {'text':text,'kind':kind,'evidence_ids':ids or []}

def case():
    ev=[{'id':'P','type':'SAMPLE','source':'虚构样品资料卡','excerpt':'演示商品：桌面理线夹，硅胶，6枚装，单孔设计。适用线径待实测，不宣称所有桌面均可粘。'},
        {'id':'N','type':'SAMPLE','source':'虚构访谈记录','excerpt':'演示受访者提到拔下充电线后线头滑到桌后，购买前担心残胶和线径不匹配；不是实际访谈。'},
        {'id':'C','type':'SAMPLE','source':'虚构订单成本单','excerpt':'每单6枚；预计实收19.9元，进货4元，运费包装4元；可承受测试损失200元，拟支出120元。'},
        {'id':'R','type':'OFFICIAL','source':'演示专用的虚构准入核验记录，不是真实官方规则','excerpt':'仅用来演示PASS状态的输入结构；未对真实商品准入进行核验。真实使用必须替换为当前实际官方规则及对应商品证明。','checked_at':'2026-10-10','url':'https://example.invalid/demo-only'},
        {'id':'F','type':'SAMPLE','source':'虚构履约与样品检查表','excerpt':'演示供应商确认单件发货与售后地址；演示样品可完成放线取线。残胶与长期老化尚未测试，不可作功效承诺。'},
        {'id':'M','type':'SAMPLE','source':'虚构竞品截图对照说明','excerpt':'演示对照材料中存在多种理线方案。只能比较信息展示角度，不证明本品独家、市场销量或搜索量。'}]
    dimensions={}
    for key,basis,positive,negative,improvement,ids in [
        ('demand','材料描述了具体线头滑落问题，但样本不能代表市场规模','问题可用一个桌面镜头解释','演示访谈不能验证实际需求','真实询问目标用户并记录原话',['N']),
        ('profit','由七项费用计算，主观等级由脚本覆盖','小单可核算变动成本','推广与售后均是假设','用实际结算替换假设',['C']),
        ('operations','小件可以单人拍摄、打包；履约资料齐备的演示条件','无需复杂安装工具','适配答疑会占用时间','准备线径与表面适配说明',['P','F']),
        ('content','取线、走线和孔径均可近景拍摄','手机即可展示细节','没实测前不能宣称牢固不掉','同一机位记录步骤而非编造前后效果',['P']),
        ('competition','只评价样本中的信息表达差异，非蓝海判断','可突出适配边界说明','无独家功能和市场份额证据','实际补充同价位材料再比较',['M']),
        ('risk','演示准入与履约资料齐备，长期残胶风险仍应披露','非复杂功能日用品的演示案例','材质不明桌面不得承诺适用','首批记录投诉并停止不适配表面的推荐',['R','F'])]:
        dimensions[key]={'level':3,'basis':basis,'positive':[positive],'negative':[negative],'missing':[], 'improvement':improvement,'evidence_ids':ids}
    scenarios={}
    for key,vals in [('optimistic',[19.9,4,4,.6,0,.3,0]),('base',[19.9,4,4,.6,2,.8,0]),('conservative',[19.9,4,4,.6,4,2,0])]:
        keys=['revenue','purchase','shipping_packaging','platform_payment','acquisition','after_sales','other']
        scenarios[key]={'basis':'全部为演示假设；每单6枚，包邮，收入已扣优惠。不同情景仅变化获客与售后损耗，不是平台费率。',
            'costs':{k:{'value':v,'kind':'HYPOTHESIS','evidence_ids':['C']} for k,v in zip(keys,vals)}}
    summary={'reason':c('仅在演示核验条件成立、保守利润仍为正时，适合以小预算测试；不能据此判断市场畅销。','INFERENCE',['N','C','F']),
        'biggest_risk':c('线径、桌面材质与残胶问题尚需逐项实测，禁止许诺无痕适配所有桌面。','INFERENCE',['P','F']),
        'direction':c('先测试单人办公桌拔线后的线头归位场景。'),
        'audience':c('经常给手机充电、拔线后需要到桌后找线头的办公桌使用者；在意桌面适配与取放顺手。'),
        'angle':c('主打法为场景教程：拍清楚放线、取线与适用边界；购买理由待实际反馈验证。'),
        'advantages':[c('演示规格为6枚装。','FACT',['P']),c('取线动作适合用近景说明。','INFERENCE',['P']),c('演示每单成本可逐项核算。','INFERENCE',['C'])],
        'risks':[c('残胶与长期稳定性未验证。','FACT',['F']),c('没有实际销量、搜索量或市场规模数据。','UNKNOWN'),c('获客与售后费用是假设，实际贡献利润可能不同。','INFERENCE',['C'])],
        'actions':[c('取一份样品，测量线径与孔径，并记录桌面材质和取放情况。'),c('向供应商索要有效资质、发货和售后证明，对照当前官方规则核验。'),c('核对七项每单费用与200元演示止损预算，再决定是否开展小规模内容测试。')]}
    specs=[
        ('痛点观察','拔掉充电线后，线头该放哪里？','线头滑到桌后','动作拆解','线头、桌沿、手部三个位置同框','拍拔线动作→标出线头位置→展示放线方法→说明桌面适配','在放线步骤出现商品','验证用户是否主动提到找线头的困扰'),
        ('使用场景','小书桌的充电区，可以怎么安排？','桌面可用位置少','空间布局','俯拍一张桌面，划出充电与写字区','测桌面→画区→摆线→展示取放路径','作为充电区可选配件','比较空间布局角度是否带来收藏'),
        ('使用方法','理线夹怎么放线？先看这几个步骤','不知道如何放取线','步骤教学','手部放线过程分三格','核对孔径→局部试用→放线→取线→注意事项','每一步展示实际样品','观察教程是否减少操作咨询'),
        ('购买顾虑','买理线夹前，先确认你的桌面材质','担心残胶和不适配','适配筛选','桌面材质标签与样品并列','列材质→说明未测范围→安排隐蔽位置试用→记录移除情况','展示边界而非保证无痕','记录材质适配类问题是否集中'),
        ('替代方案','理线夹、束线带，分别用在哪里？','不知道选哪种工具','用途对照','两类工具与同一根线同框','区分固定线头与整理线束→示范步骤→列不适用情况','只展示本品实际承担的任务','验证用途对照是否帮助选购'),
        ('日常习惯','下班收桌面时，充电线放哪一步整理？','收桌时容易忘记线材','流程嵌入','收桌动作顺序卡','移开杂物→整理充电区→放线→核查次日取放','出现在收桌流程中，不编造个人坚持经历','比较日常流程是否吸引持续关注'),
        ('产品细节','孔径没看清，理线夹可能买不合适','线材粗细不匹配','尺寸实测准备','卡尺、孔位和线材近景','量孔→量线→试放→标明测量误差与结果','用样品尺寸说明选择条件','观察尺寸展示是否减少规格咨询'),
        ('价格价值','一包6枚理线夹，先数清你有几个位置要用','担心买多浪费','数量预算','6枚样品和位置草图','数充电位置→估需要数量→核对实付价→计算闲置数量','仅按真实6枚规格演示，不做虚假折扣','验证按需购买角度的商品点击表现'),
        ('常见误区','理线夹不是所有线材问题的答案','误以为能整理所有线束','用途边界','单根线头和大线束对照','列任务→示范适用动作→说明不适用任务→替代选择','明确本品作用范围','观察边界说明对售前顾虑的影响'),
        ('用户问题','床头充电线能用理线夹吗？先做适配检查','床头表面和线长不确定','场景迁移验证','床头样板、线长标记、夹子','确认材质→量线长→局部试装→记录取放→无结果先不推荐','作为待验证方案，不写已实测好用','收集床头场景是否值得单独拍摄的需求')]
    topics=[dict(zip(('name','title','pain','angle','cover','structure','placement','purpose'),row),evidence_ids=['P']) for row in specs]
    days=[]
    daily=[
        ('验证商品与风险','索要成本单和资质；核验类目；用样品测孔径与目标线径；逐项填写每单费用。','样品、尺子、供应商资料、费用单','成本七项可追溯；准入、履约、样品三门有结论。','未确认不采购库存。','VERIFY'),
        ('定位用户与场景','找目标桌面使用者描述找线过程；记录原话；选一个主场景及两个备选。','访谈记录、桌面草图','写出人群、触发动作、顾虑、购买理由各一条。','不把少量反馈当市场规模。','PREPARE'),
        ('准备上架草稿','写三个商品标题；拍规格主图；保持6枚单SKU；核对价格和售后条款。','规格表、图片、结算费用','草稿里的每项属性都有依据，费用复算一致。','仅准入确认后人工上架；不会自动提交。','PREPARE'),
        ('准备素材','手机固定机位；拍放线、取线、量尺寸；给未测试表面贴待测标记。','手机、样品、卡尺、桌面','每个主张有对应镜头；未知效果未写入字幕。','同一条件拍摄，禁止伪造对比。','PREPARE'),
        ('制作首批笔记','选痛点、教程、适配筛选三个角度；每篇只测试一个主要问题。','三套素材、选题表','三篇有不同目的，标题不承诺未测效果。','不把拍摄计划写成亲测经历。','PREPARE'),
        ('发布小规模测试','确认三门仍通过；人工发布首篇，再安排其余两篇；逐篇记录发布时间与可见指标。','准入核验、笔记稿、数据表','每篇有ID和统计口径；不可见指标留空。','不为凑日程越过核验门。','PUBLISH'),
        ('第一次复盘','按相同观察窗口对照三种角度；检查咨询中的适配问题；核对订单贡献利润。','数据表、实际结算、咨询原话','选出下轮只改变的一个变量；无订单不虚算转化。','数据量不足时写未定，不判断失败。','REVIEW')]
    for i,row in enumerate(daily,1):
        days.append(dict(zip(('goal','steps','materials','done','caution','action'),row),day=i,evidence_ids=[],
            blocked_steps=['列出缺失的费用、资质、履约与样品项，向对应来源核实，暂停采购库存。','根据已知用途列人群与场景假设，只整理访谈问题。','制作属性核对清单；不提交上架，逐项标出待核实字段。','准备样品测试方案；若无样品，记录未测试，不编拍摄结果。','仅保留选题草稿，把所有效果句改为待测试问题。','检查阻塞项是否已解决；未解决继续暂停上架及带货发布。','汇总证据缺口与已花预算，决定缩减、继续核验或停止。'][i-1],
            blocked_done='形成可追溯的核验记录；未解决项有负责人/来源，不发生上架及带货发布。'))
    phases=[]
    for period,goal,steps,done,action in [
        ('1-7','准备与验证','执行首周清单；先核对费用与三道风险门，再安排内容。','核验通过或明确暂停原因；草稿和素材可追溯。','VERIFY'),
        ('8-14','内容测试','沿用首周角度，每轮只改变场景、标题或封面中的一个变量，记录同窗口数据。','每篇记录角度、变量、观察窗口及实际可见数据。','PUBLISH'),
        ('15-21','优化迭代','按自身内容对照选择一个方向；核查适配类咨询；实际订单重算贡献利润。','保留选择理由与反例，未获得足够数据则继续观察而非断言有效。','REVIEW'),
        ('22-30','阶段决策','比较实际支出与预算；检查退款损耗；依据证据决定继续、改价或停止。','输出继续/调整/停止及原因；未验证的市场假设保持未验证。','REVIEW')]:
        phases.append({'period':period,'goal':goal,'steps':steps,'materials':'核验清单、数据表、订单结算、预算记录','done':done,'caution':'无统一成功点击率，不承诺周期内出单。','action':action,'evidence_ids':[],
            'blocked_steps':'只补齐成本、准入、履约与样品证据，复查预算；不投入带货发布或库存。', 'blocked_done':'阻塞项有新证据则重新诊断；无证据则维持暂停，记录停止/继续核验理由。'})
    strategy={'positioning':c('以适配说明清楚的桌面线头整理配件为定位假设；没有独家功能证据，不宣称优于全部竞品。'),
        'pricing':c('19.9元为演示实收假设。实际定价先核对平台结算、优惠承担与七项费用，再比较用户提供的同规格价格。'),
        'stop_rule':c('达到用户确认的可承受损失上限即暂停新增投入；出现安全/准入/履约阻塞立即暂停；实际单笔贡献持续非正时先重算与整改。无足够数据不因阅读少直接判失败。'),
        'review_rule':c('按同一观察窗口对比自己的不同角度；分开记录曝光、阅读、点击、咨询与真实订单。有效订单样本不足时不估转化率；下一轮只变一个因素。'),
        'scenes':[{'name':name,'pain':pain,'selling_point':'6枚单孔样品，具体线径和表面适配需实测','expression':expression,'evidence_ids':['P']} for name,pain,expression in [('办公桌充电区','拔线后线头滑落','近景记录放线取线'),('宿舍小桌面','线材与书本争位置','俯拍布局，先量空间'),('床头充电位','取线距离与材质不确定','先做线长和表面适配检查')]],
        'plays':[{'name':name,'why':why,'audience':'有对应场景并愿意先确认适配的人','demonstration':demo,'materials':'手机、实际样品、目标线材、尺子','risk':'未经测量不写全适配；未做长期测试不写永不掉落','evidence_ids':['P']} for name,why,demo in [('场景种草型','问题和动作能同框展示','拍线头滑落与放置动作，描述观察而非夸大效果'),('实用教程型','降低使用步骤的不确定性','拍量尺寸、放线和取线顺序'),('功能演示型','孔位细节可实际检查','卡尺量孔径，记录适配与不适配样本')]],
        'topics':topics,'days':days,'phases':phases,
        'listing':{'titles':['硅胶桌面理线夹 6枚装 单孔线材整理配件','桌面线头整理夹 硅胶6枚装','单孔理线夹 6枚装 桌面线材配件'],
            'hero':'浅色背景斜放6枚实物；旁放尺子显示真实尺寸，避免比例误导。','sku':'先做已确认的6枚单规格，不建议未核算的新套餐。买二送一时进货按实际发出三份算，收入按两份扣优惠算。',
            'detail_order':'购买理由假设→使用场景→已确认特点→实际规格→放取方法→适配边界→真实发货与售后条款。',
            'prohibited':'不写永不掉落、所有桌面通用、无痕无残胶、销量第一或伪造亲测。'}}
    return {'schema_version':'1.0','mode':'deep','demo':True,'evidence':ev,
        'product':{'name':'桌面理线夹 · 原创虚构演示','fields':{'category':c('普通桌面收纳配件','FACT',['P']),'use':c('整理单根线材的放置位置','FACT',['P']),'规格':c('6枚装，硅胶，单孔','FACT',['P']),'适配':c('线径、表面材质及长期残胶情况待核实','UNKNOWN')}},
        'summary':summary,'dimensions':dimensions,'gates':{k:{'status':'PASS','reason':reason,'evidence_ids':ids} for k,reason,ids in [('compliance','仅演示：假设已核验当前规则和商品材料；不代表真实平台准入',['R']),('fulfillment','演示供应商可单件发货并有售后地址',['F']),('sample','演示放线取线可完成；长期效果未验证，不承诺',['F'])]},
        'budget':{'max_loss':200,'planned_spend':120,'evidence_ids':['C']},'scenarios':scenarios,'price_tests':[16.9,19.9,22.9],
        'questions':[],'strategy':strategy}

def variants():
    a=case(); b=copy.deepcopy(a); b['dimensions']['competition'].update(level=None,missing=['缺少真实竞品对照材料'],evidence_ids=[])
    b['evidence']=[e for e in b['evidence'] if e['id']!='M']
    b['summary']['reason']=c('缺少竞品对照，暂不判断竞争优势；可在已核验的演示经营条件下谨慎测试。','INFERENCE',['C','F'])
    d=copy.deepcopy(b)
    for s in d['scenarios'].values(): s['costs']['purchase']={'value':None,'kind':'UNKNOWN','evidence_ids':[]}
    d['dimensions']['profit'].update(level=None,missing=['进货成本未知'])
    d['gates']['compliance']={'status':'UNKNOWN','reason':'需要查询当前官方规则；未获取到可核验的准入资料','evidence_ids':[]}
    d['questions']=['这件商品每单实际进货成本和实收售价是多少？','能提供当前类目准入与供应商履约资料吗？']
    d['summary']['reason']=c('进货成本和当前准入证据缺失，完整利润未知，暂缓经营决策。','UNKNOWN')
    d['summary']['advantages'][2]=c('费用未齐，利润优势无法确认。','UNKNOWN')
    negative=copy.deepcopy(a); negative['product']['name']='理线夹低价包邮方案 · 虚构负利润演示'
    for s in negative['scenarios'].values(): s['costs']['revenue']['value']=5
    negative['summary']['reason']=c('实收5元不足以覆盖进货和履约等成本，当前方案暂不推荐。','INFERENCE',['C'])
    negative['summary']['direction']=c('先核对成本和实收口径，停止当前低价包邮方案。')
    for e in negative['evidence']:
        if e['id']=='C': e['excerpt']=e['excerpt'].replace('19.9','5')
    quick=copy.deepcopy(d); quick['mode']='quick'; quick.pop('strategy')
    return {'positive':a,'cautious':b,'incomplete':d,'negative':negative,'quick':quick}

def screenshot_case():
    # Authored after actually viewing the original synthetic product-card.png.
    d=variants()['quick']; d['product']={'name':'截图中的桌面理线夹 · 初步诊断','image':'../media/product-card.png','fields':{
        'category':c('桌面理线收纳配件','INFERENCE',['IMG']), 'use':c('资料卡写明用于整理线材','FACT',['IMG']),
        '规格':c('资料卡写明6枚装、硅胶、单孔；不是独立材质检测','FACT',['IMG']),
        '成本售价':c('图片未提供','UNKNOWN'), '资质':c('图片未提供','UNKNOWN')}}
    d['evidence']=[{'id':'IMG','type':'IMAGE','source':'原创合成商品资料卡，宿主实际查看','excerpt':'图中文字：桌面理线夹6枚装；硅胶；单孔；用于整理线材；进货成本、售价、孔径、资质未提供；长期牢固、无残胶未测试。'}]
    for k,dim in d['dimensions'].items():
        dim.update(level=None,basis='仅有商品资料图，不能从中确认经营条件',positive=['可识别商品大致用途'],negative=['没有真实经营与市场验证'],missing=['缺少本维关键证据'],improvement='先补齐与本维相关的真实资料',evidence_ids=['IMG'])
    d['dimensions']['content'].update(level=2,basis='图中单孔与放线任务可以设计细节展示，实际效果未知',missing=[])
    for s in d['scenarios'].values():
        s['basis']='图片没有成本与收入信息，保留未知，不创建利润假设'
        for key in s['costs']: s['costs'][key]={'value':None,'kind':'UNKNOWN','evidence_ids':[]}
    for g in d['gates'].values(): g.update(status='UNKNOWN',reason='单张图不足以核验；准入需要查询当前官方规则',evidence_ids=[])
    d['budget']={'max_loss':None,'planned_spend':None,'evidence_ids':[]}; d['price_tests']=[]
    d['summary']={'reason':c('目前只能做初步分析；成本、资质与履约未确认，暂缓经营决策。','UNKNOWN'),
        'biggest_risk':c('无法从图片判断适配和长期残胶效果。','INFERENCE',['IMG']),
        'direction':c('先观察桌面拔线后线头位置，验证整理需求。'),
        'audience':c('经常在桌面取放充电线且需要固定线头位置的人，真实需求待访谈。'),
        'angle':c('先做孔位与线径适配检查，待样品可用后拍放取步骤。'),
        'advantages':[c('资料卡写明6枚装。','FACT',['IMG']),c('外观可用于解释单孔放线方式。','INFERENCE',['IMG']),c('尚不能确认利润或市场优势。','UNKNOWN')],
        'risks':[c('成本售价未知。','UNKNOWN'),c('资质履约未知。','UNKNOWN'),c('长期效果未测试。','FACT',['IMG'])],
        'actions':[c('获取每单实收、进货与其余五项费用。'),c('索要供应商履约与资质材料，对照当前官方规则。'),c('拿样测孔径、线径和目标表面，记录结果后再评估。')]}
    d['questions']=['预计每单实际售价和进货成本是多少？','能否提供供应商资质、发货与售后说明？','是否已有可供测试的样品？']
    # Image must be placed inside input directory for explicit bounded access.
    d['product']['image']='product-card.png'
    return d
