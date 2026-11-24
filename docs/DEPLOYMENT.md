# 部署说明 / Deployment notes

完整的中英文入门说明见 [中文 README](../README.zh-CN.md) 和 [English README](../README.md)。本文补充环境适配细节。

## 原始环境线索

- Python 扩展文件名指向 CPython 3.5、Linux aarch64；原构建目录也使用 `linux-aarch64-3.5`。
- PaddleLite 包元数据说明其面向 EdgeBoard。代码在 `PaddleLitePredictor.load()` 中声明 FPGA FP16 / NHWC、Host Float、ARM Float 执行位置。
- 项目没有记录完整 SDK 版本、FPGA 镜像版本及 Python 依赖版本，因此不能保证任意 ARM64 板卡或现代 Python 环境可直接复现。
- `PaddlePaddlePredictor` 使用旧 `paddle.fluid` API，是保留接口；主巡航与检测代码实际实例化 `PaddleLitePredictor`。

The extension and old build paths indicate CPython 3.5 on Linux aarch64. Package metadata mentions EdgeBoard, and inference configuration declares FPGA, Host, and ARM places. Exact SDK, FPGA image, and Python dependency versions are not recorded. The legacy `paddle.fluid` wrapper is preserved, while the navigation and detection modules instantiate the PaddleLite wrapper.

## 设备与参数

| 项目 / Setting | 位置 / Location | 当前默认值 / Current default |
| --- | --- | --- |
| 前置摄像头 / Front camera | `src/config.py` | `/dev/video0` |
| 侧置摄像头 / Side camera | `src/config.py` | `/dev/video1` |
| 分辨率 / Capture resolution | `src/camera.py` | 640 × 480 |
| 控制器 / Controller | `src/config.py` | `mc601` |
| 串口 / Serial device | `src/serial_port.py`, `src/cart.py` | `/dev/ttyUSB0` |
| 波特率 / Baud | 同上 / Same files | `mc601`: 380400; `wobot`: 115200 |
| 模型根目录 / Model root | `src/config.py` | 仓库根目录 / Repository root |
| 保存路径 / Capture paths | 各采集与历史脚本 / Capture and legacy scripts | 多处为 `/run/media/sda1/...` |

380400 是原始代码的值，本次整理未将其改为其他常见波特率。串口设备在两个模块中分别打开，保持了原始实现；如有串口竞争，应结合控制板协议检查。

The value 380400 is preserved exactly. Two modules open the serial device separately, following the original implementation; investigate device contention against the controller protocol if necessary.

## 模型目录迁移

默认通过 `src/config.py` 所在位置解析仓库根目录。`SMARTCAR_MODEL_ROOT` 的值应是包含 `models/` 的父目录，支持 `~`，相对值则以进程启动目录解析。

```bash
export SMARTCAR_MODEL_ROOT=/opt/smartcar
# Example file: /opt/smartcar/models/sign_off/model
```

The override points to the parent of `models/`, not `models/` itself. Without it, models resolve relative to this checkout.

## PaddleLite 运行库

```text
third_party/runtime/paddlelite.cpython-35m-aarch64-linux-gnu.so
third_party/paddlelite/lib/libpaddle_full_api_shared.so
```

统一启动器提供 Python 模块搜索路径；共享库搜索路径仍需在启动 Python 之前设置：

```bash
export LD_LIBRARY_PATH="$PWD/third_party/paddlelite/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
python3 tools/run.py src/final.py
```

The launcher supplies the Python module path. Set `LD_LIBRARY_PATH` before starting Python so the dynamic linker can locate the SDK library and keep any existing SDK paths.

如需从绑定源码重新构建，请在匹配的板卡工具链中执行：

```bash
PYTHON=python3 bash scripts/build_paddlelite.sh
```

脚本在 `third_party/paddlelite/` 内执行 `setup.py build_ext --inplace`，并将生成的扩展复制到 `third_party/runtime/`。它不会下载 SDK、替换板卡库或修复 ABI 不兼容。本次仅检查了脚本语法，未进行板卡编译。

The helper builds the preserved bindings in place and copies the extension into the runtime directory. It does not obtain an SDK or resolve ABI incompatibilities. Only its syntax has been checked; a board build has not been performed.

## 历史工具

- 使用 `python3 tools/run.py <仓库内脚本路径>` 启动已移动脚本，脚本参数可继续附在后面。
- `tools/data/collect.py`、`new_collect.py` 依赖损坏的原 `joystick.py` 中的 `JoyStick`，需恢复源码后使用。
- `tools/validation/` 是保留的历史模型验证脚本，需要实际图片数据、对应模型及输出目录；不是自动化测试套件。
- `image/`、`test/` 仅保留目录占位，当前没有示例图像、训练数据或验证数据。
- 不要以导入所有模块的方式检查依赖；`serial_port.py`、`tasks.py` 和主流程存在导入期硬件初始化。

Run moved scripts through `tools/run.py`. Capture scripts need the damaged joystick module restored. Validation tools require real datasets, model mappings, and output directories; they are not an automated test suite. Avoid importing every module to inspect dependencies, because some modules initialize hardware during import.
