import pandas as pd
import numpy as np
import tensorflow.compat.v1 as tf
from flask import Flask,jsonify,request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

tf.disable_v2_behavior()

df_clean = pd.read_csv("clean_data.csv")
df_games = pd.read_csv("df_games.csv")
train_list = []

i = 0
usergroup = df_clean.groupby('userid')
usergroup.head()
train_key_list = []
train_val_list = []
for userID, cur in usergroup:
  train_key_list.append(userID)
  temp = [0]*len(df_games) # temp that stores every game's hours played
  
  for no, game in cur.iterrows():
    temp[game['game_index']] = game['hoursplayed']
    i+=1
  train_val_list.append(temp)
  train_list.append(temp)


# Setting the models Parameters
hiddenUnits = 50
visibleUnits = len(df_clean['game'].unique())
vb = tf.placeholder(tf.float32, [visibleUnits])  
hb = tf.placeholder(tf.float32, [hiddenUnits]) 
W = tf.placeholder(tf.float32, [visibleUnits, hiddenUnits]) 

# Phase 1: Input Processing
v0 = tf.placeholder("float", [None, visibleUnits])
_h0 = tf.nn.sigmoid(tf.matmul(v0, W) + hb)  
h0 = tf.nn.relu(tf.sign(_h0 - tf.random_uniform(tf.shape(_h0)))) 

# Phase 2: Reconstruction
_v1 = tf.nn.sigmoid(tf.matmul(h0, tf.transpose(W)) + vb) 
v1 = tf.nn.relu(tf.sign(_v1 - tf.random_uniform(tf.shape(_v1))))
h1 = tf.nn.sigmoid(tf.matmul(v1, W) + hb)

# Learning rate
alpha = 1

# Create the gradients
w_pos_grad = tf.matmul(tf.transpose(v0), h0)
w_neg_grad = tf.matmul(tf.transpose(v1), h1)

# Calculate the Contrastive Divergence to maximize
CD = (w_pos_grad - w_neg_grad) / tf.to_float(tf.shape(v0)[0])

# Create methods to update the weights and biases
update_w = W + alpha * CD
update_vb = vb + alpha * tf.reduce_mean(v0 - v1, 0)
update_hb = hb + alpha * tf.reduce_mean(h0 - h1, 0)

# Set the error function, here we use Mean Absolute Error Function
err = v0 - v1
err_sum = tf.reduce_mean(err*err)
cur_w = np.zeros([visibleUnits, hiddenUnits], np.float32)

cur_vb = np.zeros([visibleUnits], np.float32)

cur_hb = np.zeros([hiddenUnits], np.float32)

prv_w = np.zeros([visibleUnits, hiddenUnits], np.float32)

prv_vb = np.zeros([visibleUnits], np.float32)

prv_hb = np.zeros([hiddenUnits], np.float32)
sess = tf.Session()
sess.run(tf.global_variables_initializer())

epochs = 30
batchsize = 150
errors = []
for i in range(epochs):
    for start, end in zip(range(0, len(train_list), batchsize), range(batchsize, len(train_list), batchsize)):
        batch = train_list[start:end]
        cur_w = sess.run(update_w, feed_dict={v0: batch, W: prv_w, vb: prv_vb, hb: prv_hb})
        cur_vb = sess.run(update_vb, feed_dict={v0: batch, W: prv_w, vb: prv_vb, hb: prv_hb})
        cur_hb = sess.run(update_hb, feed_dict={v0: batch, W: prv_w, vb: prv_vb, hb: prv_hb})
        prv_w = cur_w
        prv_vb = cur_vb
        prv_hb = cur_hb
    errors.append(sess.run(err_sum, feed_dict={v0: train_list, W: cur_w, vb: cur_vb, hb: cur_hb}))
    print(errors[-1])

def get_dummy(req):

    user = np.zeros(5155)

    for i in req:
        print(int(i["game_index"]))
        user[int(i["game_index"])] = int(i["hours_played"])

    input = np.reshape(user, (1,5155)).tolist()

    return input

@app.route("/predict", methods=['POST'])
@cross_origin()
def predict():
    req = request.json
    input = get_dummy(req["games"])

    output = np.array([])

    for i in range(len(input[0])):
        if input[0][i] > 0:
            output = np.append(output,i)

    hh0 = tf.nn.sigmoid(tf.matmul(v0, W) + hb)
    vv1 = tf.nn.sigmoid(tf.matmul(hh0, tf.transpose(W)) + vb)
    feed = sess.run(hh0, feed_dict={v0: input, W: prv_w, hb: prv_hb})
    rec = sess.run(vv1, feed_dict={hh0: feed, W: prv_w, vb: prv_vb})
    inputuser_games = df_games
    inputuser_games["recommendation_score"] = rec[0]
    game = inputuser_games.sort_values(["recommendation_score"], ascending=False)

    ret = []
    i = 0
    for g in game["game_index"]:
        if g not in output:
            ret.append(g)
            i += 1
        if(i >= 5):
            break
    return jsonify({'result': ret})
