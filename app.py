from flask import Flask, render_template, request, send_from_directory
import os
import instaloader

app = Flask(__name__)

def download_instagram_media(url, video_quality="high"):
    try:
        if "instagram.com/p/" not in url:
            raise ValueError("A URL fornecida não parece ser do Instagram.")

        loader = instaloader.Instaloader()
        post_code = url.split("/p/")[-1].rstrip('/')
        post = instaloader.Post.from_shortcode(loader.context, post_code)

        if post.typename in ["GraphVideo", "GraphImage"]:
            if video_quality == "high" and post.typename == "GraphVideo":
                video_file = f"{post_code}_high.mp4"
            else:
                video_file = f"{post_code}.mp4"

            target_path = os.path.join('static', video_file)
            loader.download_post(post, target=target_path)
            return True, video_file, target_path
        else:
            return False, "O post não contém um vídeo ou imagem."

    except ValueError as ve:
        return False, f"Erro: {ve}"
    except instaloader.exceptions.InstaloaderException as ie:
        return False, f"Ocorreu um erro durante o download: {ie}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_url = request.form['video_url']
        success, message, video_file_path = download_instagram_media(video_url)
        return render_template('index.html', success=success, message=message, video_file_path=video_file_path)
    return render_template('index.html', success=None, message=None, video_file_path=None)

@app.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory('static', filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
