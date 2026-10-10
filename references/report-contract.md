# JSON契约 1.0（宿主内部使用）

最小完整结构见examples/quick/input.json；深度见examples/positive/input.json。示例全部虚构，真实输入必须demo=false并替换全部证据与内容。数值不自动补默认。

- schema_version="1.0"、mode="quick"/"deep"、demo布尔。
- evidence列表：id仅字母数字短横下划线，type=USER/IMAGE/OFFICIAL/SAMPLE，source来源名称，excerpt实际摘录。OFFICIAL额外url和checked_at。引用必须存在，id不重复。
- Claim={text非空,kind:FACT/INFERENCE/HYPOTHESIS/UNKNOWN,evidence_ids:[]}。FACT必须有证据；HYPOTHESIS可以无证据但只能表达待验证事项。脚本不证明语义正确。
- product={name,fields:{字段名:Claim},image?:相对输入JSON目录的PNG/JPEG/WebP路径}。category/use用于决策，二者未知触发D。其他商品字段按实际材料填未知或来源。
- summary：reason/biggest_risk/direction/audience/angle为Claim；advantages/risks/actions各3个Claim。questions最多3条文字。
- dimensions必须含demand/profit/operations/content/competition/risk；每项level:0..4或null，basis文字，positive/negative/missing文字列表，improvement文字，evidence_ids。missing表示关键缺项，有缺项则level必须null。利润等级最终由完整情景算式覆盖。
- gates包含compliance/fulfillment/sample；每项status=PASS/UNKNOWN/BLOCK、reason、evidence_ids。准入PASS须引用OFFICIAL日期来源，不等于脚本鉴真。
- budget={max_loss:数字或null,planned_spend:数字或null,evidence_ids:[]}。
- scenarios恰含optimistic/base/conservative，每个有basis和costs；costs恰含七项（见利润框架），各项value/kind/evidence_ids。缺值用null+UNKNOWN。price_tests可选售价数字列表。
- deep还需strategy：positioning/pricing/stop_rule/review_rule是Claim；scenes3项(name,pain,selling_point,expression,evidence_ids)；plays3项(name,why,audience,demonstration,materials,risk,evidence_ids)；topics10项(name,title,pain,angle,cover,structure,placement,purpose,evidence_ids)。
- strategy.listing：titles3个字符串、hero、sku、detail_order、prohibited文字。
- strategy.days7项：day1..7、goal/steps/materials/done/caution、action、blocked_steps/blocked_done、evidence_ids。
- strategy.phases4项：period顺序1-7/8-14/15-21/22-30，其他字段同days但无day。

quick不要求strategy，默认只输出summary.md/result.json/handoff.json；--html额外简报。deep固定输出完整HTML、以上JSON/摘要和空表头data-record.csv。result.json保存computed及门控后的计划；handoff保留商品和来源，不带本地图片路径。HTML只是本地报告，无任何外部自动提交。

每次输出新目录。JSON解析/验证失败退出码1，不生成成功报告。输入文件过大或损坏由宿主处理。证据URL只显示文本，不自动加载；报告中的用户文字全部转义。用户自己的资料仅存在其授权的本地输出目录，不加入examples或公开包。
