import copy
import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from engine import assess,validate,economics,return_loss,order_revenue,ValidationError,effective_plan
from cases import case,variants,screenshot_case

class EngineTests(unittest.TestCase):
    def test_single_screenshot_only(self):
        data=screenshot_case(); r=assess(data)
        self.assertEqual(r['decision'],'D'); self.assertIsNone(r['profits']['base']['contribution'])
        self.assertEqual(r['assessed_weight'],15); self.assertEqual(len(data['questions']),3)

    def test_four_decisions(self):
        self.assertEqual({k:assess(v)['decision'] for k,v in variants().items()},
                         {'positive':'A','cautious':'B','incomplete':'D','negative':'C','quick':'D'})

    def test_profit_arithmetic(self):
        p=economics(case()['scenarios']['base'])
        self.assertEqual(p['contribution'],8.5); self.assertEqual(p['gross'],15.9)
        self.assertEqual(p['margin'],42.71); self.assertTrue(p['assumed'])

    def test_missing_each_fee(self):
        for key in case()['scenarios']['base']['costs']:
            with self.subTest(key=key):
                data=case(); data['scenarios']['base']['costs'][key]={'value':None,'kind':'UNKNOWN','evidence_ids':[]}
                r=assess(data)
                self.assertIsNone(r['profits']['base']['contribution']); self.assertIsNone(r['scores']['profit']['level'])
                self.assertEqual(r['decision'],'D'); self.assertIsNone(r['total'])

    def test_zero_revenue(self):
        data=case(); data['scenarios']['base']['costs']['revenue']['value']=0
        r=assess(data); self.assertEqual(r['decision'],'C'); self.assertIsNone(r['profits']['base']['margin'])

    def test_nonpositive_gate_precedes_score(self):
        data=case()
        for d in data['dimensions'].values(): d['level']=4
        data['scenarios']['base']['costs']['revenue']['value']=2
        self.assertEqual(assess(data)['decision'],'C')

    def test_compliance_block(self):
        data=case(); data['gates']['compliance'].update(status='BLOCK',reason='存在严重产品安全隐患的材料，暂停核验')
        self.assertEqual(assess(data)['decision'],'C')

    def test_credentials_unknown(self):
        data=case(); data['gates']['compliance'].update(status='UNKNOWN',evidence_ids=[])
        self.assertEqual(assess(data)['decision'],'D')

    def test_no_official_pass(self):
        data=case(); data['gates']['compliance']['evidence_ids']=['P']
        with self.assertRaises(ValidationError): assess(data)

    def test_hard_fulfillment(self):
        data=case(); data['gates']['fulfillment'].update(status='BLOCK',reason='无发货能力')
        self.assertEqual(assess(data)['decision'],'C')

    def test_operations_unfit(self):
        data=case(); data['dimensions']['operations']['level']=1
        self.assertEqual(assess(data)['decision'],'C')

    def test_sample_unknown_blocks_execution(self):
        data=case(); data['gates']['sample']['status']='UNKNOWN'
        r=assess(data); self.assertEqual(r['decision'],'B'); self.assertFalse(r['publish_ready'])

    def test_missing_competitors_not_full_score(self):
        r=assess(variants()['cautious']); self.assertIsNone(r['total']); self.assertEqual(r['assessed_weight'],85)

    def test_partial_is_not_normalized(self):
        data=case(); data['dimensions']['competition'].update(level=None,evidence_ids=[],missing=['缺少样本'])
        r=assess(data); self.assertEqual(r['subtotal'],68.75); self.assertIsNone(r['total'])

    def test_budget_over(self):
        data=case(); data['budget']['planned_spend']=201
        self.assertEqual(assess(data)['decision'],'C')

    def test_budget_missing(self):
        data=case(); data['budget']['max_loss']=None
        self.assertEqual(assess(data)['decision'],'B')

    def test_conservative_negative(self):
        data=case(); data['scenarios']['conservative']['costs']['acquisition']['value']=30
        self.assertEqual(assess(data)['decision'],'B')

    def test_bundle_coupon(self):
        self.assertEqual(order_revenue(10,2,3),17)
        # Buy two, gift one: procurement is for THREE, revenue only for two.
        data=case(); s=data['scenarios']['base']; s['costs']['revenue']['value']=order_revenue(10,2,3)
        s['costs']['purchase']['value']=4*3
        self.assertEqual(economics(s)['contribution'],-2.4)

    def test_return_expected_loss(self):
        self.assertEqual(return_loss(.1,15),1.5)
        with self.assertRaises(ValidationError): return_loss(1.1,15)

    def test_bad_numbers(self):
        for value in [True,-1,'NaN','Infinity','not a number']:
            with self.subTest(value=value):
                data=case(); data['scenarios']['base']['costs']['revenue']['value']=value
                with self.assertRaises(ValidationError): assess(data)

    def test_references(self):
        data=case(); data['summary']['reason']['evidence_ids']=['absent']
        with self.assertRaises(ValidationError): validate(data)

    def test_fact_requires_source(self):
        data=case(); data['summary']['reason'].update(kind='FACT',evidence_ids=[])
        with self.assertRaises(ValidationError): validate(data)

    def test_real_rejects_demo_evidence(self):
        data=case(); data['demo']=False
        with self.assertRaises(ValidationError): validate(data)

    def test_missing_level(self):
        data=case(); data['dimensions']['content']['missing']=['没有图片或实测']
        with self.assertRaises(ValidationError): validate(data)

    def test_unknown_product(self):
        data=case(); data['product']['fields']['use']['kind']='UNKNOWN'
        self.assertEqual(assess(data)['decision'],'D')

    def test_questions_max_three(self):
        data=case(); data['questions']=['问题']*4
        with self.assertRaises(ValidationError): validate(data)

    def test_duplicate_topics(self):
        for key in ['title','angle','purpose']:
            with self.subTest(key=key):
                data=case(); data['strategy']['topics'][1][key]=data['strategy']['topics'][0][key]
                with self.assertRaises(ValidationError): validate(data)

    def test_missing_plan_deliverable(self):
        data=case(); data['strategy']['days'][2]['done']=''
        with self.assertRaises(ValidationError): validate(data)

    def test_days_and_periods_cover(self):
        data=case(); data['strategy']['days'][1]['day']=1
        with self.assertRaises(ValidationError): validate(data)
        data=case(); data['strategy']['phases'][-1]['period']='22-29'
        with self.assertRaises(ValidationError): validate(data)

    def test_blocked_plan_substitution(self):
        data=variants()['negative']; result=assess(data)
        plan=effective_plan(data['strategy']['days'],result)
        self.assertEqual(plan[5]['steps'],data['strategy']['days'][5]['blocked_steps'])
        self.assertNotEqual(plan[5]['steps'],data['strategy']['days'][5]['steps'])
        self.assertIn('暂停',plan[5]['execution'])

    def test_no_data_invention(self):
        data=variants()['incomplete']; original=copy.deepcopy(data); assess(data)
        self.assertEqual(data,original)
        self.assertNotIn('sales_volume',data); self.assertNotIn('search_volume',data)

    def test_unknown_cost_nonzero_invalid(self):
        data=case(); data['scenarios']['base']['costs']['purchase']['kind']='UNKNOWN'
        with self.assertRaises(ValidationError): validate(data)

    def test_empty_scenarios_rejected(self):
        data=case(); data['scenarios']={}
        with self.assertRaises(ValidationError): validate(data)

    def test_known_costs_already_exceed_revenue(self):
        data=case(); costs=data['scenarios']['base']['costs']
        costs['revenue']['value']=399; costs['purchase']['value']=380; costs['shipping_packaging']['value']=25
        costs['platform_payment']={'value':None,'kind':'UNKNOWN','evidence_ids':[]}
        r=assess(data)
        self.assertEqual(r['decision'],'C'); self.assertIsNone(r['profits']['base']['contribution'])
        self.assertLess(r['profits']['base']['contribution_upper_bound'],0)

if __name__=='__main__': unittest.main()
