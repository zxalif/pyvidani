import numpy as np  # noqa
import cv2
import glob
import sys
import os

FRAME_DIRECTORY = "./frames/"


def extract_frames(video):
    cap = cv2.VideoCapture(video)
    counter = 0
    ret = True

    while(cap.isOpened() and ret):
        ret, frame = cap.read()

        if ret:
            cv2.imwrite("./{}/{}.png".format(FRAME_DIRECTORY, counter), frame)
            counter += 1


class Frame:
    def __init__(self, frame):
        self.frame = frame

    def normalize(self):
        _max = max(self.frame)
        _min = min(self.frame)
        median = (_max + _min) / 2
        return map(lambda x: 1 if x >= median else 0, self.frame)


def get_next_index(data, item, last_index):
    """Return next index from current index of an Item"""
    for index in range(last_index + 1, len(data)):
        if data[index] == item:
            last_index = index
            break
    return last_index


def cluster_item(data, item, index):
    remaining_items = data[index:]
    if item not in remaining_items: return [], None, None
    start_index = remaining_items.index(item)  # 1
    last_index = start_index
    done = False
    while not done:
        _last_index = get_next_index(remaining_items[:], item, last_index)
        if last_index + 1 == _last_index:
            last_index = _last_index
        else:
            done = True
            break
    position = len(data) - len(remaining_items) + start_index
    _last_index = len(data) - len(remaining_items) + start_index + last_index + 1
    return remaining_items[start_index:last_index + 1], position, _last_index


def sub_list_for_item(data, item):
    if item not in data:
        return {}
    pixels = []
    index = data.index(item)
    done = False
    next_index = index
    tmp = []
    while not done:
        sub, _start, next_index = cluster_item(data[:], item, next_index)
        done = _start in tmp
        if not sub: break
        if _start not in tmp:
            tmp.append(_start)
            pixels.append((_start, len(sub)))
    return pixels


def snap(data, ruler=3):
    div = len(data) // ruler
    mod = len(data) % ruler
    return [data[0] for _ in range(div + mod)]


def row_squash(data, ruler=3):
    """ Small ruler will perform more better"""
    _rev = data[::-1]
    _rev_data = []
    for i in range(0, len(_rev), int(ruler)):
        _rev_sub = _rev[i:i + int(ruler)]
        _rev_data.append(max(_rev_sub, key=_rev_sub.count))
    return _rev_data[::-1]


def column_squash(data, ruler=9):
    _rev = data[::-1]
    _rev_data = []
    for i in range(0, len(_rev), int(ruler)):
        _temp = []
        _y = _rev[i:i + int(ruler)]
        for args in zip(*_y):
            _max = max(args, key=args.count)
            _temp.append(_max)
        _rev_data.append(_temp)
    return _rev_data[::-1]


def rowsnap(data, width=80):
    row = row_squash(data, ruler=len(data) / width)
    return row


def columnsnap(data, height=28):
    columns = column_squash(data[:], ruler=len(data) / height)
    return columns


def pprint():
    images = glob.glob("./{}/*.png".format(FRAME_DIRECTORY))
    sorted_images = sorted([int(i.split('/')[-1].split('.')[0]) for i in images])
    os.system("clear")

    for file in sorted_images:
        file = "./{}/{}.png".format(FRAME_DIRECTORY, file)
        img = cv2.imread(file, 0)
        img = img.tolist()

        for index, item in enumerate(img):
            box = Frame(item)
            img[index] = list(box.normalize())

        img = columnsnap(img[:])
        _i = []

        for index, _img in enumerate(img):
            _img = rowsnap(_img[:], width=80)
            _write = "".join(map(str, _img)).replace("0", ".")
            _i.append(_write)

        # clear the previous buffer
        for _ in range(len(_i)):
            sys.stdout.write("\x1b[1A\x1b[2K")

        # write each row of a frame
        for img_row in _i:
            sys.stdout.write(img_row + "\n")
    for image in images: os.remove(image)


def main(file):
    extract_frames(file)
    pprint()


if __name__ == '__main__':
    main("./sample/horse-riding.mp4")
