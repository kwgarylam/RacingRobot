import numpy as np
import theano
import cv2
import lasagne
import theano.tensor as T
from sklearn.model_selection import train_test_split

from train import loadDataset, buildMlp

seed = 42
np.random.seed(seed)
folder = 'cropped'
# Arrow keys
UP_KEY = 82
DOWN_KEY = 84
RIGHT_KEY = 83
LEFT_KEY = 81
EXIT_KEYS = [113, 27]  # Escape and q

X, y_true, images, factor = loadDataset(seed=seed, split=False)
indices = np.arange(len(X))
idx_train, idx_test = train_test_split(indices, test_size=0.4, random_state=seed)
idx_val, idx_test  = train_test_split(idx_test, test_size=0.5, random_state=seed)

input_var = T.matrix('inputs')
input_dim = X.shape[1]
network = buildMlp(input_var, input_dim)

with np.load('model.npz') as f:
    param_values = [f['arr_%d' % i] for i in range(len(f.files))]
lasagne.layers.set_all_param_values(network, param_values)

test_prediction = lasagne.layers.get_output(network, deterministic=True)
pred_fn = theano.function([input_var], test_prediction)

y_test = pred_fn(X)
current_idx = 0

while True:
    name = images[current_idx]
    im = cv2.imread('{}/{}'.format(folder, images[current_idx]))

    text = "train"
    if current_idx in idx_val:
        text = "val"
    elif current_idx in idx_test:
        text = "test"
    cv2.putText(im, text, (0,20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255,255,255))

    # x_center, y_center = map(int, name.split('_')[0].split('-'))
    height, width, n_channels = im.shape
    x_true = int(y_true[current_idx] * width * factor)
    x_center =int(y_test[current_idx][0] * (width * factor))
    x_center = np.clip(x_center, 0, width)
    y_center = height // 2
    print(name, "error={}".format(abs(x_center - x_true)))
    # Draw prediction and true center
    cv2.circle(im, (x_center, y_center), radius=10, color=(0,0,255),
               thickness=2, lineType=8, shift=0)
    cv2.circle(im, (x_true, y_center), radius=10, color=(255,0,0),
               thickness=1, lineType=8, shift=0)
    cv2.imshow('Predicition', im)
    key = cv2.waitKey(0) & 0xff
    if key in EXIT_KEYS:
        cv2.destroyAllWindows()
        break
    elif key in [LEFT_KEY, RIGHT_KEY]:
        current_idx += 1 if key == RIGHT_KEY else -1
        current_idx = np.clip(current_idx, 0, len(images)-1)
