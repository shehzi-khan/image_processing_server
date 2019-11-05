import json
import os


data_dict = json.load(open(os.path.join('../data','database.json'), 'r'))
print("images:",len(data_dict["images"]))
# exit()
print("annotations:",data_dict["annotations"][0].keys())
print(data_dict["categories"][0])


def create_updated_json():
    images = os.listdir(os.path.join("../data","images"))
    print(images)
    updated_images=[]
    ids=[]
    updated_ann=[]
    for img in data_dict["images"]:
        if str(img["file_name"]) in images:
        # if int(img["file_name"].split('.')[0]) == 7795:
            updated_images.append(img)
            ids.append(img["id"])

    for img in data_dict["annotations"]:
        if img["image_id"] in ids:
            updated_ann.append(img)

    updated_json={"images":updated_images,"annotations":updated_ann,"categories":data_dict["categories"]}
    print(len(updated_json["images"]))

    open(os.path.join("../data","database.json"),"w").write(json.dumps(updated_json))


# create_updated_json()