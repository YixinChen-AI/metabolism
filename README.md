# metabolism
Multi-organ metabolic analysis framework

# 项目名称

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/你的用户名/仓库名/blob/main/路径/你的Notebook.ipynb)

📌 **一键运行效果**：点击上方 <img src="https://colab.research.google.com/assets/colab-badge.svg" width="100" alt="Open in Colab"> 徽章，可直接在 Google Colab 中打开本项目的 Jupyter Notebook 并运行代码。


---
1. 功能1：DICOM to NIfTI Conversion Tool （metabolism.DcmWorker）
2. 功能2：对CT或者PET影像的分割 （metabolism.Segmentor）
3. 功能3：对构建reference network的正常人数量进行稳定性分析（metabolism.StabilityTester）
4. 功能4：Traditional Group-level metabolic network （metabolism.MetabolicNetworks.GroupLevelNetwork）
   
# 0 准备
## 0.1 数据集格式
请务必用这样的格式进行准备，后续的分析都会基于这样的结果进行。总之需要三级结构.
```bash
输入结构：
dicom_dataset/
├─ control group/
│  ├─ case_001#CT_series/
│  ├─ case_002#CT_series/
│  ├─ case_001#PET_series/
│  └─ ......
└─ disease1 group/

输出结构：
nifti_dataset/
├─ control group/
│  ├─ case_001#CT_series.nii.gz
│  ├─ case_002#CT_series.nii.gz
│  └─ case_001#PET_series.nii.gz
└─ disease1 group/
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
3. **支持模型清单**
   - MPUM 
      - 请引用：Modality-Projection Universal Model for Comprehensive Full-Body Medical Imaging Segmentation
      - 可分割CT脑区、分割CT全身、分割PET脑区、分割PET全身，部分MR组织
   - TotalSegmentator (soon):
      - 请引用：TotalSegmentator: robust segmentation of 104 anatomic structures in CT images
      - 可分割CT全身，部分MR组织
   - MOOSE (soon):
      - 请引用：Fully-automated, semantic segmentation of whole-body 18F-FDG PET/CT images based on data-centric artificial intelligence
      - 可分割CT全身，部分MR组织
## 2.2 如何使用
```
from metabolism import Segmentor
segmentor = Segmentor()
segmentor.load_model(modelname="mpum")
segmentor.inference_all(nifti_dataset="<输入nifti_dataset的路径>",
                       targetpart="brain")
```
细节：
1. 输入的nifti_dataset路径同样要求3级目录，与DcmWorker的输出目录路径结构一致；
2. 推理的分割结果会与.nii.gz文件在同一目录下面，分割结果会在f'{modelname}#{niftiname}'的文件夹中。

# 3. 稳定性分析 （metabolism.StabilityTester）
## 3.1 功能概述
- 从SUV图像与分割掩膜中提取ROI特征；
- 自动生成标准化摄取值比(SUVR)
- 数据质量筛查：自动检测NaN/Inf异常值
- 基于残差的偏相关计算（年龄/性别/体重协变量控制）
- 相关系数矩阵相似度评估（全数据 vs 子样本）

## 3.2 如何使用
```
from metabolism.StabilityTester import StabilityTester
stabilityTester = StabilityTester()
# step1
stabilityTester.suvseg2feature(dataset = "/share/home/yxchen/dataset/metabolism_dataset/ADNI_preprocess/ADNI_CN/",
                         modelname="mpum")
# step2
df = stabilityTester.analyze(dataset = "/share/home/yxchen/dataset/metabolism_dataset/ADNI_preprocess/ADNI_CN/",
                         modelname="mpum")
```
细节：
1. step1将分割结果和PET SUV进行特征提取，提取出每一个roi的relative meansuv；
2. step2将提出出来的relative meansuv进行稳定性分析。数据集有N个样本，随机抽取n个样本(n<N),N样本计算的partial correlation matrix和n样本计算的计算相似度。以此来确定多少reference group和control group的合理划分。
3. 这里的数据结构是2级结构。
   
# 4. metabolism.StabilityTester
## 4.1 功能概述
![image](https://github.com/user-attachments/assets/dbe1ae8d-da1b-4b8c-b888-150a7bb8f175)
Reference Paper: Individual-specific metabolic network based on 18F-FDG PET revealing multi-level aberrant metabolisms in Parkinson's disease

## 4.2 如何使用
```
from metabolism.MetabolicNetworks import GroupLevelNetwork
from metabolism.StabilityTester import StabilityTester
stabilityTester = StabilityTester()
groupLevelNetwork = GroupLevelNetwork()
# step 1
# stabilityTester.suvseg2feature(dataset = "/share/home/yxchen/dataset/metabolism_dataset/ADNI_preprocess/ADNI_CN/",
#                          modelname="mpum")
# stabilityTester.suvseg2feature(dataset = "/share/home/yxchen/dataset/metabolism_dataset/ADNI_preprocess/ADNI_AD/",
#                          modelname="mpum")

# step 2
grouplevelnet = groupLevelNetwork.process(dataset1 = "/share/home/yxchen/dataset/metabolism_dataset/ADNI_preprocess/ADNI_CN/",
                          dataset2 = "/share/home/yxchen/dataset/metabolism_dataset/ADNI_preprocess/ADNI_AD/",
                         modelname="mpum")
```
细节：
1. 两个数据集需要先进行stabilityTester的suvseg2feature的处理，也建议先进行稳定性分析；
2. 鉴于公式中的分子没有使用绝对值，datset1和dataset2并非对称；
