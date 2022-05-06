import json
import os.path
import subprocess

import cv2

from tools.misc import ergo_logger

logger = ergo_logger.get_logger('video_preprocess.log')


class VideoPreprocessor():
    def __init__(self):
        pass

    @staticmethod
    def reduce_rate_and_resize(video_file):
        logger.info(f'********************************')
        logger.info(f'Processing {video_file}')
        vidcap = cv2.VideoCapture(video_file)
        rate = int(vidcap.get(cv2.CAP_PROP_FPS))
        logger.info(f'frame rate: {rate}')
        height = vidcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        width = vidcap.get(cv2.CAP_PROP_FRAME_WIDTH)
        dar, sar, par = VideoPreprocessor.get_aspect_ratios(video_file)
        logger.info(f'dar:{dar}, sar: {sar}, par:{par}')
        success, image = vidcap.read()
        count = 0

        success = True
        adjusted_frames = []
        while success:
            # cv2.imwrite(f'{str(output_path)}/frame{count}.png', image)  # save frame as JPEG file
            if sar != 1:
                image = cv2.resize(src=image, dsize=(int(dar * height), int(height)), interpolation=cv2.INTER_AREA)
            adjusted_frames.append(image)
            success, image = vidcap.read()
            logger.info(f'Read frame {count}')
            count += 1
        output_video = os.path.join(os.path.dirname(video_file),
                                    os.path.basename(video_file).replace('.mp4', '_r10.mp4'))
        VideoPreprocessor.frames_to_video_using_ffmpeg(frames=adjusted_frames, output_path=output_video, rate=10)
        return output_video

    @staticmethod
    def frames_to_video_using_ffmpeg(frames=None, output_path=None, rate=10):
        logger.info('frames_to_video() output = ' + str(output_path))
        import skvideo.io
        writer = skvideo.io.FFmpegWriter(output_path,
                                         # inputdict={'-s':'{}x{}'.format(1080,1920)},
                                         outputdict={'-r': str(rate),
                                                     '-loglevel': 'debug',
                                                     '-vcodec': 'libx264',
                                                     '-pix_fmt': 'yuv420p',
                                                     '-b:v': '90000000'}, verbosity=1)

        for index, img in enumerate(frames):

            if img is None:
                continue
            img = img[:, :, ::-1]
            # data = np.asarray(img)
            # img = Image.fromarray(np.roll(data, 1, axis=-1))
            try:
                writer.writeFrame(img)
            except ValueError as ve:
                logger.info('ValueError writer.writeFrame(img) @ image index ' + str(index))
                logger.info(str(ve))

        writer.close()

    @staticmethod
    def get_aspect_ratios(video_file):
        cmd = 'ffprobe -i "{}" -v quiet -print_format json -show_format -show_streams'.format(video_file)
        #     jsonstr = subprocess.getoutput(cmd)
        jsonstr = subprocess.check_output(cmd, shell=True, encoding='utf-8')
        r = json.loads(jsonstr)
        # look for "codec_type": "video". take the 1st one if there are mulitple
        video_stream_info = [x for x in r['streams'] if x['codec_type'] == 'video'][0]
        if 'display_aspect_ratio' in video_stream_info and video_stream_info['display_aspect_ratio'] != "0:1":
            a, b = video_stream_info['display_aspect_ratio'].split(':')
            dar = int(a) / int(b)
        else:
            # some video do not have the info of 'display_aspect_ratio'
            w, h = video_stream_info['width'], video_stream_info['height']
            dar = int(w) / int(h)
            ## not sure if we should use this
            # cw,ch = video_stream_info['coded_width'], video_stream_info['coded_height']
            # sar = int(cw)/int(ch)
        if 'sample_aspect_ratio' in video_stream_info and video_stream_info['sample_aspect_ratio'] != "0:1":
            # some video do not have the info of 'sample_aspect_ratio'
            a, b = video_stream_info['sample_aspect_ratio'].split(':')
            sar = int(a) / int(b)
        else:
            sar = dar
        par = dar / sar
        return dar, sar, par
