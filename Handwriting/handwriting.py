import os
import sys
from datetime import datetime

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from skimage.transform import resize
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

TEST_CASE = '01_kevin_ferranti'
TEST_SUB_CASE = '00_wie_im_buch'

RESULT_FOLDER = 'result'
TEST_FOLDER = 'test'
TEST_PATH = '{0}/{1}'.format(TEST_FOLDER, TEST_CASE)
RESULT_PATH = '{0}/{1}'.format(RESULT_FOLDER, TEST_CASE)

CSV_FILE = '{0}/{1}.csv'.format(RESULT_PATH, TEST_SUB_CASE)
os.makedirs(os.path.dirname(CSV_FILE), exist_ok=True)
sys.stdout = open(CSV_FILE, 'w')

CREATE_IMAGE_FILES = True

TEST_SIZE = 0.5
RANDOM_STATE_TEST = 42
HIDDEN_LAYER_SIZES = 1000
MAX_ITER = 10000
ALPHA = 1e-5
SOLVER = 'adam'
TOL = 1e-4
RANDOM_STATE = 1
LEARNING_RATE_INIT = 1e-1

CREATION_TIME = 0
ITERATION_AMOUNT = 0


def create_neuronal_network():
    digits = datasets.load_digits()

    # Rescale the data and split into training and test sets
    X, y = digits.data / 255., digits.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE_TEST)

    # Redirect stdout to mlp log file
    mlp_logfile = '{0}/mlp.log'.format(RESULT_PATH)
    os.makedirs(os.path.dirname(mlp_logfile), exist_ok=True)
    sys.stdout = open(mlp_logfile, 'w')

    mlp = MLPClassifier(hidden_layer_sizes=(HIDDEN_LAYER_SIZES,), max_iter=MAX_ITER, alpha=ALPHA,
                        solver=SOLVER, verbose=10, tol=TOL, random_state=RANDOM_STATE,
                        learning_rate_init=LEARNING_RATE_INIT)

    mlp.fit(X_train, y_train)

    sys.stdout = open(CSV_FILE, 'w')

    # Read last line of output of mlp training
    logfile = open(mlp_logfile, 'r')
    lines = logfile.readlines()
    logfile.close()

    iteration_amount = 0

    if SOLVER == 'adam':
        lastline = None
        for line in lines:
            if 'Iteration' in line:
                lastline = line
        print(lastline.split('loss')[0])
        iteration_amount = iteration_amount + int(lastline.split('Iteration')[1].split(',')[0])

    print("Training set score: {0}".format(mlp.score(X_train, y_train)))
    print("Test set score: {0}".format(mlp.score(X_test, y_test)))

    return [X_test, y_test, mlp, iteration_amount]


def plot_two_images(image1, image2, target_file):
    fig, axes = plt.subplots(nrows=1, ncols=2)
    ax = axes.ravel()
    ax[0].imshow(image1, cmap='gray')
    ax[0].set_title("Original image")
    ax[1].imshow(image2, cmap='gray')
    ax[1].set_title("Resized image")

    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    plt.savefig(target_file)
    plt.close(fig)


def rgb2gray(rgb):
    return np.dot(rgb[..., :3], [0.299, 0.587, 0.114])


def predict_testdata(mlp, sub_folder):
    print()

    paint_net_file_name = './{0}/{1}/paint_net-info.txt'.format(TEST_PATH, sub_folder)
    if os.path.isfile(paint_net_file_name):
        file_paint_net_info = open(paint_net_file_name, 'r')
        print(file_paint_net_info.read())

    print()

    wrong_numbers_map = {}

    for number in range(10):
        img = mpimg.imread('./{0}/{1}/{2}.png'.format(TEST_PATH, sub_folder, number))
        gray = rgb2gray(np.asarray(img))

        gray_resized = resize(gray, (8, 8), anti_aliasing=True)

        if CREATE_IMAGE_FILES:
            plot_two_images(gray, gray_resized, './{0}/{1}/{2}.png'.format(
                RESULT_PATH, sub_folder, number))

        a = (16 - gray_resized * 16).astype(int)  # really weird here, but try to convert to 0..16
        predicted = mlp.predict(a.flatten().reshape(1, -1))

        if predicted == number:
            predicted_same = True
        else:
            predicted_same = False
            wrong_numbers_map[number] = predicted[0]

        print('{0}x{1};{2};{3};{4}'.format(sub_folder, sub_folder, number, predicted[0], predicted_same))

    print('{0};{1}'.format('wrong prediction amount', len(wrong_numbers_map.keys())))
    return wrong_numbers_map


