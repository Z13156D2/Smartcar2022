# 第三方组件 / Third-party components

| 目录 / Directory | 内容 / Contents |
| --- | --- |
| `paddlelite/src/` | 原项目提供的 PaddleLite Python 绑定 / Original PaddleLite Python bindings |
| `paddlelite/include/` | PaddleLite API 头文件 / API headers |
| `paddlelite/lib/` | `libpaddle_full_api_shared.so` 板卡共享库 / Board runtime library |
| `paddlelite/pybind11/` | 随项目提供的 pybind11 源码 / Bundled pybind11 sources |
| `runtime/` | CPython 3.5、Linux aarch64 的预编译扩展 / Prebuilt extension |

原有第三方源文件和版权头保持不变。PaddleLite 绑定源文件带有 PaddlePaddle Authors 的 Apache-2.0 声明，pybind11 的许可证保留在 [`paddlelite/pybind11/LICENSE`](paddlelite/pybind11/LICENSE)。板卡共享库来自原项目，当前快照未单独记录其 SDK 版本和二进制许可说明；再分发时需核对原供应商条款。

Original third-party source files and copyright headers are unchanged. The PaddleLite binding sources carry PaddlePaddle Authors' Apache-2.0 notices. The bundled pybind11 license is preserved at [`paddlelite/pybind11/LICENSE`](paddlelite/pybind11/LICENSE). The board shared library came with the original project; its exact SDK version and separate binary licensing terms were not recorded in this snapshot. Check the vendor terms when redistributing it.

原构建产物、缓存及分发包仅保存在本地 `.local/paddlelite-artifacts/`，未提交至仓库。运行所需的扩展和共享库则显式保留。

Old build intermediates and distribution packages are retained locally under the ignored `.local/paddlelite-artifacts/`. The deployment extension and shared library remain versioned.
