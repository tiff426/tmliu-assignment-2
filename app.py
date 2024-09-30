import numpy as np
from PIL import Image as im
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import sklearn.datasets as datasets
import plotly.graph_objects as go
import plotly.express as px
from flask import Flask, render_template, jsonify, send_file, request
import json
import os
# the methods we'll need from kmeans.py
from kmeans import KMeans, create_data
from io import BytesIO
from werkzeug.utils import secure_filename
import glob

app = Flask(__name__, static_url_path='/static')

kmeans = None
total = 0
points = None

SNAPS_FOLDER = './snaps/steps'
app.config['SNAPS_FOLDER'] = SNAPS_FOLDER

if not os.path.exists(SNAPS_FOLDER):
    os.makedirs(SNAPS_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')


# create the starting first plot
points = []

def first_plot(points):
    # TEMPFILE = 'snaps/initial.png'
    # fig, ax = plt.subplots()
    # fig.set_figwidth(15)
    # fig.set_figheight(15)
    # plt.title('KMeans Clustering Data')
    # # dont have self.data yet
    # ax.scatter(points[:, 0], points[:, 1], c='blue')
    # fig.savefig(TEMPFILE)
    # plt.grid()
    # plt.close()
    plt.scatter(points[:, 0], points[:, 1], c='blue', alpha=0.6) 
    plt.savefig('static/initial.png')
    plt.close()

@app.route('/first')
def first():
    global points
    num_points = int(request.args.get('numPoints', 30))
    points = create_data()
    first_plot(points)
    return send_file('./static/initial.png')   # that's what the file is called in kmeans

@app.route('/getsnap')
def get_snap():
    # kmeans.py handles all oru snaps, but now we actually have to disply the right snap back
    step = int(request.args.get('step_count', 0))
    path = f'snaps/steps/step{step}.png'
    return send_file(path)

@app.route('/execute', methods=['GET'])
def execute():
    global kmeans
    global total
    k = int(request.args.get('k', 0))
    first_method = request.args.get('first_method', 'random')   # random if not
    kmeans = KMeans(points, k)
    total = kmeans.lloyds(first_method)
    return str(total)

@app.route('/manually', methods=['GET'])
def man_execute():
    global kmeans
    global total
    k = int(request.args.get('k', 0))
    man_points = json.loads(request.args.get('manual_points'))
    kmeans = KMeans(points, k)
    total = kmeans.man_lloyds(man_points)
    return str(total)

@app.route('/resetplot')
def reset():
    global kmeans 
    kmeans = None
    global total
    total = 0

    snaps = glob.glob(os.path.join(SNAPS_FOLDER, '*'))
    for snap in snaps:
        os.remove(snap)

    return send_file('./snaps/initial.png')

@app.route('/newdata')
def newData():
    reset()
    global points
    points = create_data()
    first_plot(points)
    return send_file('./snaps/initial.png')

@app.route('/getmanpoints')
def get_man_points():
    global points
    if points is not None:
        return jsonify(points.tolist())
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
