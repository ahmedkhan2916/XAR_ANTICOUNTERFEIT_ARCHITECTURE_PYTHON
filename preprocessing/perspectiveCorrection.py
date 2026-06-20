# import cv2
# import numpy as np



# def order_points(pts):


#     rect = np.zeros((4,2),dtype="float32")
#     s=pts.sum(axis=1)

#     rect[0]=pts[np.argmin(s)]#top-left
#     rect[2]=pts[np.argmax(s)]#bottom-right

#     diff=np.diff(pts,axis=1)

#     rect[1]=pts[np.argmin(diff)]#top-right
#     rect[2]=pts[np.argmax(diff)]#bottom-left 

#     return rect






# def four_point_transform(image,pts):

#     rect=order_points(pts)

#     (tl,tr,bl,br)=rect

#     widthA= np.linalg.norm(br-bl)

#     widthB=np.linalg.norm(tr-tl)

#     maxWidth= max(int(widthA),int(widthB))

#     heightA = np.linalg.norm(tr - br)
#     heightB = np.linalg.norm(tl - bl)

#     maxHeight = max(int(heightA), int(heightB))

#     dst = np.array([
#         [0, 0],
#         [maxWidth - 1, 0],
#         [maxWidth - 1, maxHeight - 1],
#         [0, maxHeight - 1]
#     ], dtype="float32")

#     matrix = cv2.getPerspectiveTransform(rect, dst)

#     warped = cv2.warpPerspective(
#         image,
#         matrix,
#         (maxWidth, maxHeight)
#     )


#     return warped







# def correct_perspective(image_path,output_path="corrected.png"):

#     image=cv2.imread(image_path)

#     original=image.copy()

#     gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

#     blur=cv2.GaussianBlur(gray,(5,5),0)

#     edged=cv2.Canny(blur,75,200)

#     contours,_=cv2.findContours(edged,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

#     contours=sorted(contours, key=cv2.contourArea,reverse=True)[:5]

#     screenCnt = None

#     for contour in contours:

#         peri=cv2.arcLength(contour,True)

#         approx=cv2.approxPolyDP(contour, 0.02*peri,True)

#         if len(approx) == 4:

#             screencut = approx

#             break

    
#     if screenCnt is None:

#         raise Exception("Sticker Boundary not found")
    
#     warped = four_point_transform(original,screenCnt.reshape(4,2)) #this function will be created soon

#     cv2.imwrite(output_path,warped)

#     return output_path

# if __name__ == "__main__":

#     output=correct_perspective(

#         "test.jpg",
#         "corrected.png"
#     )

#     print("saved",output)






import cv2
import numpy as np
from warpSticker import warp_sticker
from normalizeLightining import normalize_lighting

# =========================
# LOAD IMAGE
# =========================

IMAGE_PATH = "GenuineChecked.png"

image = cv2.imread(IMAGE_PATH)

if image is None:
    raise Exception("Image not found")

original = image.copy()

# =========================
# PREPROCESSING
# =========================

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(gray, (5, 5), 0)

_, thresh = cv2.threshold(
    blur,
    120,
    255,
    cv2.THRESH_BINARY_INV
)

# =========================
# FIND CONTOURS
# =========================

contours, hierarchy = cv2.findContours(
    thresh,
    cv2.RETR_TREE,
    cv2.CHAIN_APPROX_SIMPLE
)

marker_candidates = []

# =========================
# DETECT SQUARES
# =========================

for contour in contours:

    area = cv2.contourArea(contour)

    # Ignore tiny contours
    if area < 100:
        continue

    perimeter = cv2.arcLength(contour, True)

    approx = cv2.approxPolyDP(
        contour,
        0.04 * perimeter,
        True
    )

    # Must have 4 corners
    if len(approx) != 4:
        continue

    x, y, w, h = cv2.boundingRect(approx)

    aspect_ratio = w / float(h)

    # Must be square-ish
    if 0.8 <= aspect_ratio <= 1.2:

        center_x = x + w // 2
        center_y = y + h // 2

        marker_candidates.append({
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "center": (center_x, center_y),
            "area": area
        })

# =========================
# SORT BIGGEST CANDIDATES
# =========================

marker_candidates = sorted(
    marker_candidates,
    key=lambda m: m["area"],
    reverse=True
)

# Keep strongest markers only
marker_candidates = marker_candidates[:40]

if len(marker_candidates) < 4:
    raise Exception("Not enough marker candidates found")

# =========================
# IMAGE SIZE
# =========================

height, width = gray.shape

# =========================
# FIND CORNER MARKERS
# =========================

top_left = None
top_right = None
bottom_left = None
bottom_right = None

min_tl = 999999999
min_tr = 999999999
min_bl = 999999999
min_br = 999999999

for marker in marker_candidates:

    cx, cy = marker["center"]

    # TOP LEFT
    dist_tl = cx + cy

    if dist_tl < min_tl:
        min_tl = dist_tl
        top_left = marker

    # TOP RIGHT
    dist_tr = (width - cx) + cy

    if dist_tr < min_tr:
        min_tr = dist_tr
        top_right = marker

    # BOTTOM LEFT
    dist_bl = cx + (height - cy)

    if dist_bl < min_bl:
        min_bl = dist_bl
        bottom_left = marker

    # BOTTOM RIGHT
    dist_br = (width - cx) + (height - cy)

    if dist_br < min_br:
        min_br = dist_br
        bottom_right = marker

# =========================
# DRAW DETECTED MARKERS
# =========================

corner_markers = [
    ("TOP_LEFT", top_left),
    ("TOP_RIGHT", top_right),
    ("BOTTOM_LEFT", bottom_left),
    ("BOTTOM_RIGHT", bottom_right)
]

for label, marker in corner_markers:

    x = marker["x"]
    y = marker["y"]
    w = marker["w"]
    h = marker["h"]

    cv2.rectangle(
        original,
        (x, y),
        (x + w, y + h),
        (0, 255, 0),
        3
    )

    cv2.putText(
        original,
        label,
        (x, y - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

# =========================
# PRINT RESULTS
# =========================

print("\n===== DETECTED XAR MARKERS =====")

for label, marker in corner_markers:
    print(
        f"{label}: {marker['center']}"
    )

# =========================
# CREATE CORNER MAP
# =========================

corners = {
    "top_left": top_left["center"],
    "top_right": top_right["center"],
    "bottom_right": bottom_right["center"],
    "bottom_left": bottom_left["center"]
}

# =========================
# WARP STICKER
# =========================

warped = warp_sticker(
    image,
    corners,
    output_size=1000
)

# =========================
# SAVE OUTPUTS
# =========================

cv2.imwrite(
    "detected_markers.png",
    original
)

cv2.imwrite(
    "final_warped_Genuine.png",
    warped
)

print("\nSaved outputs:")
print("detected_markers.png")
print("final_warped.png")

# =========================
# SHOW RESULTS
# =========================

cv2.imshow(
    "Detected XAR Markers",
    original
)

cv2.imshow(
    "Warped Sticker",
    warped
)

cv2.waitKey(0)
cv2.destroyAllWindows()