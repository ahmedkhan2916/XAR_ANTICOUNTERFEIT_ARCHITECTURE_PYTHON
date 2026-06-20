# import numpy as np
# import sys
# import json


# avgEdgeTurbulence=[]
# stdEdgeTurbulance=[]
# avgLocalVariange=[]
# stdLocalVariance=[]
# avgBleedScore=[]
# stdBleedScore=[]
# avgEdgedensity=[]
# stdEdgeDensity=[]


# totalEdgeTurbulanceData=[]
# totalLocalVarianceData=[]
# totalBleedData=[]
# totalEdgedensityData=[]



# def findAVGandSTD(regionLength):


#     # print("yes i am here to help you in finding avg and std",regionLength)
#     # AVG & STD OF EDGETURBULANCE REGIONS
#     average_Val_EdgeTurbulanceData=np.mean(totalEdgeTurbulanceData)
#     std_Val_EdgeTurbulanceData=np.std(totalEdgeTurbulanceData,ddof=1)

#     # AVG & STD OF LOCALVARIANCE REGIONS
#     average_Val_LocalVarianceData=np.mean(totalLocalVarianceData)
#     std_Val_LocalVarianceData=np.std(totalLocalVarianceData,ddof=1)

#     # AVG & STD OF BLEED REGIONS
#     average_Val_Bleed_Data=np.mean(totalBleedData)
#     std_Val_Bleed_Data=np.std(totalBleedData,ddof=1)

#     # AVG & STD OF EDGEDENSITY REGIONS
#     average_Val_Edge_Data=np.mean(totalEdgedensityData)
#     std_Val_Edge_Data=np.std(totalEdgedensityData,ddof=1)


#     if all([average_Val_EdgeTurbulanceData,std_Val_EdgeTurbulanceData,average_Val_LocalVarianceData,std_Val_LocalVarianceData,average_Val_Bleed_Data,std_Val_Bleed_Data,average_Val_Edge_Data,std_Val_Edge_Data]):

#         return average_Val_EdgeTurbulanceData,std_Val_EdgeTurbulanceData,average_Val_LocalVarianceData,std_Val_LocalVarianceData,average_Val_Bleed_Data,std_Val_Bleed_Data,average_Val_Edge_Data,std_Val_Edge_Data
    
#     else:
#         return False







    
    



# def extract_Regions_Data(ForensicData):

#     with open(ForensicData,"r")as file:

#         data=json.load(file)

#     all_regions_data=data["ForensicData"]
    
#     regionLength=len(all_regions_data)
    

#     for region_name,metrics in all_regions_data.items():
#         print("processing",region_name)

       
        
#         edgeTurbulance=metrics["edgeTurbulence"]
#         totalEdgeTurbulanceData.append(edgeTurbulance)
#         localVariance=metrics["localVariance"]
#         totalLocalVarianceData.append(localVariance)
#         bleedScore=metrics["bleedScore"]
#         totalBleedData.append(bleedScore)
#         edgeDensity=metrics["edgeDensity"]
#         totalEdgedensityData.append(edgeDensity)


#     if all([totalEdgeTurbulanceData,totalBleedData,totalEdgedensityData,totalLocalVarianceData]):

#         return True,regionLength  

#     else:

#         return False

#     # print(totalBleedData,totalEdgedensityData,totalLocalVarianceData,totalEdgeTurbulanceData)


        
        






# def getData(forensicData):

#     if not forensicData:
#         return "ForensicData is Empty"
    

#     Signal,regionLength=extract_Regions_Data(forensicData)

#     if Signal == True:
#         return True,regionLength
    
#     else:
#         return False
    





# if __name__ == "__main__":

#     checkSignal,regionLength=getData(forensicData=sys.argv[1])

#     if checkSignal==True:

#         average_Val_EdgeTurbulanceData,std_Val_EdgeTurbulanceData,average_Val_LocalVarianceData,std_Val_LocalVarianceData,average_Val_Bleed_Data,std_Val_Bleed_Data,average_Val_Edge_Data,std_Val_Edge_Data=findAVGandSTD(regionLength)


#         print(average_Val_EdgeTurbulanceData,std_Val_EdgeTurbulanceData,average_Val_LocalVarianceData,std_Val_LocalVarianceData,average_Val_Bleed_Data,std_Val_Bleed_Data,average_Val_Edge_Data,std_Val_Edge_Data)

#     else:
#         print("sorry something went wrong")    

   









import json
import sys

import numpy as np


METRIC_KEYS = (
    "edgeTurbulence",
    "localVariance",
    "bleedScore",
    "edgeDensity",
)


def findAVGandSTD(values_by_metric):
    stats = {}

    for metric_name, values in values_by_metric.items():
        if not values:
            raise ValueError(f"No values found for {metric_name}")

        stats[metric_name] = {
            "avg": float(np.mean(values)),
            "std": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        }

    return stats


def extract_Regions_Data(forensic_data_path):
    with open(forensic_data_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    all_regions_data = data.get("ForensicData")
    if not isinstance(all_regions_data, dict) or not all_regions_data:
        raise ValueError("ForensicData is missing or empty")

    values_by_metric = {metric_name: [] for metric_name in METRIC_KEYS}

    for region_name, metrics in all_regions_data.items():
        print("processing", region_name)

        for metric_name in METRIC_KEYS:
            if metric_name not in metrics:
                raise KeyError(f"{region_name} is missing {metric_name}")

            values_by_metric[metric_name].append(metrics[metric_name])

    return values_by_metric, len(all_regions_data)


def getData(forensicData):
    if not forensicData:
        raise ValueError("ForensicData path is empty")

    values_by_metric, regionLength = extract_Regions_Data(forensicData)
    stats = findAVGandSTD(values_by_metric)

    return stats, regionLength


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python regionStatistics.py <masterData.json>")
        sys.exit(1)

    try:
        stats, regionLength = getData(forensicData=sys.argv[1])
    except (FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as error:
        print(f"sorry something went wrong: {error}")
        sys.exit(1)

    print("total regions:", regionLength)
    print("edgeTurbulence avg/std:", stats["edgeTurbulence"]["avg"], stats["edgeTurbulence"]["std"])
    print("localVariance avg/std:", stats["localVariance"]["avg"], stats["localVariance"]["std"])
    print("bleedScore avg/std:", stats["bleedScore"]["avg"], stats["bleedScore"]["std"])
    print("edgeDensity avg/std:", stats["edgeDensity"]["avg"], stats["edgeDensity"]["std"])











