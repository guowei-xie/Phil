## 项目简介

用于“Aliy助手【菲尔】”的Prompt调优工具， 从飞书多维表（Bitable）获取验证集，调用自定义推理任务（Aliy工作流）进行处理，并对结果进行样本级与标签级统计分析。程序运行后将在控制台输出概览，并把分析结果保存到 `results/analysis_YYYYMMDD_HHMMSS.xlsx`。

---

## 目录结构
```
Phil/
  main.py                # 入口脚本：拉取数据、执行处理、汇总并导出结果
  config.ini             # 运行配置（含密钥/Token，务必妥善保管）
  config.example.ini     # 配置示例（可复制为 config.ini 并填入真实值）
  requirements.txt       # Python 依赖
  logs/                  # 日志目录（滚动日志）
  results/               # 结果输出目录（Excel/CSV）
  src/
    processor.py         # 核心处理与分析逻辑
    utils/logger.py      # 日志器封装（支持文件滚动与控制台输出）
    lark/                # 与飞书/外部服务对接的封装
      base.py
      bitable.py
      aliy.py
```

---

## 环境要求
- Python 3.9+（建议 3.10 或更高）

### 创建与激活虚拟环境（Windows PowerShell）
```powershell
# 在项目根目录执行
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt
```

### 创建与激活虚拟环境（macOS / Linux bash）
```bash
# 在项目根目录执行
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip3 install -r requirements.txt
```

---

## 配置
请先复制 `config.example.ini` 为 `config.ini`，并按需填写真实配置。切勿把真实密钥提交到版本库。

`config.ini` 关键段落说明：
- [APP]
  - `appId`/`appSecret`: 应用级凭据（如需调用飞书开放能力等）。
  - `logLevel`: 应用级默认日志级别（INFO/DEBUG 等）。
- [LOGGER]
  - `logLevel`: 其他日志输出级别。
  - `logFile`: 日志文件路径，默认写入 `logs/` 下并带日期后缀（由 `utils/logger.py` 控制）。
- [DATASET]
  - `wiki`: 验证集多维表格是否位于wiki空间， True-是/False-否。
  - `appToken`、`tableId`: 验证集的飞书多维表凭据与表标识。
  - `sampleSize`: 采样数量（0 表示使用全部）。
- [Aliy]
  - `webhook`、`apiKey`: 自定义任务触发接口与密钥。

---

## 运行
```powershell
# 已激活虚拟环境且配置完成后
python main.py
```
运行过程：
1. 通过 `src.lark.bitable.LarkBitable` 拉取样本记录；
2. 逐条调用 `src.processor.process_single_case` 触发自定义任务；
3. 汇总为样本级与标签级指标（`analyze_results_by_sample`、`analyze_results_by_label`）；
4. 控制台打印概览，并写入 `results/analysis_YYYYMMDD_HHMMSS.xlsx`（含 `sheet1_samples` 与 `sheet2_labels`）。

---