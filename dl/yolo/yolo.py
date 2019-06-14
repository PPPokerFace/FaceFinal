from .models import *
from .utils.datasets import *
from .utils.utils import *
import time
from django.conf import settings
from torchvision import transforms as trans


class YOLO:
    def __init__(self):
        # Not support multi gpus Now
        # self.GPUs = "0,1"
        # os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        # Path to cfg file. Filename must ends with .cfg .
        self.cfg = os.path.join(BASE_DIR, 'cfg', settings.YOLO_CFG)

        # Path to weights file . Filename must ends with .pt , not support .weight .
        self.weights = os.path.join(BASE_DIR, 'cfg', settings.YOLO_MODEL)

        # Path to names file .
        self.names = os.path.join(BASE_DIR, 'cfg', 'face.names')

        # The image size the yolo runs .
        self.img_size = settings.YOLO_IMAGE_SIZE

        # The confidence threshold .
        self.conf_thres = 0.3

        # The num threshold .
        self.nms_thres = 0.45

        self.device = torch_utils.select_device()

        # init the model
        self.model = Darknet(self.cfg, self.img_size)

        if self.weights.endswith('.pt'):  # pytorch format
            self.model.load_state_dict(torch.load(self.weights, map_location=self.device)['model'])

        self.model.to(self.device).eval()

        self.classes = load_classes(self.names)

        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.classes))]

    def loadModel(self, cfg, weights, img_size):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.cfg = os.path.join(BASE_DIR, 'cfg', cfg)
        self.weights = os.path.join(BASE_DIR, 'cfg', weights)
        try:
            self.img_size = img_size
            self.model = Darknet(self.cfg, img_size)
            self.model.load_state_dict(
                torch.load(self.weights, map_location=self.device)['model'])
            self.model.to(self.device).eval()
        except:
            return False
        return True

    def prepare_image(self, frame, auto=False):
        # Padded resize

        if auto == True:
            image, _, _, _ = letterbox(frame, new_shape=self.img_size, mode="auto")
        else:
            if isinstance(self.img_size, int):
                image, _, _, _ = letterbox(frame, new_shape=self.img_size, mode="square")
            else:
                image, _, _, _ = letterbox(frame, new_shape=self.img_size, mode="rect")

        if False:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            t = trans.Compose([
                trans.ToTensor()])

            image = t(image)

            return image

        else:
            # Normalize RGB
            image = image[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB
            image = np.ascontiguousarray(image, dtype=np.float32)  # uint8 to float32
            image /= 255.0  # 0 - 255 to 0.0 - 1.0

            # Get detections
            image = torch.from_numpy(image)  # .unsqueeze(0)
            return image

    def prepare_image_auto(self, frame):
        # Padded resize
        image=None
        # Normalize RGB
        image = image[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB
        image = np.ascontiguousarray(image, dtype=np.float32)  # uint8 to float32
        image /= 255.0  # 0 - 255 to 0.0 - 1.0

        # Get detections
        image = torch.from_numpy(image)  # .unsqueeze(0)
        return image

    def predict(self, image, image_size: list):
        # Convert the image from ndarray to tensor
        if isinstance(image, np.ndarray) and len(image.shape) == 4:
            image = torch.from_numpy(image)

        # Convert the image from ndarray to tensor
        if isinstance(image, np.ndarray) and len(image.shape) == 3:
            image = torch.from_numpy(image)

        if isinstance(image, torch.Tensor) and len(image.shape) == 3:
            image = image.unsqueeze(0)

        # Now the image type must be tensor
        if not isinstance(image_size, list):
            image_size = [image_size]

        if isinstance(image_size, list) and image.shape[0] != len(image_size):
            assert "The number of images not equals the length of image_size list"

        # Normalize the type of image_size
        for single_img_size in image_size:
            # Convert the shape from size to size,size
            if isinstance(single_img_size, int):
                frame_shape = (single_img_size, single_img_size)

            # Convert the shape from height,width,channel to height,width
            elif isinstance(single_img_size, np.ndarray) and len(single_img_size.shape) == 3:
                frame_shape = (single_img_size, single_img_size)

        image = image.to(self.device)
        pred,_ = self.model(image)

        # set boxes < threshold to zero ...
        # And the after one only works for batch equals one .
        pred[pred[:, :, 4] < self.conf_thres] = 0
        # pred = pred[pred[:, :, 4] > self.conf_thres]  # remove boxes < threshold

        # Output is a list for every batch .
        # [ Tensor, Tensor ]
        detections = non_max_suppression(pred, self.conf_thres, self.nms_thres)
        ret = []
        # For every batch
        for img,detection, single_img_size in zip(image,detections, image_size):
            if detection is None:
                ret.append([])
                continue
            box = detection[:, :4]  # xyxy
            scale_coords(img.shape[1:], box, single_img_size).round()  # to original shape

            # For every bbox , the type is xmin,ymin,xmax,ymax,conf,score,classesid.
            # The ret is looks like :[[[130.06, 114.47, 209.84, 218.75, 0.7499187588691711, 1.0, 0.0]]]
            ret.append(detection.cpu().detach().numpy())

        end = time.time()
        return ret

        # The code just works on batch = 1
        if len(pred) > 0:
            # Run NMS on predictions
            non_max_suppression(pred, self.conf_thres, self.nms_thres)[0]
            # Rescale boxes from 416 to true image size
            scale_coords(self.img_size, detections[:, :4], frame_shape).round()

            # Draw bounding boxes and labels of detections
            for *xyxy, conf, cls_conf, cls in detections:
                ret.append([xyxy[0], xyxy[1], xyxy[2], xyxy[3], self.classes[int(cls)], conf])
                # Add bbox to the image
#                label = '%s %.2f' % (self.classes[int(cls)], conf)
#                plot_one_box(xyxy, frame, label=False, color=self.colors[int(cls)])
#           cv2.imwrite("frame.jpg", frame)
