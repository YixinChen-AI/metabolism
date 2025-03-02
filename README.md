# metabolism
Multi-organ metabolic analysis framework


---
1. 功能1：DICOM to NIfTI Conversion Tool
2. 
# DICOM to NIfTI Conversion Tool
## 功能概述
本工具提供医学影像数据(DICOM格式)的自动化批处理解决方案，支持以下核心功能：
1. **多模态转换**
   - CT/PET原始数据转为NIfTI标准格式
   - 自动识别设备制造商、扫描协议及序列描述
   - 元数据校验机制（随机采样10个文件验证一致性）
2. **PET标准化摄取值(SUV)计算**
   - 支持7种体重标准化算法：
     * 总体重(TBW)
     * 成人瘦体重(Hume/Boer/James公式)
     * 儿童瘦体重(Peter/Fusch/Boer公式)
   - 放射性药物代谢衰减补偿
   - 性别/身高自适应计算

## 环境依赖
```python
pypi中已经标记
```

## 数据集格式
```bash
输入结构：
dicom_dataset/
├─ case_001/
│  ├─ CT_series_1/
│  ├─ CT_series_2/
│  ├─ PET_series_1/
│  └─ ......
└─ case_002/

输出结构：
nifti_dataset/
├─ case_001/
│  ├─ CT#series_1.nii.gz
│  ├─ PET#series_1.nii.gz
│  └─ SUVTBW#series_1.nii.gz
└─ case_002/
```