def join_wrong_numbers_map(map1, map2):
    for key in map2.keys():
        if key not in map1.keys():
            map1[key] = []

        map1[key].append(map2[key])


def format_occasions_of_number(numbers):
    num_map = {}
    for number in numbers:
        if number not in num_map.keys():
            num_map[number] = 0

        num_map[number] = num_map[number] + 1

    result = ""
    for number in num_map.keys():
        result = result + '{0}->{1}'.format(number, num_map[number])
        result = result + ';'
    return result


def calculate_test_result_value(wrong_numbers_map):
    test_result = 0

    for key in wrong_numbers_map.keys():
        numbers = wrong_numbers_map[key]
        num_map = {}
        for number in numbers:
            if number not in num_map.keys():
                num_map[number] = 0

            num_map[number] = num_map[number] + 1

        for number in num_map.keys():
            test_result = test_result + num_map[number]

    return test_result


start_time = datetime.timestamp(datetime.now())
X_test, y_test, mlp, iteration_amount = create_neuronal_network()
end_time = datetime.timestamp(datetime.now())
CREATION_TIME = CREATION_TIME + (end_time - start_time)

print('{0};{1}'.format('time for creation', CREATION_TIME))

print()

wrong_numbers_map = {}

sub_folders = [8, 25, 50, 100, 150, 180, 200, 220, 250, 300, 350, 400]
# sub_folders = [1, 2, 3, 5]
# sub_folders = [1, 2, 3, 4]
amount_of_tests = len(sub_folders) * 10

for sub_folder in sub_folders:
    join_wrong_numbers_map(wrong_numbers_map, predict_testdata(mlp, sub_folder))

print()
for key in sorted(wrong_numbers_map.keys(), key=int):
    print('{0};{1};{2};{3}'.format(
        'number of mismatch',
        key,
        len(wrong_numbers_map[key]),
        format_occasions_of_number(wrong_numbers_map[key])))

test_result_value = calculate_test_result_value(wrong_numbers_map)
print('{0};{1}'.format('amount of errors', test_result_value))

# write into total result file
total_result_file = '{0}/total_result.csv'.format(RESULT_PATH)

if not os.path.isfile(total_result_file):
    os.makedirs(os.path.dirname(total_result_file), exist_ok=True)
    file = open(total_result_file, 'a')
    file.write('{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14}\n'.format(
        'FILE_NAME',
        'TEST_SIZE', 'RANDOM_STATE_TEST',
        'HIDDEN_LAYER_SIZES', 'MAX_ITER', 'ALPHA', 'SOLVER', 'TOL', 'RANDON_STATE', 'LEARNING_RATE_INIT',
        'Anzahl Ausgewertet', 'Anzahl Fehler', 'Fehlerprozentsatz',
        'Dauer Erstellung', 'Anzahl Iterationen'))
    file.close()

file = open(total_result_file, 'a')
file.write('{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14}\n'.format(
    TEST_SUB_CASE,
    TEST_SIZE, RANDOM_STATE_TEST,
    HIDDEN_LAYER_SIZES, MAX_ITER, ALPHA, SOLVER, TOL, RANDOM_STATE, LEARNING_RATE_INIT,
    amount_of_tests, test_result_value, test_result_value / amount_of_tests * 100,
    CREATION_TIME, iteration_amount))
file.close()
