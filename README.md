# SSHDB

SSHDB 提供共生固氮相关基因及候选蛋白的检索、序列与结构比对、基因组浏览和数据下载。前端使用 Vue 和 Vite，后端使用 Django 和 MySQL。

## 前端页面

路由在 [frontend/src/router/index.js](frontend/src/router/index.js) 中注册。下表的组件路径相对于 [frontend/src/views](frontend/src/views)。

| 浏览器路径 | Vue 组件 | 用途 |
| --- | --- | --- |
| `/` | `Home.vue、components/VisitorMap.vue` | 首页，提供快捷检索、代表物种、示例入口和访客分布地图。 |
| `/search` | `Index.vue` | 按基因、物种、基因组版本及ABC类别筛选。 |
| `/gene-info` | `GeneInfoPage.vue、components/GeneSearch.vue、components/GeneTable.vue` | 按基因或物种查询关联蛋白，以表格展示，也承接首页快捷检索。 |
| `/protein/detail` | `components/ProteinDetail.vue、components/ProteinSequencePanel.vue` | 展示选中蛋白的标识、物种、结构域、氨基酸序列和3D结构。 |
| `/structure-candidate-search` | `StructureCandidateSearch.vue` | 给定查询蛋白和目标物种，按预计算蛋白向量的余弦相似度筛选候选。 |
| `/sequence-alignment` | `SequenceAlignment.vue` | 输入两条蛋白序列，查看 BLASTP 局部比对和 MAFFT 全长比对。 |
| `/structure-alignment` | `StructureAlignment.vue` | 上传两份结构，查看 US-align 叠合、TM-score、RMSD 和对齐片段。 |
| `/jbrowse` | `JBrowse.vue` | 选择物种和组装版本，打开基因组浏览器。 |
| `/download` | `Download.vue` | 列出并下载基因组、蛋白结构、向量、同源候选结果和固氮相关基因数据。 |
| `/about` | `About.vue` | 介绍数据库框架、检索与工具用法、联系方式和参考文献。 |
|  | `App.vue` | 顶部、导航栏、底部。 |

## 后端接口

请求先由 [backend/config/urls.py](backend/config/urls.py) 分发到 `api`、`search` 和 `tools` 三个模块。下面按功能列出接口、后端处理入口以及实际调用它的前端页面。文件链接均可直接打开对应源码。

### 数据查询与下载

路由注册在 [backend/api/urls.py](backend/api/urls.py)。下表的处理类均位于 [backend/api/views.py](backend/api/views.py)，查询使用的数据模型位于 [backend/api/models.py](backend/api/models.py)。

