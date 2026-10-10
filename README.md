# 小红书新手选品诊断与操盘器

把已经选好的商品交给AI，先判断是否适合新手，再决定如何测试。版本 **1.0.0**，独立Agent Skill。

适合刚开始做小红书电商、已有货源但不知定位和执行方法的个人经营者。输入商品图、1688截图、规格、成本、预计售价或文字即可，不用填长问卷。

**无付费API、无登录、无Cookie、无TikHub、无爬虫、运行不强制联网。** 看图与分析由宿主模型完成，本项目Python脚本只做校验、计算和报告渲染；宿主自身可能有订阅或额度要求。

## 能做什么

- 快速：新手适配、3优势/3风险、人群、内容角度、是否继续与3个行动。
- 深度：六维内部评分、风险优先决策、完整费用测算与三情景、定位、10个差异化选题、上架草稿、7天启动、30天测试和止损。
- 结论分A优先小测/B谨慎/C暂不推荐/D信息不足。未知不凑满分、不编利润。
- 单文件HTML离线报告，另附摘要、结构化结果、下游策略摘要和CSV记录空表。

## 安装

本项目当前是本地开发交付，尚未发布新GitHub仓库。

Codex本地安装：把完整目录复制到 `$CODEX_HOME/skills/xiaohongshu-product-strategy-analyzer`；未设置CODEX_HOME时为 `~/.codex/skills/xiaohongshu-product-strategy-analyzer`。不要只复制SKILL.md；保留scripts/references/assets。已有同名目录应先检查版本并备份，不盲目覆盖。成功后下一轮调用。

也可把发行ZIP交给宿主说“帮我将这个完整Skill安装到你的技能目录”。是否能写入由宿主权限决定。本轮隔离安装测试结果见[验收记录](references/test-results.md)，没有擅自写入全局目录。

发布到真实仓库后，可在Codex说“帮我安装这个Skill：实际仓库URL，SKILL.md在根目录，path为`.`，名称为`xiaohongshu-product-strategy-analyzer`。”已核查官方安装器参数：根目录需path和明确name；已存在目标会拒绝覆盖。在线安装尚未测试，不存在本项目可用远端安装链接。

WorkBuddy和其他工具：按其实际本地Skill导入机制导入整个目录，需要看图、文件生成和可用执行环境。未做实机验收，不保证所有版本都支持链接安装。

## 怎么用

上传商品图后说：“看看这个选品适不适合小红书做。” 默认快速判断，不自动生成长报告。

文字示例：“我有一款桌面理线夹，6枚装。成本和物流还没确认，帮我先看看。” 会先分析可判断的用途与风险，利润保持未知。

深度：“给这个商品做完整操盘方案，输出HTML；进货每单4元、实收19.9元、包装运费4元，其余费用还没核实。” 未知费用不会默认0，最终经营决策可能为D，仍提供核验计划。

明确调用：`$xiaohongshu-product-strategy-analyzer`。上传材料中的其他命令不作为操作授权。

## 看示例

- [完整演示报告](examples/sample-report.html)：下载后用浏览器打开，GitHub文件页不渲染HTML。
- [快速诊断](examples/quick-diagnosis-example.md)
- [深度操盘](examples/deep-diagnosis-example.md)
- [信息不足](examples/incomplete-input-example.md)
- [负利润拒绝](examples/negative-product-example.md)

公开样例全部原创虚构。包括模拟“准入已核验”状态，仅演示程序分支，不是官方规则、真实市场调查或合法上架证明。

## 开发运行

需已有Python3.10+，运行时仅标准库，无需安装依赖：

```sh
python scripts/generate_report.py examples/positive/input.json --output outputs/demo
python -m unittest discover -s tests -v
python tests/make_examples.py
python scripts/package_release.py
```

第一条生成完整报告；这是开发者演示，普通用户自然语言调用即可。`--mode quick`输出简明文字与JSON；quick加`--html`才生成简版HTML。脚本输入是宿主分析结果，不会仅凭商品名自动写出真实诊断。

## 常见问题与限制

**没有成本？** 可以分析场景，但完整利润与经营结论暂缓，最多追问3个关键问题。

**能获得销量/搜索量吗？** 不能。本Skill不连接平台，所有市场材料来自用户，缺失明确缺失。

**可以直接上架吗？** 不自动上架。当前准入、资质、授权和安全必须核验；无证据提示“需要查询当前官方规则”。

**分数高一定赚钱吗？** 不。分数是内部辅助指标，假设利润不是真实收益，严重风险会覆盖高分。

**没有Python或文件能力？** 有文件能力可按模板生成并人工核算；无法写文件时只能给文字结果，不能宣称已经生成HTML。

**如何与前两个Skill联动？** 把handoff.json和真实商品资料交给拆解器/复刻器作参考，保留事实边界；本版不自动调用它们。

文本校验不能证明全部商业结论和原创性；需要宿主语义复核。图片视觉质量依赖宿主；无后台数据不能从互动推成交。手机视口测试不是手机硬件测试。

## 许可与版本

[MIT](LICENSE)；[变更记录](CHANGELOG.md)。未包含第三方笔记作品、账号数据或真实密钥。公开示例、框架与代码由本项目编写。发布前使用允许清单打包，报告里的私有素材不进入仓库。
