from flask import Flask, Response, send_from_directory,request
from flask_cors import CORS,cross_origin
import cv2
import json
import os
import colorsys

# print(os.pardir)
# exit()
data_dict = json.load(open(os.path.join(os.pardir, 'data','database.json'), 'r'))

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

app = Flask(__name__)
cors = CORS(app, cross_origin=True,resources={r"http://0.0.0.0:3000/*": {"origins": "*"}})

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/live')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/category')
def get_category():
    result= data_dict["categories"]
    if 'id' in request.args:
        for cat in result:
            if int(cat['id']) == int(request.args.get('id')):
                result = cat
                break
    else:
        print(request.args)
    return Response(json.dumps(result))

@app.route('/images')
def get_images():
    # images = []
    # for entry in data_dict["images"]:
    #     images.append(entry["file_name"])
    if 'start' in request.args:
        start = int(request.args.get('start'))
    else:
        start=0
    if 'end' in request.args:
        end = int(request.args.get('end'))
        if end >=len(data_dict["images"]):
            end = len(data_dict["images"]) - 1
    else:
        end=len(data_dict["images"])-1

    return Response(json.dumps(data_dict["images"][start:end]),headers={"Access-Control-Allow-Origin": "*"})

@app.route('/images/length')
def get_images_number():
    return Response(json.dumps({'len':len(data_dict["images"])}), headers={"Access-Control-Allow-Origin": "*"})
    # return

@app.route('/image')
def get_image():
    img_file=request.args.get('file_name')
    mask=None
    img=None
    annotations=None
    final_image=None
    final_ann=[]
    if 'mask' in request.args:
        mask_arg=request.args.get('mask')
        if mask_arg=="true":
            mask=cv2.imread(os.path.join(os.pardir, "data", "masks", img_file.replace("jpg", "png")))
    if 'bbox' in request.args:
        bbox_arg=request.args.get('bbox')
        if bbox_arg=="true":
            for item in data_dict["images"]:
                if item["file_name"] == img_file:
                    id=item["id"]
                    break;

            for item in data_dict["annotations"]:
                if int(item["image_id"]) == int(id):
                    annotations=item
                    break;

            if 'ann' in request.args:
                final_ann = []
                ann = request.args.get('ann')
                list_ann = ann.split(',')
                for seg in annotations["segments_info"]:
                    if str(seg["id"]) in list_ann:
                        final_ann.append(seg)

    if 'hide_image' in request.args:
        hide_image_arg=request.args.get('hide_image')
        if hide_image_arg=="false":
            img = cv2.imread(os.path.join(os.pardir, "data", "images", img_file))



    # img = cv2.imread(os.path.join(os.pardir, "data", "images", img_file))

    if img is not None:
        final_image=img
        if mask is not None:
            final_image=cv2.addWeighted(final_image,0.3,mask,0.9,0,final_image)
    else:
        if mask is not None:
            final_image=mask
        else:
            final_image = cv2.imread(os.path.join(os.pardir, "data", "images", img_file))

    if len(final_ann)>0:
        N=len(final_ann)
        HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N)]
        RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        # print(RGB_tuples)
        thickness = int(final_image.shape[0] * 0.01)
        print(thickness)
        for i,segment in enumerate(final_ann):
            bbox=segment["bbox"]
            cat_id=segment["category_id"]
            for cat in data_dict["categories"]:
                if int(cat["id"]) == int(cat_id):
                    super_category=cat["supercategory"]
                    category=cat["name"]
                    break;
            color=(int(RGB_tuples[i][0]*255),int(RGB_tuples[i][1]*255),int(RGB_tuples[i][2]*255))
            cv2.rectangle(final_image, (bbox[0],bbox[1]), (bbox[0]+bbox[2],bbox[1]+bbox[3]), color, thickness=3, lineType=8, shift=0)

            font_size=1
            # if bbox[0]- (font_size* 10 + 2* thickness)  >= 0 :
            #     text_x = bbox[0]- (font_size* 10 + 2* thickness)
            # else:
            text_x = bbox[0] + (2* thickness)

            text_y = bbox[1] + (2 * thickness)
            cv2.putText(final_image, super_category+" / "+category, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_size, color,2)

    ret, jpeg = cv2.imencode('.jpg', final_image)
    img_bytes=jpeg.tobytes()
    img_data=(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + img_bytes + b'\r\n\r\n')
    return Response(img_data,mimetype='multipart/x-mixed-replace; boundary=frame')
    # return Response(img, headers={"Access-Control-Allow-Origin": "*"})
    # return send_from_directory(os.path.join(os.pardir,"data","images"),img_file)

@app.route('/thumbs')
def get_thumb():
    img_file=request.args.get('file_name')
    return send_from_directory(os.path.join(os.pardir,"data","thumbs"),img_file)

@app.route('/image/details')
def get_details():
    if 'id' in request.args:
        img_id = request.args.get('id')
        details=None
        for img in data_dict["images"]:
            if int(img["id"]) == int(img_id):
                details=img
        for img in data_dict["annotations"]:
            if int(img["image_id"]) == int(img_id):
                for key in img.keys():
                    if str(key) is not "image_id":
                        details[key]=img[key]
        return json.dumps(details)

@app.route('/image/annotations')
def get_annotations():
    if 'id' in request.args:
        img_id = request.args.get('id')
        for img in data_dict["annotations"]:
            if int(img["image_id"]) == int(img_id):
                return json.dumps(img)

@app.route('/image/classes')
def get_classes():
    if 'id' in request.args:
        img_id = request.args.get('id')
        for item in data_dict["annotations"]:
            if int(item["image_id"]) == int(img_id):
                annotations = item
                break;
        classes=[]
        for i,segment in enumerate(annotations["segments_info"]):
            bbox=segment["bbox"]
            cat_id=segment["category_id"]
            seg_id=segment["id"]
            for cat in data_dict["categories"]:
                if int(cat["id"]) == int(cat_id):
                    super_category=cat["supercategory"]
                    category=cat["name"]
                    break;
            classes.append({"seg_id":seg_id,"cat_id":cat_id,"category":category,"super":super_category})

        print(classes)
        return Response(json.dumps({"classes":classes}), headers={"Access-Control-Allow-Origin": "*"})

@app.route('/image/mask')
def get_mask():
    img_file = request.args.get('file_name')
    return send_from_directory(os.path.join(os.pardir,"data","masks"),img_file.replace("jpg","png"))


app.run(host='0.0.0.0', debug=True)