| 方法与接口路径 | 后端处理类 | 对应前端页面与调用文件 | 作用 |
| --- | --- | --- | --- |
| GET `/api/genes/unique/` | `GeneUniqueListAPIView` | `/search` 的 [Index.vue](frontend/src/views/Index.vue)，以及 `/gene-info` 内的 [GeneSearch.vue](frontend/src/views/components/GeneSearch.vue) | 返回去重基因名，填充基因选择框。 |
| GET `/api/species/names/` | `SpeciesGenomeVersionListAPIView` | `/search` 的 [Index.vue](frontend/src/views/Index.vue)，以及 `/structure-candidate-search` 的 [StructureCandidateSearch.vue](frontend/src/views/StructureCandidateSearch.vue) | 返回物种、科及基因组版本，填充物种与版本选择框。 |
| GET `/api/search/results/` | `SearchResultAPIView` | `/search` 的 [Index.vue](frontend/src/views/Index.vue) | 按 `gene`、`species`、`conservatory_genome_name` 和可选 `category` 筛选已有候选记录。 |
| GET `/api/protein/info/` | `ProteinInfoAPIView` | `/gene-info` 的 [GeneInfoPage.vue](frontend/src/views/GeneInfoPage.vue) 发起请求，由 [GeneTable.vue](frontend/src/views/components/GeneTable.vue) 展示结果 | 按 `gene_id` 或 `organism` 查询蛋白注释列表，也承接首页快捷检索跳转。 |
| GET `/api/protein/sequence/` | `ProteinSequenceAPIView` | `/protein/detail` 的 [ProteinDetail.vue](frontend/src/views/components/ProteinDetail.vue) 发起请求，将数据传给 [ProteinSequencePanel.vue](frontend/src/views/components/ProteinSequencePanel.vue) | 按 `protein_id` 返回氨基酸序列及可用 CIF 文件信息。 |
| GET `/api/protein/cif/files/` | `ProteinCifFileListAPIView` | `/download` 的 [Download.vue](frontend/src/views/Download.vue) | 列出可下载的蛋白结构文件。 |
| GET `/api/protein/cif/` | `ProteinCifFileAPIView` | `/protein/detail` 内的 [ProteinSequencePanel.vue](frontend/src/views/components/ProteinSequencePanel.vue)，以及 `/download` 的 [Download.vue](frontend/src/views/Download.vue) | 按蛋白 ID 或文件名读取 CIF，用于结构展示或下载。 |
| GET `/api/genome/files/`、`/api/genome/file/` | `GenomeResourceListAPIView`、`GenomeResourceFileAPIView` | `/download` 的 [Download.vue](frontend/src/views/Download.vue) | 分别列出和下载基因组序列及注释资源。 |
| GET `/api/npy/files/`、`/api/npy/file/` | `NpyResourceListAPIView`、`NpyResourceFileAPIView` | `/download` 的 [Download.vue](frontend/src/views/Download.vue) | 分别列出和下载蛋白向量及其元数据。 |
| GET `/api/homology/files/`、`/api/homology/file/` | `HomologyResourceListAPIView`、`HomologyResourceFileAPIView` | `/download` 的 [Download.vue](frontend/src/views/Download.vue) | 分别列出和下载同源候选结果文件。 |
| GET `/api/snf/files/`、`/api/snf/file/` | `SnfResourceListAPIView`、`SnfResourceFileAPIView` | `/download` 的 [Download.vue](frontend/src/views/Download.vue) | 分别列出和下载固氮相关基因数据。 |

下载页先请求各个 `files/` 列表接口，再用响应中的文件 URL 发起下载。蛋白详情页则先获取序列和结构文件信息，再由 `ProteinSequencePanel.vue` 读取 CIF 并显示三维结构。

### 蛋白向量检索

路由注册在 [backend/search/urls.py](backend/search/urls.py)，请求处理类位于 [backend/search/views.py](backend/search/views.py)。

| 方法与接口路径 | 后端处理类及业务函数 | 对应前端页面与调用文件 | 作用 |
| --- | --- | --- | --- |
| GET `/search/protein-example/` | `ExampleProteinAPIView` → `get_example_protein()` | `/structure-candidate-search` 的 [StructureCandidateSearch.vue](frontend/src/views/StructureCandidateSearch.vue) | 根据 `query_species` 获取示例蛋白，供用户填入检索表单。 |
| GET `/search/protein-embedding/` | `ProteinEmbeddingSearchAPIView` → `protein_embedding_search()` | `/structure-candidate-search` 的 [StructureCandidateSearch.vue](frontend/src/views/StructureCandidateSearch.vue) | 根据 `protein_id` 和 `target_species` 检索候选，可指定 `query_species` 及相似度区间。 |

两个业务函数位于 [backend/search/services.py](backend/search/services.py)。该文件负责读取示例索引、查找查询蛋白向量、分批计算余弦相似度及筛选结果。向量表 `protein_embedding` 的模型定义在 [backend/search/models.py](backend/search/models.py)，物种信息使用 [backend/api/models.py](backend/api/models.py) 中的 `SpeciesInfo`。示例索引的路径由 `PROTEIN_EXAMPLE_JSON_PATH` 配置。

### 序列与结构比对

路由注册在 [backend/tools/urls.py](backend/tools/urls.py)，HTTP 请求处理函数位于 [backend/tools/views.py](backend/tools/views.py)。

