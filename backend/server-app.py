from flask import Flask, Response, send_from_directory,request,redirect, url_for
from flask_cors import CORS,cross_origin
import cv2
import numpy as np
import json
import os,requests
import colorsys
from werkzeug.utils import secure_filename
# from dl.face_recognition import FaceImage
UPLOAD_FOLDER = '/home/shehzikhan/Projects/image_processing_server/data/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

data_dict = json.load(open(os.path.join(os.pardir, 'data','database.json'), 'r'))

app = Flask(__name__)
cors = CORS(app, cross_origin=True,resources={r"http://0.0.0.0:3000/*": {"origins": "*"}})
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    images=os.listdir(os.path.join(os.pardir, "data", "images"))

    if 'start' in request.args:
        start = int(request.args.get('start'))
    else:
        start=0
    if 'end' in request.args:
        end = int(request.args.get('end'))
        if end >=len(images):
            end = len(images) - 1
    else:
        end=len(images)-1

    return Response(json.dumps(images[start:end]),headers={"Access-Control-Allow-Origin": "*"})

@app.route('/images/length')
def get_images_number():
    return Response(json.dumps({'len':len(data_dict["images"])}), headers={"Access-Control-Allow-Origin": "*"})
    # return

# def process_image():
#     face = FaceImage()
#     rgb_image = cv2.imread('pic.jpg')
#     result = face.detect_face(rgb_image)
#     return result

def process_on_server(img):
    _,img_encoded=cv2.imencode('.jpg',img)
    respose= requests.post("http://0.0.0.0:5050/recognize",data=img_encoded.tostring(),headers={'content-type':'image/jpeg'})
    result=json.loads(respose.text)
    print(result)
    # print(type(result))
    return result


@app.route('/image')
def get_image():
    img_file=request.args.get('file_name')
    show_bbox=True
    show_identity=True
    show_age=True
    show_gender=True
    show_emotion=True
    if 'bbox' in request.args:
        bbox_arg=request.args.get('bbox')
        show_bbox = False if bbox_arg == "false" else True
    if 'identity' in request.args:
        identity_arg=request.args.get('identity')
        show_identity = False if identity_arg == "false" else True
    if 'age' in request.args:
        age_arg=request.args.get('age')
        show_age = False if age_arg == "false" else True
    if 'gender' in request.args:
        gender_arg=request.args.get('gender')
        show_gender = False if gender_arg == "false" else True
    if 'emotion' in request.args:
        emotion_arg=request.args.get('emotion')
        show_emotion = False if emotion_arg == "false" else True


    image = cv2.imread(os.path.join(os.pardir, "data", "images", img_file))
    results = process_on_server(image)

    if len(results)>0:
        N=len(results)
        HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N)]
        RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        # print(RGB_tuples)
        thickness = 1
        # print(thickness)
        for i,face in enumerate(results):
            identity=face["identity"]
            age=face["age"]
            gender=face["gender"]
            emotion=face["emotion"]
            size=["size"]
            bbox=face["bbox"]

            color = (int(RGB_tuples[i][0] * 255), int(RGB_tuples[i][1] * 255), int(RGB_tuples[i][2] * 255))

            if show_bbox:
                cv2.rectangle(image, (bbox[0],bbox[1]), (bbox[2],bbox[3]), color, thickness=1, lineType=8, shift=0)

            info=[]
            if show_identity:
                info.append(identity)
            if show_gender:
                info.append(gender)
            if show_age:
                info.append(str(age))
            if show_emotion:
                info.append(emotion)
            font_size=1
            text_x = bbox[0] + (2* thickness)
            text_y = bbox[1] + (2 * thickness)
            for i,x in enumerate(info):
                print(type(x),x)
                if type(x) == type({"":""}):
                    info[i]="unkown"
            text=",".join(info)
            cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_size, color,2)

    ret, jpeg = cv2.imencode('.jpg', image)
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
    if 'file_name' in request.args:
        # img_id = request.args.get('id')
        img_file = request.args.get('file_name')
        image = cv2.imread(os.path.join(os.pardir, "data", "images", img_file))
        _, img_encoded = cv2.imencode('.jpg', image)
        response = requests.post("http://0.0.0.0:5050/annotations", data=img_encoded.tostring(),
                                headers={'content-type': 'image/jpeg'})
        # result = json.loads(response.text)
        # print(result)
        # print(type(result))
        return response

        # for img in data_dict["annotations"]:
        #     if int(img["image_id"]) == int(img_id):
        #         return json.dumps(img)

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


@app.route('/images/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' in request.files:

            file = request.files['file']
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                print('No selected file')
                return redirect(request.url)
            if file:
                filename = secure_filename(file.filename)
                print(file.filename,filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        else:
            nparr = np.fromstring(request.data, np.uint8)
            print(nparr)
            # decode image
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            print(img.shape)
            cv2.imwrite("/home/shehzikhan/Projects/image_processing_server/data/uploads/new.jpg",img)

    return Response(json.dumps({"classes": ""}), headers={"Access-Control-Allow-Origin": "*"})


app.run(host='0.0.0.0')