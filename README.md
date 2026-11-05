# SSHDB

SSHDB 提供共生固氮相关基因及候选蛋白的检索、序列与结构比对、基因组浏览和数据下载。前端使用 Vue 和 Vite，后端使用 Django 和 MySQL。

## 前端页面

路由在 [frontend/src/router/index.js](frontend/src/router/index.js) 中注册。下表的组件路径相对于 [frontend/src/views](frontend/src/views)。

| 浏览器路径 | Vue 组件 | 用途 |
| --- | --- | --- |
| `/` | `Home.vue` | 首页，提供快捷检索、代表物种、示例入口和访客分布地图。 |
| `/search` | `Index.vue` | 按基因、物种、基因组版本及类别筛选数据库中已有的候选记录。 |
| `/gene-info` | `GeneInfoPage.vue` | 按基因或物种查询关联蛋白，以表格展示，也承接首页快捷检索。 |
| `/protein/detail` | `components/ProteinDetail.vue` | 展示选中蛋白的标识、物种、结构域、氨基酸序列和可用结构。 |
| `/structure-candidate-search` | `StructureCandidateSearch.vue` | 给定查询蛋白和目标物种，按预计算蛋白向量的余弦相似度筛选候选。这个分数与下方结构叠合产生的 TM-score 含义不同。 |
| `/sequence-alignment` | `SequenceAlignment.vue` | 输入两条蛋白序列，查看 BLASTP 局部比对和 MAFFT 全长比对。 |
| `/structure-alignment` | `StructureAlignment.vue` | 上传两份结构，查看 US-align 叠合、TM-score、RMSD 和对齐片段。 |
| `/jbrowse` | `JBrowse.vue` | 选择物种和组装版本，打开内嵌基因组浏览器。基因组清单、序列和轨道依赖独立静态资源服务。 |
| `/download` | `Download.vue` | 列出并下载基因组、蛋白结构、向量、同源候选结果和固氮相关基因数据。旧地址 `/test` 会跳转到这里。 |
| `/about` | `About.vue` | 介绍数据库框架、检索与工具用法、联系方式和参考文献。 |
|  | `App.vue` | 顶部、导航栏、底部。 |

## 后端接口

[Django 总路由](backend/config/urls.py) 分发到三个模块。[api](backend/api/urls.py) 负责数据查询和文件，[search](backend/search/urls.py) 负责向量检索，[tools](backend/tools/urls.py) 负责运行比对和访客统计。每个模块的请求参数和响应字段在同目录的 `views.py` 中。

| 方法 | 路径 | 用途 |
| --- | --- | --- |
| GET | `/api/genes/unique/`、`/api/species/names/` | 分别返回去重基因名、物种及其基因组版本，用于初始化筛选框。 |
| GET | `/api/search/results/` | 按 `gene`、`species` 和基因组标识 `conservatory_genome_name` 查询已有记录，可再用 `category` 筛选。 |
| GET | `/api/protein/info/` | 按 `gene_id` 或 `organism` 获取蛋白注释列表。 |
| GET | `/api/protein/sequence/` | 按 `protein_id` 返回氨基酸序列及可用 CIF 文件信息。 |
| GET | `/api/protein/cif/files/`、`/api/protein/cif/` | 前者列结构文件，后者按文件名或蛋白 ID 取 CIF 文件。 |
| GET | `/api/{genome,npy,homology,snf}/files/`、`/api/{genome,npy,homology,snf}/file/` | 花括号代表四组实际路径。分别对应基因组及注释、蛋白向量及元数据、同源候选结果、固氮相关基因。复数路径列文件，单数路径取文件。 |
| GET | `/search/protein-example/` | 按 `query_species` 获取一个可用于向量检索的示例蛋白。 |
| GET | `/search/protein-embedding/` | 根据 `protein_id` 和 `target_species` 检索目标物种的向量，可指定查询物种和相似度区间。 |
| POST | `/tools/sequence/align/` | JSON 提交 `sequence1` 和 `sequence2`，返回 BLASTP 与 MAFFT 的比对结果。 |
| POST | `/tools/structure/align/` | 表单上传 `file1` 和 `file2`，返回 US-align 指标和叠合文件地址。 |
| POST | `/tools/visitors/track/` | 成功切换页面后记录访问事件，用于汇总访问次数和估算独立访客数。 |
| GET | `/tools/visitors/stats/` | 按时间段返回浏览量、按访客标识去重的数量及国家分布，供首页地图使用。 |

`/admin/` 是 Django 管理入口。开发环境中，`/media/` 用于读取比对输出。`/search` 本身是前端页面，开发代理仅将上述两个 `/search/protein-…/` 接口转发到 Django。代理配置见 [frontend/vite.config.js](frontend/vite.config.js)。

## 运行所需的本地资源

- 启动 Django 前，设置环境变量 `DJANGO_SECRET_KEY` 和 `SSHDB_DB_PASSWORD`，或在本机的 `backend/config/settings.local.json` 中用这两个键填写配置。该文件已列入 Git 忽略规则。
- 数据查询依赖已有 MySQL 业务表。访客统计还依赖 `visitor_event` 表，其 Django 模型设置了 `managed = False`，普通迁移不会创建它。按国家展示访问量需要 GeoIP 数据及读取库，见 [GeoIP 配置说明](backend/geoip/README.md)。
- 启用比对和下载前，请核对 [backend/config/settings.py](backend/config/settings.py) 中 BLASTP、MAFFT、US-align 和各类数据文件的实际路径。JBrowse 静态服务需支持 HTTP Range，以读取已建索引的基因组文件。
