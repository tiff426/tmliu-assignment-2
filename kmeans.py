import numpy as np
from PIL import Image as im
import matplotlib.pyplot as plt
import sklearn.datasets as datasets
import plotly.graph_objects as go
import plotly.express as px
from flask import Flask, render_template, jsonify
import json

# centers = [[0, 0], [2, 2], [-3, 2], [2, -4]]
# X, _ = datasets.make_blobs(n_samples=300, centers=centers, cluster_std=1, random_state=0)
# now we have to create our data instead of hardcoding
# do outside of Kmeans class since we want data and initial graph to be there already
def create_data():
    # assignment didnt secify how many dtaa poitns so ill do 
    # points = np.random.rand(30, 2)
    # points = points * 10
    # return points
    data_points, _ = datasets.make_blobs(n_samples=30, cluster_std=1)
    return data_points


# def first_plot(points):
#     # TEMPFILE = 'snaps/initial.png'
#     # fig, ax = plt.subplots()
#     # fig.set_figwidth(15)
#     # fig.set_figheight(15)
#     # plt.title('KMeans Clustering Data')
#     # # dont have self.data yet
#     # ax.scatter(points[:, 0], points[:, 1], c='blue')
#     # fig.savefig(TEMPFILE)
#     # plt.grid()
#     # plt.close()
#     plt.scatter(points[:, 0], points[:, 1], c='blue', alpha=0.6) 
#     plt.savefig('static/initial.png')
#     plt.close()


