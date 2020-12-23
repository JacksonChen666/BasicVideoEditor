#  BasicVideoEditor. A video editor made for cutting and combining people.
#  Copyright (C) 2020  JacksonChen666
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import ffmpeg


def processCuts(cuts: dict):
    for videoName in cuts.keys():
        videoMeta = cuts[videoName]
        video = ffmpeg.input(videoName)
        if "Cuts" in videoMeta:
            videoMetaCuts = videoMeta["Cuts"]
            if isinstance(videoMetaCuts, dict):
                for cut in videoMetaCuts.keys():
                    start = cut
                    end = videoMetaCuts[start]
                    if end == -1.0:
                        yield video.video.filter("trim", start=start).setpts('PTS-STARTPTS')
                        yield video.audio.filter("atrim", start=start).filter_('asetpts', 'PTS-STARTPTS')
                    else:
                        if start > end:
                            raise ValueError("The end of a clip cannot go before the start of the clip.")
                        yield video.video.filter("trim", start=start, duration=end).setpts('PTS-STARTPTS')
                        yield video.audio.filter("atrim", start=start, duration=end).filter_('asetpts', 'PTS-STARTPTS')


videoCuts = {
    "video1.ignore.mp4": {
        "Cuts": {
            1.0: -1.0
        }
    },
    "video2.ignore.mp4": {
        "Cuts": {
            2.0: 2.5
        }
    }
}

# convert all filenames to ffmpeg-python video and audio that's properly cut
videos = processCuts(videoCuts)

joined = ffmpeg.concat(*videos, v=1, a=1).node

finalVideo = joined[0]
finalAudio = joined[1]

# https://stackoverflow.com/a/60142346
out = ffmpeg.output(finalVideo, finalAudio, 'out.ignore.mp4').run()
