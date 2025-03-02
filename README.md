# metabolism
Multi-organ metabolic analysis framework


---
1. 功能1：DICOM to NIfTI Conversion Tool
2. 
# DICOM to NIfTI Conversion Tool
## 功能概述
本工具提供医学影像数据(DICOM格式)的自动化批处理解决方案，支持以下核心功能：
1. **多模态转换**
   - CT/PET原始数据转为NIFTI标准格式
   - 自动识别设备制造商、扫描协议及序列描述
   - 元数据校验机制（随机采样10个文件验证一致性）
   - 支持CT、PET、动态转换成NIFTI格式
   - 支持PET转换成SUV NIFTI
2. **PET标准化摄取值(SUV)计算**
   - 支持6种体重标准化算法：
     * 总体重(TBW)
     * 成人瘦体重(Hume/James公式)
     * 儿童瘦体重(Peter/Fusch/Boer公式)

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

## 如何安装
```
# 支持pypi
pip install metabolism
```

## 如何使用
```
from metabolism import DcmWorker
dicomworker = DcmWorker(
    dicom_dataset = "<输入dicom_dataset的路径>",
    nifti_dataset = "<输出nifti_dataset的路径>",
    bodyweight = "TBW",# 还可以选择“LBW_child_Peter”,"LBW_child_Fusch","LBW_child_Boer","LBW_adult_James","LBW_adult_Hume"
    pipeline = ["DynamicPET"], # "CT","PET","DynamicPET","PETSUV"
)
dicomworker.run()
```
pipeline可以设置不同处理内容。
- "CT"：将CTdicom转换成nifti；
- "PET"：将静态PET转换成nifti；
- "DynamicPET"：将动态PET转换成nifti；
- "PETSUV"：将静态PET根据bodyweight的设置方法转换成SUV nifti；
