"""This module contains helper functions for the main app module."""
import os
import argparse
import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import check_img_size, non_max_suppression, apply_classifier, scale_coords, xyxy2xywh, \
    set_logging, increment_path, strip_optimizer
from utils.plots import plot_one_box, plot_one_point
from utils.torch_utils import select_device, load_classifier, time_synchronized

from PyQt5.QtGui import QImage, QPixmap

detection = True

def wipe_prediction_input_images(images_base_path: str) -> None:
    """Wipes the passed images load directory clean of any existing files.

    Parameters
    ----------
    images_base_path: str
        Directory for input images for prediction.
    """
    # delete images from data
    if os.path.isdir(images_base_path):
        for file in os.listdir(images_base_path):
            os.remove(f'{images_base_path}/{file}')

    # create images directory
    else:
        os.makedirs(images_base_path)


def get_current_prediction_output_path(prediction_output_base_path: str, image_name: str) -> str:
    """Returns the path of the current prediction output images.

    Parameters
    ----------
    prediction_output_base_path: str
        Prediction output base path.
    image_name: str
        Name of the image.

    Returns
    -------
    output_path: str
        Output path in which the predicted images are inserted.
    """
    dirs = [(prediction_output_base_path + d) for d in os.listdir(prediction_output_base_path)]
    newest_dir = max(dirs, key=os.path.getmtime)
    return newest_dir + '/' + image_name.replace('/', '')


def enable_detection() -> None:
    detection = True


def disable_detection() -> None:
    detection = False


def detect(app, weights='weights/Berlin.pt', source='data/images', image_size=640):
    """ Detects the image or video of the given source by using the specified weights.

    Parameters
    ----------
    weights: str
        Weights path.
    source: str
        Source of the detection. 0 for webcam.
    image_size: int
        Inference size (pixels).
    """
    source = str(source)
    imgsz = image_size
    save_img = True
    opt_project = 'runs/detect'
    opt_name = 'exp'
    opt_exist_ok = False
    opt_device = ''
    opt_augment = False
    opt_conf_thres = 0.25
    opt_iou_thres = 0.45
    opt_classes = 0
    opt_agnostic_nms = False
    opt_save_conf = False
    view_img = False
    save_txt = False
    webcam = False

    if source.isnumeric() or source.endswith('.txt') or source.lower().startswith(('rtsp://', 'rtmp://', 'http://')):
        print(source)
        webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
            ('rtsp://', 'rtmp://', 'http://'))

    # Directories
    save_dir = Path(increment_path(Path(opt_project) / opt_name, exist_ok=opt_exist_ok))  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Initialize
    set_logging()
    device = select_device(opt_device)
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=device)['model']).to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = True
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz)
        print("webcam")  # debug
    else:
        save_img = True
        dataset = LoadImages(source, img_size=imgsz)
        print("image")  # debug

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

    # Run inference
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
    for path, img, im0s, vid_cap in dataset:
        if webcam is True and detection is False:
            break
        img = torch.from_numpy(img).to(device)
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        t1 = time_synchronized()
        pred = model(img, augment=opt_augment)[0]

        # Apply NMS
        pred = non_max_suppression(pred, opt_conf_thres, opt_iou_thres, classes=opt_classes, agnostic=opt_agnostic_nms)
        t2 = time_synchronized()

        # Apply Classifier
        if classify:
            pred = apply_classifier(pred, modelc, img, im0s)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if webcam:  # batch_size >= 1
                p, s, im0, frame = path[i], '%g: ' % i, im0s[i].copy(), dataset.count
            else:
                p, s, im0, frame = path, '', im0s, getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # img.jpg
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # img.txt
            s += '%gx%g ' % img.shape[2:]  # print string
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f'{n} {names[int(c)]}s, '  # add to string

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_txt:  # Write to file
                        xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                        line = (cls, *xywh, conf) if opt_save_conf else (cls, *xywh)  # label format
                        with open(txt_path + '.txt', 'a') as f:
                            f.write(('%g ' * len(line)).rstrip() % line + '\n')

                    if save_img or view_img:  # Add bbox to image
                        print('successfull')
                        label = f'{names[int(cls)]} {conf:.2f}'
                        plot_one_point(xyxy, im0, label=label, color=colors[int(cls)], point_thickness=None, r=10)
                        #rgbImage = cv2.cvtColor(im0, cv2.COLOR_BGR2RGB)
                        #convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0],
                        #                 QImage.Format_RGB888)
                        #convertToQtFormat = QPixmap.fromImage(convertToQtFormat)
                        #app.Label_Bild.setPixmap(QPixmap(convertToQtFormat))
                        #detectList.append([xyxy, im0.shape, label])

                        app.image = QImage(bytearray(im0), im0.shape[1], im0.shape[0], QImage.Format_RGB888).rgbSwapped()
                        # show prediction in UI
                        app.Label_Bild.setPixmap(QPixmap(app.image))
            time.sleep(1)

            # Print time (inference + NMS)
            print(f'{s}Done. ({t2 - t1:.3f}s)')

            # Stream results
            #if view_img:
            #    cv2.imshow(str(p), im0)

            # convert detected_image into PyQT format
            #app.image = QImage(bytearray(im0), im0.shape[1], im0.shape[0], QImage.Format_RGB888).rgbSwapped()
            # show prediction in UI
            #app.Label_Bild.setPixmap(QPixmap(app.image))

            # Save results (image with detections)
            """if save_img:
                print('dataset.mode: ' + dataset.mode)  # debug
                if dataset.mode == 'image' or dataset.mode == 'images':
                    cv2.imwrite(save_path, im0)
                else:  # 'video'
                    if vid_path != save_path:  # new video
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()  # release previous video writer

                        fourcc = 'mp4v'  # output video codec
                        fps = vid_cap.get(cv2.CAP_PROP_FPS)
                        w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
                    vid_writer.write(im0)"""

    if save_txt or save_img:
        s = f"\n{len(list(save_dir.glob('labels/*.txt')))} labels saved to {save_dir / 'labels'}" if save_txt else ''
        print(f"Results saved to {save_dir}{s}")

    print(f'Done. ({time.time() - t0:.3f}s)')
