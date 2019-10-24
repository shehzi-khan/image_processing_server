from flask import Flask, Response, send_from_directory,request
import cv2
import json
import os

data_dict = json.load(open(os.path.join('data','database.json'), 'r'))

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
    return Response(json.dumps(data_dict["images"]))

@app.route('/image')
def get_image():
    img_file=request.args.get('file_name')
    return send_from_directory(os.path.join("data","images"),img_file)

@app.route('/image/details')
def get_details():
    if 'id' in request.args:
        img_id = request.args.get('id')
        for img in data_dict["images"]:
            if int(img["id"]) == int(img_id):
                return json.dumps(img)

@app.route('/image/annotations')
def get_annotations():
    if 'id' in request.args:
        img_id = request.args.get('id')
        for img in data_dict["annotations"]:
            if int(img["id"]) == int(img_id):
                return json.dumps(img)

@app.route('/image/mask')
def get_mask():
    img_file = request.args.get('file_name')
    return send_from_directory(os.path.join("data","masks"),img_file.replace("jpg","png"))


app.run(host='0.0.0.0', debug=True)