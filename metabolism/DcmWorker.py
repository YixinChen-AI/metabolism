from pathlib import Path
import sys,os,time
import pydicom,datetime
import dicom2nifti
import SimpleITK as sitk
class DcmWorker:
    def __init__(self,dicom_dataset,nifti_dataset):
        self.dicom_dataset = dicom_dataset
        self.nifti_dataset = nifti_dataset
        os.makedirs(nifti_dataset,exist_ok=True)

        self.ERROR_ICON = '❌'
        self.SUCCESS_ICON = '✅'
        self.RUNNING_ICON = '⏳'
        self.INFO_ICON = '➤'

        self.bodyweight = "TBW"
        
        pass
    def run(self):
        print(f"\n{'='*30}\nProcessing DICOM dataset: {self.dicom_dataset}\n{'='*30}")
        for case_name in os.listdir(self.dicom_dataset):
            print(f"\n[{self.INFO_ICON}Case] Processing: {case_name}")
            os.makedirs(os.path.join(self.nifti_dataset,case_name),exist_ok=True)
            print(f"  [{self.INFO_ICON}Directory] Output path created/exists: {os.path.join(self.nifti_dataset,case_name)}")
            for dicom_name in os.listdir(os.path.join(self.dicom_dataset,case_name)):
                time.sleep(3)
                dicom_dir = os.path.join(self.dicom_dataset,case_name,dicom_name)
                print(f"  [{self.RUNNING_ICON}] dicom path: {dicom_dir}")
                info = self._get_modality_info_from_dir(dicom_dir)
                if info.__contains__('error'):
                    print(f"  [{self.ERROR_ICON}Error] {info['error']}")
                    continue
                if info['ModalityType'] == 'CT':
                    print(f"  [{self.RUNNING_ICON}Conversion] Converting CT series to NIfTI")
                    dicom2nifti.convert_dicom.dicom_series_to_nifti(dicom_dir, os.path.join(self.nifti_dataset,case_name,f"{info['ModalityType']}#{dicom_name}.nii.gz"), reorient_nifti=True)
                    print(f"  [{self.SUCCESS_ICON}Success] Conversion completed")
                if info['ModalityType'] == 'PET':
                    print(f"  [{self.RUNNING_ICON}Conversion] Converting PET series to NIfTI")
                    dicom2nifti.convert_dicom.dicom_series_to_nifti(dicom_dir, os.path.join(self.nifti_dataset,case_name,f"{info['ModalityType']}#{dicom_name}.nii.gz"), reorient_nifti=True)
                    print(f"  [{self.SUCCESS_ICON}Success] Conversion completed")
                    print(f"  [{self.RUNNING_ICON}Conversion] Converting PET series to SUV")
                    self._dicom2niftiSUV(dicom_dir,os.path.join(self.nifti_dataset,case_name,f"SUV{self.bodyweight}#{dicom_name}.nii.gz"),
                                        bodyweight=self.bodyweight,ptnifti=os.path.join(self.nifti_dataset,case_name,f"{info['ModalityType']}#{dicom_name}.nii.gz"))
                    print(f"  [{self.SUCCESS_ICON}Success] Conversion completed")
                    
    def _get_modality_info_from_dir(self,dicom_dir):
        """识别DICOM文件夹的模态和设备信息"""
        # 随机采样前3个文件确保元数据一致性
        dicom_dir = Path(dicom_dir)
        sample_files = [f for f in dicom_dir.glob("*") if f.is_file()][:10]
        if len(sample_files) == 0:
            return {"error":f"dicom_dir is an empty dir! [{dicom_dir}]"}
        info = {}
        for f in sample_files:
            try:
                ds = pydicom.dcmread(f, stop_before_pixels=True)
                if not info:  # 首次读取初始化
                    info.update({
                        'Modality': ds.get('Modality', 'UN'),
                        'Manufacturer': ds.get('Manufacturer', 'Unknown'),
                        'Model': ds.get('ManufacturerModelName', 'Unknown'),
                        'Protocol': ds.get('ProtocolName', ''),
                        'SeriesDescription': ds.get('SeriesDescription', ''),
                        'ScanOptions': ds.get('ScanOptions', ''),
                        'ContrastBolusAgent': ds.get('ContrastBolusAgent', ''),
                    })
                else: 
                    if ds.Modality != info['Modality']:
                        raise ValueError("文件夹包含混合模态数据")
            except Exception as e:
                print(f"文件{f.name}读取错误: {str(e)}")
        info['ModalityType'] = self._classify_modality(info)
        return info

    def _classify_modality(self,info):
        """结合多个标签进行模态细分"""
        modality = info['Modality']
        # CT类型判断
        if modality == 'CT':
            return 'CT'
        
        # PET类型判断
        if modality == 'PT':
            if 'dynamic' in info['SeriesDescription'].lower():
                return 'Dynamic PET'
            if 'FDG' in info.get('SeriesDescription', ''):
                return 'PET (FDG)'
            return 'PET'
        
        # MR类型判断
        if modality == 'MR':
            if 'TOF' in info['Protocol']:
                return 'MR Angiography'
            if 'DWI' in info['SeriesDescription']:
                return 'MR (Diffusion)'
            return 'MR'
        
        # 其他模态
        modality_map = {
            'CR': 'X-Ray',
            'DX': 'Digital Radiography',
            'MG': 'Mammography'
        }
        return modality_map.get(modality, 'Unknown')

    def _dicom2niftiSUV(self,dicomdir,niftiname,bodyweight="TBW",ptnifti=None):
        img = sitk.ReadImage(ptnifti)
        array = sitk.GetArrayFromImage(img)
        ds = pydicom.dcmread(os.path.join(dicomdir, os.listdir(dicomdir)[0]))
        try:
            radiopharm_datetime = ds.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartDateTime
        except:
            radiopharm_datetime = ds[0x0008, 0x0022].value +ds.RadiopharmaceuticalInformationSequence[0].RadiopharmaceuticalStartTime
        injection_dose = float(ds.RadiopharmaceuticalInformationSequence[0].RadionuclideTotalDose)
        half_life = float(ds.RadiopharmaceuticalInformationSequence[0].RadionuclideHalfLife)
        weight = float(ds[0x0010, 0x1030].value)
        gender = ds.PatientSex
        # calculate weight
        if bodyweight == "TBW":
            weight = weight
        elif bodyweight == "LBW_adult": # Hume Formula 考虑了性别体重身高，对于成年人非常有用
            height = float(ds.PatientSize * 100)
            if gender == 'M':
                weight = 0.32810 * weight  + 0.33929 * height - 29.5336
            elif gender == 'F':
                weight = 0.29569 * weight  + 0.41813 * height - 43.2993
        elif bodyweight == "LBW_child_Peter": # peter 适用儿童和青少年，考虑了年龄的影响
            # gender = ds.PatientSex
            # height = ds.PatientSize * 100
            height = float(ds.PatientSize * 100)
            if gender == 'M':
                weight = (1.1 * weight)-128.0*(weight / height) ** 2
            elif gender == 'F':
                weight = (1.07 * weight)-148.0*(weight / height)** 2
        elif bodyweight == "LBW_child_Fusch": # Schmelzle and Fusch Formula 基于体重和身高，适用于不同年龄段的儿童
            # gender = ds.PatientSex
            # height = ds.PatientSize * 100
            weight = (0.0215 * weight**0.6469) * height ** 0.7236
        elif bodyweight == "LBW_child_Boer":
            # gender = ds.PatientSex
            # height = ds.PatientSize * 100
            height = float(ds.PatientSize * 100)
            if gender == 'M':
                weight = 0.465 * weight  + 0.180 * height - 21.6
            elif gender == 'F':
                weight = 0.473 * weight  + 0.173 * height - 20.6
        elif bodyweight == "LBW_adult_Boer":
            # gender = ds.PatientSex
            # height = ds.PatientSize * 100
            height = float(ds.PatientSize * 100)
            if gender == 'M':
                weight = 0.407 * weight  + 0.267 * height - 19.2
            elif gender == 'F':
                weight = 0.252 * weight  + 0.473 * height - 48.3
        elif bodyweight == "LBW_adult_James":
            height = float(ds.PatientSize * 100)
            # gender = ds.PatientSex
            # height = float(ds.PatientSize * 100)
            if gender == 'M':
                weight = 1.10 * float(weight)  - 128 * (weight / height) ** 2
            elif gender == 'F':
                weight = 1.07 * float(weight)  - 148 * (weight / height) ** 2
        elif bodyweight == "LBW_adult_Hume":
            # gender = ds.PatientSex
            # height = ds.PatientSize * 100
            height = float(ds.PatientSize * 100)
            if gender == 'M':
                weight = 0.32810 * weight  + 0.33929 * height - 29.5336
            elif gender == 'F':
                weight = 0.29569 * weight  + 0.41813 * height - 43.2933
        if half_life <= 0:
            print("Error: Half life is not positive.")
            return -1
        if ds[0x0054, 0x1102].value == 'START':
            try:
                acquisition_datetime = ds[0x0008, 0x002A].value
            except KeyError:
                acquisition_datetime = ds[0x0008, 0x0022].value +\
                      ds[0x0008, 0x0032].value
            dose = injection_dose * 2**(-datetimestr_diff(acquisition_datetime,radiopharm_datetime)/half_life)
        elif ds[0x0054, 0x1102].value == 'ADMIN':
            dose = injection_dose
        else:
            print("Error: Cannot determine the decay correction reference time.")
            return -1
        
        SUVfactor = weight * 1000 / dose
    
        # Apply SUV conversion to the nifti files
        img = sitk.ReadImage(ptnifti)
        try:
            img = sitk.Cast(img, sitk.sitkFloat32)
        except:
            pass
        img = img*SUVfactor
        sitk.WriteImage(img, niftiname)

def datetimestr_diff(datetimestr1, datetimestr2):
    """Calculate the time difference between two date time strings.
    Parameters
    ----------
    datetimestr1 : string
        Date time string 1.
    datetimestr2 : string
        Date time string 2.
    Returns
    -------
    diff : float
        Time difference in seconds.
    """
    # if decimal point is present, remove the decimal point and the following digits
    if '.' in datetimestr1:
        datetimestr1 = datetimestr1.split('.')[0]
    if '.' in datetimestr2:
        datetimestr2 = datetimestr2.split('.')[0]
    dt1 = datetime.datetime.strptime(datetimestr1, "%Y%m%d%H%M%S")
    dt2 = datetime.datetime.strptime(datetimestr2, "%Y%m%d%H%M%S")
    diff = (dt1 - dt2).total_seconds()
    return diff