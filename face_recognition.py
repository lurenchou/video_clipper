import models
import os

try:
    import cPickle as pickle
except ImportError:
    import pickle

import dlib
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import click


def recognition(video_file_path, face_classifier_file_path, skipped_duration, frame_scale_rate):
    cnn_face_detector = dlib.cnn_face_detection_model_v1(models.cnn_face_detector_model_location())
    sp = dlib.shape_predictor(models.pose_predictor_model_location())
    face_rec = dlib.face_recognition_model_v1(models.face_recognition_model_location())

    font = ImageFont.truetype('C:\\Users\\cai\\AppData\\Local\\Microsoft\\Windows\\Fonts\\SourceHanSansSC-Regular.otf', 14)  # todo 改成思源黑体

    with open(face_classifier_file_path, 'rb') as infile:
        (model, class_names) = pickle.load(infile)

    vid = cv2.VideoCapture(video_file_path)

    if skipped_duration is not None:
        vid.set(0, skipped_duration * 1000)

    while True:
        ret, frame = vid.read()
        if not ret:
            break

        if frame_scale_rate is not None:
            frame = cv2.resize(frame, None, fx=frame_scale_rate, fy=frame_scale_rate)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        dets = cnn_face_detector(frame_rgb, 1)
        if len(dets) > 0:
            face_descriptors = np.zeros((len(dets), 128))
            # face_descriptors = []
            for i, d in enumerate(dets):
                shape = sp(frame_rgb, d.rect)
                face_descriptor = face_rec.compute_face_descriptor(frame_rgb, shape, 50)
                face_descriptors[i:i+1:] = np.asarray(face_descriptor)
            predict_labels = model.predict(face_descriptors)
            predictions = model.predict_proba(face_descriptors)
            best_class_indices = np.argmax(predictions, axis=1)
            best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]

            img = Image.fromarray(frame_rgb)
            draw = ImageDraw.Draw(img)

            for i, d in enumerate(dets):
                text = '{}: {:.2%}'.format(class_names[predict_labels[i]], best_class_probabilities[i])
                draw.text((d.rect.left() + 2, d.rect.bottom() + 2), text, font=font, fill=(255, 255, 000))
                draw.rectangle([(d.rect.left(), d.rect.top()), (d.rect.right(), d.rect.bottom())],
                               outline=(255, 255, 0))

            frame = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

        cv2.imshow(video_file_path, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vid.release()
    cv2.destroyAllWindows()


@click.command()
@click.argument('video_file_path')
@click.argument('face_classifier_file_path')
@click.option('--skipped_duration', default=None, type=int, help='seconds')
@click.option('--frame_scale_rate', default=None, type=float, help='for reducing memory usage')
def main(video_file_path, face_classifier_file_path, skipped_duration, frame_scale_rate):
    if not os.path.isfile(video_file_path):
        print('\"%s\" not found' % video_file_path)
        return
    if not os.path.isfile(face_classifier_file_path):
        print('\"%s\" not found' % face_classifier_file_path)
        return

    recognition(video_file_path, face_classifier_file_path, skipped_duration, frame_scale_rate)


if __name__ == '__main__':
    main()
