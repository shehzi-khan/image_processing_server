import json
import os


data_dict = json.load(open(os.path.join('data','database.json'), 'r'))
print("images:",data_dict["images"][0])
print("annotations:",data_dict["annotations"][0].keys())
print(data_dict["categories"][0])

def create_updated_json():
    images = os.listdir(os.path.join("data","images"))
    print(images)
    updated_images=[]
    ids=[]
    updated_ann=[]
    for img in data_dict["images"]:
        if img["file_name"] not in images:
            updated_images.append(img)
            ids.append(img["id"])

    for img in data_dict["annotations"]:
        if img["image_id"] not in ids:
            updated_ann.append(img)

    updated_json={"images":updated_images,"annotations":updated_ann,"categories":data_dict["categories"]}

    open(os.path.join("data","updated-data.json"),"w").write(json.dumps(updated_json))