class KMeans():

    def __init__(self, data, k):
        self.data = data
        self.k = k
        self.assignment = [-1 for _ in range(len(data))]
        self.snaps = []
    
    def snap(self, centers, step):
        # instead of previous implementation of snaps
        TEMPFILE = 'snaps/initial.png'
        fig, ax = plt.subplots()
        fig.set_figwidth(15)
        fig.set_figheight(15)
        plt.title('KMeans Clustering STEP ', step)
        ax.scatter(self.data[:, 0], self.data[:, 1], c='blue')
        ax.scatter(centers[:, 0], centers[:, 1], c='red')
        plt.legend()
        plt.grid()
        fig.savefig('snaps/steps/step{step}.png')
        plt.close()



    def lloyds(self, method):
        # reset snaps
        self.snaps = []
        # need centers
        centers = self.initialize(method)
        step_count = 0
        # match data points to nearest center to create initial clusters
        self.snap(centers, step_count)
        self.make_clusters(centers)
        # adjust centers
        new_centers = self.compute_centers()
        step_count += 1
        self.snap(new_centers, step_count)
        history = [self.get_plot_data(centers)]
        while not self.converged(centers, new_centers):
            self.unassign()
            centers = new_centers
            self.make_clusters(centers)
            new_centers = self.compute_centers()
            step_count += 1
            self.snap(centers, step_count)
            history.append(self.get_plot_data(centers))
        
        return step_count
    
    # we need a separate implementation of lloyds for manual since we capture snapshots different
    def man_lloyds(self, points):
        # reset snaps
        self.snaps = []
        step_count = 0
        centers = np.array([[point['x'], point['y']] for point in points])
        self.snap(centers, step_count)
        self.make_clusters(centers)
        new_centers = self.compute_centers()
        step_count += 1
        self.snap(new_centers, step_count)
        while not self.converged(centers, new_centers):
            self.unasign()
            centers = new_centers
            self.make_clusters(centers)
            new_centers = self.compute_centers()
            step_count += 1
            self.snap(centers, step_count)
        return step_count

    
    # helper methods for lloyds
    # oh duhhhhh we can just create a different initializtion function for each of the required initializaation methods
    def initialize(self, method): # just choose some centeres fo initilaization??
      # picking k indices at random to be our random centers to start
        # TO DO!!!! NEED TO GET USER CHOICE AND DEPENDING ON CHOICE RUN ONE OF THESE THEN RETURN THAT RESULT   
        if method == "rand":
            return self.random_initialization()
        elif method == "far":
            return self.farthest_initialization()
        elif method == "kmeanspp":
            return self.kmeanspp
        else:
            return self.random_initialization()
        



    # random initialization (same as previously implemented initialization)
    def random_initialization(self):
        return self.data[np.random.choice(len(self.data), self.k, replace=False)]
    
    # farthest first
    def farthest_initialization(self):
        # so liek jsut iterate and find the farthest points??
        # this is like finding a point and finding the one farthest from it, not finding the longest distance betwen any 2 points
        random_start = np.random.choice(len(self.data))
        centers = [self.data[random_start]]
        # first we have to find the distances from each point to each center
        # then take the maximum of all those distances
        for i in range(1, self.k):   # since we already have a center, only need to fine k - 1
            distances = []
            for point in self.data:
                dist_nearest_center = min([self.dist(point, center) for center in centers])
                distances.append((point, dist_nearest_center))  # tuple

            next_center = max(distances, key=lambda x: x[1])    # compare all the possibel distances and choose the max, so the second arg in tup;e
            centers.append(next_center)
        return centers
    
    # kmeans++ -> DOUBLE CHECK THIS
    def kmeanspp(self):
        # centers are intialized to accelerate convergence
        # start with random center and define d as distance between a point and the closest center to c, choose next center proportional to d^2
        random_start = np.random.choice(len(self.data))
        centers = [self.data[random_start]]
        for i in range(1, self.k):
            dofx = []
            for point in self.data:
                dist_nearest_center = min([self.dist(point, center) for center in centers])
                dofx.append((point, dist_nearest_center))
            dsquared = [(d[0], d[1] ** 2) for d in dofx]
            next_center = max(dsquared, key=lambda x: x[1])
            centers.append(next_center)
        return centers
    
    # manual -> check back on how this changes plotting
    def manual(self):
        pass
    # man_centers = []
    # def manual(self):
    #     global man_centers
    #     man_centers = []

    #     def onclick(event):
    #         x, y = event.xdata, event.ydata
    #         if x is not None and y is not None:
    #             man_centers.append([x, y])
    #             plt.scaterr(x, y, color='red',marker='x')
    #             plt.draw()
    #             if len(man_centers == self.k):
    #                 plt.close()
    #     fig, ax = plt.subplots()
    #     ax.scatter(self.data[:, 0], self.data[:, 1], color='blue')
    #     fig.canvas.mpl_connect('button_press_event', onclick)
    #     plt.title("Click to select centroids")
    #     plt.show()
    
    #     return man_centers


    def make_clusters(self, centers):
        # for i in range(len(self.assignment)):
        #     dist = float('inf')
        #     for j in range(self.k):     # j represents the clusters
        #         if self.isUnassigned(i):
        #             self.assignment[i] = j      # assign point i to a cluster if it doesn;t have
        #             dist = self.dist(centers[j], self.data[i])
        #         else:
        #             new_dist = self.dist(centers[j], self.data[i])
        #             if new_dist < dist:
        #                 self.assignment[i] = j
        #                 dist = new_dist
        #     # after you are done evaluating one point, reset distance?
        #     # but hsould be a huge number since we are lookign for smaller distances 
        #     dist = float('inf')
        for i in range(len(self.assignment)):
            dist = float('inf')
            for j in range(self.k):
                new_dist = self.dist(centers[j], self.data[i])
                if new_dist < dist:
                    self.assignment[i] = j
                    dist = new_dist
    
    def isUnassigned(self, i):
        return self.assignment[i] == -1

    def compute_centers(self):
        # for i in range(self.k):
        #     cluster = []
        #     for j in range(len(self.assignment)):
        #         if self.assignment[j] == i:
        #             cluster.append(self.data[i])
        #     centers.append(np.mean(np.array(cluster), axis = 0))
        # return np.array(centers)
        centers = []
        for i in range(self.k):
            cluster = [self.data[j] for j in range(len(self.assignment)) if self.assignment[j] == i]
            if len(cluster) > 0:
                centers.append(np.mean(cluster, axis=0))
        return np.array(centers)

    def unassign(self):
        self.assignment = [-1 for _ in range(len(self.data))]

    def is_diff(self, centers, new_centers):
        for i in range(self.k):
            if self.dist(centers[i], new_centers[i]) > 1e-6: #!= 0:
                return True
        return False

    def dist(self, x, y):
        # euclidean distance
        return (sum((x - y)**2)) ** 0.5
    
    # now we also care about convergence
    def converged(self, centers, new_centers):
        for i in range(len(centers)):
            if self.dist(centers[i], new_centers[i]) == 0:
                return True
        return False
    
    def get_plot_data(self, centers):
        cluster_data = []
        for i in range(self.k):
            cluster_points = self.data[self.assignment == i]
            cluster_data.append({
                "x": cluster_points[:, 0],
                "y": cluster_points[:, 1],
                "name": f"Cluster {i}",
                "marker": {'color': f'rgb({np.random.randint(0, 255)}, {np.random.randint(0, 255)}, {np.random.randint(0, 255)})'}
            })
        center_data = {
            "x": centers[:, 0],
            "y": centers[:, 1],
            "name": "Centers",
            "marker": {'color': 'red', 'size': 12, 'symbol': 'x'}
        }
        return {"cluster": cluster_data, "centers": center_data}


# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/kmeans/<int:k>')
# def kmeans_route(k):
#     history = run_kmeans(k)
#     print(history)  # Add this line to check if data is returned
#     return history

# def run_kmeans(k):
#     kmeans = KMeans(X, k)   # remeber X is that global data set from above
#     history = kmeans.lloyds()
#     transformed_history = []
#     for step in history:
#         transformed_step = {
#             'clusters': step['cluster'],
#             'centers': step['centers']
#         }
#         transformed_history.append(transformed_step)
#     return jsonify(transformed_history)


# if __name__ == '__main__':
#     app.run(debug=True)

# stuff lance had that idk howwwww tooooo useeeeeeeee
# kmeans = KMeans(X, 6)
# kmeans.lloyds()
# images = kmeans.snaps

# images[0].save(
#     'kmeans.gif',
#     optimize=False,
#     save_all=True,
#     append_images=images[1:],
#     loop=0,
#     duration=500
# )