# 可复现测试

运行 `python -m unittest discover -s tests -v`。stdlib核心测试覆盖四决策、完整/缺失费用、负利润上限、预算/履约/资质/样品拦截、评分缺项、证据、选题重复、计划字段和分期、JSON门控、HTML转义、快速无HTML、打包排除与密钥模式。

`python tests/make_examples.py` 生成A/B/C/D和quick，以及已有媒体条件下的单截图报告。正常运行不需要Pillow；可选开发工具make_demo_media.py重绘原创资料卡，依赖Pillow和本机中文字体，不是运行时OCR或视觉引擎。

`node tests/browser_check.cjs --browser <本机浏览器可执行文件>` 用Playwright在全新离线上下文测试本地文件，不操作用户会话。需开发环境已有Playwright与浏览器；不把这作为普通用户安装要求。检查14个section加首页决策、中文、响应式、图片解码、证据跳转、打印PDF及恶意文本非执行。

`python tests/verify_installer.py --installer <宿主官方安装器路径> --package <发行ZIP>` 只将实际官方安装器HTTP返回替换为本地ZIP，验证解析根路径、复制资源、安装后渲染、重名拒绝；不是线上下载。

语义验收：人工对照十个选题的问题/叙事/测试目的；查看7天和30天的动作、材料、完成标准及风险降级。独立前向测试不读取样例答案，真实产出回复与quick JSON，运行后对照结论。详见[实际状态](../references/test-results.md)。
