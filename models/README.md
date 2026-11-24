# 部署模型 / Deployment models

每个目录保留原项目导出的 `model` 网络描述和 `params` 权重文件；文件名未修改。用途依据配置映射和调用代码整理，模型训练配置及训练数据未随项目提供。

Each directory preserves the original exported network (`model`) and weights (`params`). Roles below follow the configuration and call sites. Training configurations and datasets are not included.

| 目录 / Directory | 用途 / Role | `config.py` 映射 / Mapping |
| --- | --- | --- |
| `all_new_p708_ban` | 主巡航 / Main navigation | `cruise` |
| `all_new_ban` | 场景切换巡航 / Alternate scene navigation | `cruise3` |
| `person_5` | 人物识别 / Person detection | `task_person` |
| `pur_one` | 采购物品识别 / Purchase item detection | `task_purchase` |
| `sign_off` | 路标识别 / Sign detection | `sign_new` |
| `sign_1` | 另一套路标配置 / Alternative sign configuration | `sign_new_1` |
| `task415_un_1` | 场景任务目标 / Task object detection | `task_new` |
| `trade_fyh` | 交易目标识别 / Trade target detection | `trade_two` |

未提供 / Not supplied: `all_new_p708_ban_f` (`cruise2`), `sign707` (`sign`), `ban` (`sign_ban`), `task715` (`task`).

主程序直接使用的配置包括 `cruise`、`cruise3`、`sign_new`、`task_new`、`task_person`、`task_purchase`、`trade_two`，这些模型均已提供。历史分支仍可能依赖缺失模型或旧配置字段。

The main program uses the supplied `cruise`, `cruise3`, `sign_new`, `task_new`, `task_person`, `task_purchase`, and `trade_two` mappings. Historical branches may require missing models or older configuration fields.

模型以普通 Git 二进制文件保存，当前没有 Git LFS 指针，克隆后可直接获得文件。模型能否执行仍取决于板卡 SDK、算子支持和运行库兼容性。

The actual model binaries are stored in Git, without Git LFS pointers. Execution still depends on the board SDK, operator support, and runtime compatibility.
