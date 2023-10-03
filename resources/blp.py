# resources/blp.py
from flask import Blueprint, jsonify, request, send_from_directory
from flask.views import MethodView
import os
from werkzeug.utils import secure_filename
import tempfile
from moviepy.editor import VideoFileClip

# Import the required function from resources
from resources.utils import generate_unique_filename

blp = Blueprint("videos", __name__)


unique_name = generate_unique_filename()


@blp.route("/videos")
class VideoList(MethodView):
    """
    Retrieves a list of video metadata (filename, file size, resolution, and extension) for uploaded videos.
    """

    def get(self):
        try:
            video_folder = current_app.config["UPLOAD_FOLDER"]
            video_files = os.listdir(video_folder)
            video_list = []

            for filename in video_files:
                if filename.endswith((".mp4", ".webm", ".mov")):
                    file_path = os.path.join(video_folder, filename)
                    video_clip = VideoFileClip(file_path)

                    video_info = {
                        "file_name": filename,
                        "file_size": f"{round(os.path.getsize(file_path) / (1024 * 1024), 2)} mb",
                        "resolution": f"{video_clip.size[0]} x {video_clip.size[1]}",
                        "extension": os.path.splitext(filename)[1][1:],
                    }

                    video_list.append(video_info)

            return jsonify(video_list), 200

        except Exception as e:
            return jsonify({"error": str(e)})


@blp.route("/videos/upload", methods=["POST"])
class VideoToDisk(MethodView):
    """
    Uploads and appends video chunks to an existing video file on the disk.
    """

    def post(self):
        content_type = request.headers.get("Content-Type")
        extension = get_file_extension(content_type)

        if not os.path.exists(current_app.config["UPLOAD_FOLDER"]):
            os.makedirs(current_app.config["UPLOAD_FOLDER"])

        try:
            video_data = request.data
            if not video_data:
                return jsonify({"error": "Missing video data"}), 400

            if not extension:
                return jsonify({"error": "Unsupported Content-Type"}), 400

            filename = secure_filename(request.headers.get("X-File-Name", f"{unique_name}.{extension}"))
            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

            if os.path.exists(file_path):
                with open(file_path, "ab") as f:
                    chunk_size = 10 * 1024 * 1024
                    while True:
                        chunk = request.stream.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
            else:
                with open(file_path, "wb") as f:
                    f.write(video_data)

            return jsonify({"message": "Uploaded successfully", "filename": filename}), 201

        except Exception as e:
            return jsonify({"error": str(e)})