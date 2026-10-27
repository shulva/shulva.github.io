# 本地修复校验

不修改发布状态的默认预览（不选文件时不处理任何笔记）：

```sh
python3 scripts/repair_metadata.py
python3 scripts/repair_metadata.py --file 'zk/zk/1-ZK/1 (ZK).md'
python3 scripts/repair_metadata.py --allowlist selected-notes.txt
```

allowlist 每行是相对 `_notes` 的一个文件。只有显式 `--write` 才写入；本次没有对真实笔记执行写入。新增 front matter 带 `published: false` 和 `feed: hide`，避免主题默认 feed:show 自动公开。显式否定标记整篇跳过。已有 YAML 除已知 title:zk/feed:show 的空格与缺失 title 外保留，正文按原 UTF-8 字节保留。确认发布范围后再人工审阅发布标记。

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests
node tests/serialization.cjs
python3 scripts/check_notes_assets.py --output ../repair-logs/inventory.json
```

清点为保守源码分析，不代替构建后链接检查。缺失附件是仓库原有引用，不能据此确定附件是否私人或应公开；不下载或生成附件。wiki alias/fragment 被识别，重复 basename 不保证唯一解析。JS 转义测试执行 Node 与 Ruby 标准库 JSON 契约，覆盖引号、反斜线、换行和 script 结束标签；没有安装 Liquid，完整模板渲染仍须 Jekyll 构建验证。

当前实际构建命令（从 repo）：

```sh
BUNDLE_PATH="$PWD/vendor/bundle" BUNDLE_FROZEN=true bundle _2.4.22_ exec jekyll build --destination "$PWD/../repair-build"
```

本机 Ruby 2.6.10、Node 23.11.0；仅 Bundler 1.17.2，没有 Liquid/Jekyll，实际构建因缺 Bundler 2.4.22 失败。Gemfile/锁文件保持原样。锁定主要依赖 Jekyll 4.0.1、jekyll-feed 0.15.1、jekyll-tidy 0.2.2、jekyll-sitemap 1.4.0、kramdown-math-katex 1.0.1、webrick 1.7.0；原生依赖 sassc 2.4.0、ffi 1.15.1（需要已有编译工具）。完整精确依赖见 Gemfile.lock。

父普通 shell 在 repo 运行的下一条命令（联网下载公开依赖，全部安装到 workspace；本次未运行）：

```sh
env GEM_HOME="$PWD/../repair-gems" GEM_PATH="$PWD/../repair-gems" BUNDLE_PATH="$PWD/vendor/bundle" BUNDLE_FROZEN=true /bin/sh -c '/usr/bin/gem install --no-document bundler -v 2.4.22 && /usr/bin/ruby "$GEM_HOME/bin/bundle" _2.4.22_ install && /usr/bin/ruby "$GEM_HOME/bin/bundle" _2.4.22_ exec jekyll build --destination "$PWD/../repair-build"'
```

若原生编译或系统 Ruby 不兼容，应保留失败日志后由父提供公开 runtime；不要全局安装、改锁文件或运行未知安装脚本。生产上线仍由父处理。
