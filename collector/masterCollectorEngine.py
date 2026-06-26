import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGE_DATASET_ROOT = PROJECT_ROOT / "ImageDataSet"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".heic", ".heif"}
NO_PREPROCESS_FLAGS = {"--no-preprocess", "--skip-preprocess"}

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from forensics.localForensicsRegions import build_local_forensic_map
from forensics.physicalPrintEngine import analyze_physical_print
from detectors.stickerDetector import detect_sticker
from preprocessing.normalizeLightining import normalize_lighting
from forensics.qrGeometryEngine import analyze_qr_geometry


def parse_image_arguments(args):

    if len(args) >= 3 and args[0].lower() == "imagedataset":
        return str(Path(args[0]) / args[1] / args[2]), args[3] if len(args) >= 4 else None

    if len(args) >= 2 and Path(args[1]).suffix.lower() in IMAGE_EXTENSIONS:
        dataset_folder = IMAGE_DATASET_ROOT / args[0]
        project_folder = PROJECT_ROOT / args[0]

        if dataset_folder.is_dir() or project_folder.is_dir():
            return str(Path(args[0]) / args[1]), args[2] if len(args) >= 3 else None

    return args[0], args[1] if len(args) >= 2 else None


def resolve_image_path(image_path):

    input_path = Path(image_path).expanduser()

    if input_path.is_absolute():
        return input_path if input_path.is_file() else None

    candidates = [
        PROJECT_ROOT / input_path,
        IMAGE_DATASET_ROOT / input_path,
    ]

    if len(input_path.parts) == 1 and IMAGE_DATASET_ROOT.exists():
        candidates.extend(IMAGE_DATASET_ROOT.glob(f"*/{input_path.name}"))

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    return None


def metaData(stickerId,device,lightning,flash,distance,captureType,tilt):

    metaData1={"metaData":{"stickerId":stickerId,"device":device,"lightning":lightning,"flash":flash,"distance":distance,"captureType":captureType,"tilt":tilt}}

    metaJSon=json.dumps(metaData1)

    return metaJSon


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(json.dumps({
            "error": "Provide image path"
        }))

        sys.exit()

    masterData=[]    

    run_preprocessing = not any(flag in sys.argv[1:] for flag in NO_PREPROCESS_FLAGS)
    collector_args = [
        arg for arg in sys.argv[1:]
        if arg not in NO_PREPROCESS_FLAGS
    ]

    if len(collector_args) < 1:
        print(json.dumps({
            "error": "Provide image path"
        }))

        sys.exit()

    image_argument, output_argument = parse_image_arguments(collector_args)

    resolved_image_path = resolve_image_path(image_argument)

    if resolved_image_path is None:
        print(json.dumps({
            "error": "Image not found",
            "imagePath": image_argument,
            "imageDataSetRoot": str(IMAGE_DATASET_ROOT)
        }))

        sys.exit()

    image_path = str(resolved_image_path)

    normalized_image_output=str(
        output_argument
        if output_argument is not None
        else PROJECT_ROOT / "collector" / f"{Path(image_path).stem}Completed.jpg"
    )

    warped_image_output=str(PROJECT_ROOT / "collector" / f"{Path(image_path).stem}WarpedImage.jpg")

    metaJson=metaData("Sunlight_GENUINE_A12_test40","SamsungA12","Day_4:00pm",False,"medium","Genuine",4)
    # print(metaJson)

    if not metaJson:
        sys.exit("metaJson is empty brooooo")

    jsonLoads=json.loads(metaJson)

    firstValue=list(jsonLoads.values())[0]

    firstValue= jsonLoads["metaData"]["stickerId"]

    if run_preprocessing:
        warpedImage=detect_sticker(image_path,warped_image_output)

        camera_detail,output_path=normalize_lighting(warped_image_output,normalized_image_output)

        print(warpedImage)

        qr_image_path = warped_image_output

    else:
        output_path = image_path
        qr_image_path = image_path

    masterData.append(metaJson)

    # print("here is first master data",master)

    result  = build_local_forensic_map(output_path)

    if not result:

        sys.exit("Result is empty broooooo")

    resultJson=json.dumps(result)

    masterData.insert(1,resultJson)

    # print("Secondary Data Stored>>>",master)

    result2 = analyze_physical_print(output_path)

    if not result2:

        sys.exit("Result is empty broooooo")


    result2Json = json.dumps(result2)

    masterData.insert(2,result2Json) 


    qrGeometryData= analyze_qr_geometry(qr_image_path)

    if not qrGeometryData:
         sys.exit("QR DETECTION ERROR")

    qrGeometryDataJson=json.dumps(qrGeometryData)
    masterData.insert(3,qrGeometryDataJson)

    master_data_path = PROJECT_ROOT / "Datasets" / "Genuine" / f"{Path(output_path).stem}_masterData.json"
    master_data_path.parent.mkdir(parents=True, exist_ok=True)

    masterDataJson = {}
    for item in masterData:
        masterDataJson.update(json.loads(item))

    with master_data_path.open("w", encoding="utf-8") as master_data_file:
        json.dump(masterDataJson, master_data_file, indent=2)


    print(masterDataJson,output_path)
    print(masterDataJson["metaData"])

    



