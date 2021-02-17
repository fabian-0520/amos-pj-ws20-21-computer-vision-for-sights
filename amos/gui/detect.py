import argparse
import logging
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


class Detection:
    def __init__(self) -> None:
        """Creates new configured instance for the detection process."""
        self.detection = True

    def disable_detection(self) -> None:
        """Disables the detection process."""
        self.detection = False

    def enable_detection(self) -> None:
        """Enables the detection process."""
        self.detection = True

    def detect(self, app, weights, source='data/images', image_size=736, debug=False):
        """ Detects the image or video of the given source by using the specified weights.

        Parameters
        ----------
        weights: str
            Weights path.
        source: str
            Source of the detection. 0 for webcam.
        image_size: int
            Inference size (pixels).
        debug: bool
            Whether the debug mode is on.
        """
        print(f'Detecting using weights: {weights}')
        source = str(source)
        imgsz = image_size
        opt_project = 'runs/detect'
        opt_name = 'exp'
        opt_exist_ok = False
        opt_device = ''
        opt_augment = False
        opt_conf_thres = 0.25
        opt_iou_thres = 0.01
        opt_classes = 0
        opt_agnostic_nms = True
        opt_save_conf = False
        webcam = False

        if source.isnumeric() or source.endswith('.txt') or source.lower().startswith(('rtsp://', 'rtmp://', 'http://')):
            print(source)
            webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
                ('rtsp://', 'rtmp://', 'http://'))

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
            cudnn.benchmark = True  # set True to speed up constant image size inference
            dataset = LoadStreams(source, img_size=imgsz)
            print("webcam")  # debug
            logging.debug("webcam")
        else:
            dataset = LoadImages(source, img_size=imgsz)
            print("image")  # debug

        # Get names and colors
        names = model.module.names if hasattr(model, 'module') else model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

        # Run inference
        t0 = time.time()
        img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
        _ = model(img.half() if half else img) if device.type != 'cpu' else None  # run once
        logging.debug("start inference")
        for path, img, im0s, vid_cap in dataset:
            if self.detection is False and webcam is True:
                logging.debug("kill thread")
                dataset.kill_thread()
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

                #p = Path(p)  # to Path
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
                        logging.debug('Prediction: {}; Confidence {}'.format(f'{names[int(cls)]}', f'{conf:.2f}'))
                        label = ''.join(map(lambda x: x if x.islower() else ' ' + x, names[int(cls)]))
                        label = f'{label} {conf:.2f}' if debug else label
                        if debug:
                            plot_one_box(xyxy,
                                            im0,
                                            label=label,
                                            color=colors[int(cls)],
                                            line_thickness=3)
                        plot_one_point(xyxy,
                                        im0,
                                        label=label,
                                        color=colors[int(cls)],
                                        point_thickness=None,
                                        r=10)


                app.image = QImage(bytearray(im0), im0.shape[1], im0.shape[0], QImage.Format_RGB888).rgbSwapped()
                app.Label_Bild.setPixmap(QPixmap(app.image))
                time.sleep(1/60)

                # Print time (inference + NMS)
                print(f'{s}Done. ({t2 - t1:.3f}s)')

        logging.debug(f'Done. ({time.time() - t0:.3f}s)')
        print(f'Done. ({time.time() - t0:.3f}s)')
