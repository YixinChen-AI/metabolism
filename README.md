# metabolism
Multi-organ metabolic analysis framework


---
1. 功能1：DICOM to NIfTI Conversion Tool
2. 功能2：对CT或者PET影像的分割
   2.1 MPUM
      - 请引用：Modality-Projection Universal Model for Comprehensive Full-Body Medical Imaging Segmentation
      - 可分割CT脑区、分割CT全身、分割PET脑区、分割PET全身，部分MR组织
   2.2 TotalSegmentator:
      - 请引用：TotalSegmentator: robust segmentation of 104 anatomic structures in CT images
      - 可分割CT全身，部分MR组织
   2.3 MOOSE:
      - 请引用：Fully-automated, semantic segmentation of whole-body 18F-FDG PET/CT images based on data-centric artificial intelligence
      - 可分割CT全身，部分MR组织
# 0 准备
## 0.1 数据集格式
请务必用这样的格式进行准备，后续的分析都会基于这样的结果进行。
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

## 0.2 如何安装
```
# 支持pypi
pip install metabolism
```
# 1. DICOM to NIfTI Conversion Tool (metabolism.DcmWorker)
## 1.1 功能概述
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

## 1.2 如何使用
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

# 2. 对CT或者PET影像的分割（metabolism.Segmentor）
## 2.1 功能概述
一个医学影像分割工具，主要用于处理NIFTI格式的CT图像数据
1. **环境诊断模块**
   - 自动检测PyTorch框架的安装状态及GPU硬件支持情况
2. **通过check_pytorch_environment函数**
   - 支持单文件推理（inference方法）和批量处理（inference_all方法）
  
## 2.2 如何使用
