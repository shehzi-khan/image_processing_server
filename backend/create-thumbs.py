import os,cv2

def create_thumbs():
    images = os.listdir(os.path.join("../data","images"))
    for img in images:
        image = cv2.imread(os.path.join("../data","images",img))
        thumb = cv2.resize(image,(48,48))
        cv2.imwrite(os.path.join("../data","thumbs",img),thumb)

create_thumbs()