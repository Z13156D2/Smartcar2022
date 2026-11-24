# 文件整理记录 / Reorganization record

## 整理原则

本次按用途建立目录，保留历史代码、参数、模型和第三方文件。没有根据文件名猜测比赛版本先后顺序，也没有删除重复的完整流程。`src/final.py` 作为主要阅读入口；它与原 `bot1.py`、`bot2.py` 的 SHA-256 相同，但原文件未提供独立的版本发布记录。

Files are grouped by function. Historical code, tuning values, models, and third-party components are preserved. Filenames are not treated as proof of version chronology. `src/final.py` is the main reading entry and is byte-identical to the original `bot1.py` and `bot2.py`; no separate release history was supplied.

## 目录映射

| 原内容 / Original contents | 当前位置 / Current location |
| --- | --- |
| `final.py` 和共用控制、视觉模块 / Shared control and vision modules | `src/` |
| `all*.py`, `bot*.py`, `meeting*.py` 等完整流程 / Integrated variants | `experiments/integrated/` |
| `cruiser_*.py`, `only_cruiser.py` | `experiments/navigation/` |
| 交易、保护、人物等任务实验 / Individual task experiments | `experiments/tasks/` |
| 硬件调试脚本，含原 `run.py` / Hardware debugging scripts | `tools/hardware/` |
| 采集、拍照与图像工具 / Capture and image tools | `tools/data/` |
| 模型验证脚本 / Model validation scripts | `tools/validation/` |
| `paddlelite/` 源码、头文件、库 / SDK sources, headers, library | `third_party/paddlelite/` |
| 根目录 PaddleLite Python 扩展 / Root-level extension | `third_party/runtime/` |
| `per.md` | `docs/legacy-performance.md` |
| 原 `config.py` 的完整副本 / Exact original configuration | `archive/config.py.original` |
| `build_lib_35.sh`, `export.sh` | `archive/scripts/*.original` |
| `joystick.py`, `jiuji.py` | `archive/corrupted/*.original` |
| 空文件 `xunjipaizhao.py` / Empty placeholder | `archive/placeholders/` |
| 旧构建、分发包与包元数据 / Old build and distribution artifacts | `.local/paddlelite-artifacts/`（忽略 / ignored） |
| GstShark 跟踪文件与 `nohup.out` / Traces and log | `.local/traces/`, `.local/logs/`（忽略 / ignored） |
| macOS `.DS_Store` 与 `._*` 元数据 / macOS metadata | `.local/metadata/`（忽略 / ignored） |

逐文件迁移清单位于 [`file-map.json`](file-map.json)，记录原路径、新路径、整理前字节数及 SHA-256。原模型文件保持原位且未改动。虚拟环境、IDE 状态和 Python 缓存仍留在本地并由 Git 忽略。

[`file-map.json`](file-map.json) records original and current paths, original byte counts, and SHA-256 hashes for relocated files. Models remain unchanged in place. The local virtual environment, IDE state, and Python caches remain on disk and are ignored by Git.

## 实际代码变更

1. `src/config.py`：将固定 `/home/root/quanguo/` 模型前缀改为根据仓库位置解析，并支持 `SMARTCAR_MODEL_ROOT`。原始内容另存于 `archive/config.py.original`。
2. 新建 `tools/run.py`：补齐脚本迁移后的模块搜索路径，统一以仓库根目录为工作目录，不导入车辆模块来展示帮助。
3. 新建 `scripts/build_paddlelite.sh`：使用新的第三方目录构建绑定，不执行原构建脚本中的递归删除。
4. 添加中英文 README、模型与部署文档、依赖清单、Git 忽略及文件属性规则。

Changes are limited to model path resolution, a launcher that preserves flat imports, a build helper for the new layout, and repository documentation/configuration. Competition behavior and tuning values have not been redesigned.

## 原始文件异常

`joystick.py`、`jiuji.py` 含空字节，无法通过 Python 语法解析。`export.sh` 也含空字节，不是有效 shell 脚本。其原始字节完整保留为 `.original` 文件，没有猜测补写缺失实现。

The original `joystick.py`, `jiuji.py`, and `export.sh` contain null bytes. Exact bytes are retained as `.original` files; missing implementations were not guessed.

## 验证范围

- 检查整理后所有项目 Python 文件的语法，并检查 Python 3.5 语法兼容性。
- 对照迁移清单校验原始文件 SHA-256；修改后的配置通过保留的原件校验。
- 检查已提供模型的 `model` / `params` 文件完整性及主流程模型配置路径。
- 检查 README 与新增文档的本地链接，确认 Git 跟踪模型、SDK 与文档，忽略环境、缓存和中间产物。
- 检查启动器帮助、参数透传、工作目录和模块路径设置，不运行车辆控制代码。
- 在支持 Bash 的本地环境中检查新构建脚本语法；未在 ARM64 板卡上构建。

Validation covers static syntax, original-file hashes, model paths, documentation links, Git inclusion/exclusion, launcher behavior, and build-script syntax. It does not establish end-to-end operation on the original hardware.
