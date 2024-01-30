import os
import cv2
import torch
from matplotlib import pyplot as plt


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_type = "DPT_Large"     # MiDaS v3 - Large     (highest accuracy, slowest inference speed)
# model_type = "DPT_Hybrid"   # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed)
# model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)

model = torch.hub.load("isl-org/MiDaS", model_type)
# model = torch.load("C:\\Users\\Administrator\\Desktop\\机器人框架v2\\midas\\weight\\dpt_large_384.pt")
model.to(device)
model.eval()

midas_transforms = torch.hub.load("isl-org/MiDaS", "transforms")

if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
    transform = midas_transforms.dpt_transform
else:
    transform = midas_transforms.small_transform


folder = 'result_midas_pic'
# folder = 'result_dpt_pic'
for num in range(2):
    img = cv2.imread(f"{num+1}.jpg")
    # img = cv2.imread(f"2.jpg")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    input_batch = transform(img).to(device)

    with torch.no_grad():
        prediction = model(input_batch)

        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()

    depth_map = prediction.cpu().numpy()

    plt.imshow(depth_map, cmap='plasma')
    plt.colorbar() # 添加颜色条
    plt.show()

    depth_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
    depth_normalized = depth_normalized.astype('uint8')
    depth_image = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_VIRIDIS)

    filr_path = os.path.join(folder,f'depth2_image{num+1}.jpg' )
    cv2.imwrite(filr_path, depth_image)