| 方法与接口路径 | 后端处理函数及执行文件 | 对应前端页面与调用文件 | 作用 |
| --- | --- | --- | --- |
| POST `/tools/sequence/align/` | `protein_alignment_api()` → [blastp_utils.py](backend/tools/blastp_utils.py) 的 `run_combined_protein_alignment()` | `/sequence-alignment` 的 [SequenceAlignment.vue](frontend/src/views/SequenceAlignment.vue) | JSON 提交 `sequence1` 和 `sequence2`，执行 BLASTP 局部比对及 MAFFT 全长比对，返回统计和对齐结果。 |
| POST `/tools/structure/align/` | `structure_align_view()` → [structure_align_utils.py](backend/tools/structure_align_utils.py) 的 `run_usalign()` | `/structure-alignment` 的 [StructureAlignment.vue](frontend/src/views/StructureAlignment.vue) | 表单上传 `file1` 和 `file2`，执行 US-align，返回 TM-score、RMSD、对齐片段和叠合文件地址。 |

[backend/tools/structure_align_utils.py](backend/tools/structure_align_utils.py) 还负责上传结构检查、解析 US-align 输出，以及将结果保存到 `backend/media/structure_align/`。前端随后通过返回的 `/media/…` 地址加载或下载结构和结果文件。外部程序路径及运行参数在 [backend/config/settings.py](backend/config/settings.py) 中配置。

### 访客统计

这两个接口同样由 [backend/tools/urls.py](backend/tools/urls.py) 注册，并在 [backend/tools/views.py](backend/tools/views.py) 中实现。访客事件模型 `VisitorEvent` 位于 [backend/tools/models.py](backend/tools/models.py)，对应 MySQL 的 `visitor_event` 表。

| 方法与接口路径 | 后端处理函数 | 对应前端页面与调用文件 | 作用 |
| --- | --- | --- | --- |
| POST `/tools/visitors/track/` | `visitor_track_view()` | [router/index.js](frontend/src/router/index.js) 在页面成功导航后调用 [utils/visitorTracking.js](frontend/src/utils/visitorTracking.js)，覆盖前端各路由页面 | 提交访问事件和访客标识，记录页面路径、访问时间及可解析的国家信息。 |
| GET `/tools/visitors/stats/` | `visitor_stats_view()` | 首页 `/` 的 [Home.vue](frontend/src/views/Home.vue) 挂载 [VisitorMap.vue](frontend/src/views/components/VisitorMap.vue)，由后者发起请求 | 按 `period` 汇总浏览量、去重访客数及国家分布，供首页地图和统计数字展示。 |

国家识别依赖 GeoIP 数据文件和读取库，配置说明见 [backend/geoip/README.md](backend/geoip/README.md)。地图的地理边界文件位于 [frontend/public/maps/world.json](frontend/public/maps/world.json)。

### 路由和资源服务

| 路径或文件 | 对应页面及职责 |
| --- | --- |
| `/admin/` | [backend/config/urls.py](backend/config/urls.py) 注册的 Django 管理入口。 |
| `/media/…` | 供 `/structure-alignment` 页面读取比对结果。开发环境由 Django 在 `DEBUG` 开启时提供，生产部署需配置媒体文件服务。 |
| `/jbrowse-static/…` | `/jbrowse` 的 [JBrowse.vue](frontend/src/views/JBrowse.vue) 从独立静态服务读取 `genomes.json`、浏览器及基因组轨道资源。默认前缀可通过 `VITE_JBROWSE_BASE_URL` 配置。 |
| [frontend/src/utils/request.js](frontend/src/utils/request.js) | 统一创建 Axios 请求客户端，页面通过相对地址访问后端。 |
| [frontend/vite.config.js](frontend/vite.config.js) | 配置开发代理，将 `/api`、`/tools`、两个向量检索接口及 `/media` 转发到 Django，将 `/jbrowse-static` 转发到独立资源服务。前端 `/search` 页面路由由 Vue Router 处理。 |

## 运行所需的本地资源

- 这里的 (backend/config/settings.py) 中 很多软件如BLASTP、MAFFT、US-align 以及数据库连接等都是我本地的，实际以/data/sshdb/backend/config/settings.py华为云上的配置文件为主。
