from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
import youtube_dl
from .forms import DownloadForm


def download_video(request):
    global context
    form = DownloadForm(request.POST or None)
    if form.is_valid():
        video_url = form.cleaned_data.get("url")
        if 'm.' in video_url:
            video_url = video_url.replace(u'm.', u'')

        elif 'youtu.be' in video_url:
            video_id = video_url.split('/')[-1]
            video_url = 'https://www.youtube.com/watch?v=' + video_id

        if len(video_url.split("=")[-1]) != 11:
            return HttpResponse('Enter correct url.')
        # video_url = 'https://www.youtube.com/watch?v=ydg9KZCCPE0&ab_channel=Spatry%27sCupofLinux'
        # video = pafy.new(video_url)

        ydl_opts = {}

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            meta = ydl.extract_info(
                video_url, download=False)
        video_audio_streams = []
        for m in meta['formats']:
            file_size = m['filesize']
            if file_size is not None:
                file_size = f'{round(int(file_size) / 1000000,2)} mb'

            resolution = 'Audio'
            if m['height'] is not None:
                resolution = f"{m['height']}x{m['width']}"
            video_audio_streams.append({
                'resolution': resolution,
                'extension': m['ext'],
                'file_size': file_size,
                'video_url': m['url']
            })
        video_audio_streams = video_audio_streams[::-1]
        context = {
            'form': form,
            'title': meta['title'], 'streams': video_audio_streams,
            'description': meta['description'], 'likes': meta['like_count'],
            'dislikes': meta['dislike_count'], 'thumb': meta['thumbnails'][3]['url'],
            'duration': round(int(meta['duration'])/60, 2), 'views': meta['view_count']
        }
        return render(request, 'home.html', context)

    return render(request, 'home.html', {'form': form})
