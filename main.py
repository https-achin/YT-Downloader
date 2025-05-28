import os
import subprocess
from pytube import YouTube
import sys

DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')

print(r"__   _______     ______                    _                 _           ")
print(r"\ \ / /_   _|    |  _  \                  | |               | |          ")
print(r" \ V /  | |______| | | |_____      ___ __ | | ___   __ _  __| | ___ _ __ ")
print(r"  \ /   | |______| | | / _ \ \ /\ / / '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|")
print(r"  | |   | |      | |/ / (_) \ V  V /| | | | | (_) | (_| | (_| |  __/ |   ")
print(r"  \_/   \_/      |___/ \___/ \_/\_/ |_| |_|_|\___/ \__,_|\__,_|\___|_|   ")
print(r"                                                                         ")
print(r"                                                                         ")   
print(r"                        Made By Sachin :)                                ")
print(r" ------------------------------------------------------------------------")

def show_menu():
    print("\nYouTube Downloader")
    print("1. Download Video")
    print("2. Download Audio Only")
    print("3. Download Video (using yt-dlp)")
    print("4. Download Audio (using yt-dlp)")
    print("5. Exit")
    choice = input("Enter your choice (1-5): ")
    return choice.strip()


def get_youtube_url():
    while True:
        url = input("Enter a valid YouTube video URL: ").strip()
        if 'youtube.com/watch?v=' in url or 'youtu.be/' in url:
            try:
                yt = YouTube(url)
                return yt
            except Exception as e:
                print(f"Error: {e}\nPlease enter a valid YouTube URL.")
        else:
            print("Invalid URL. Please enter a valid YouTube video URL.")


def select_quality(yt, audio_only=False):
    try:
        if audio_only:
            streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
        else:
            streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
        
        qualities = []
        print("\nAvailable Qualities:")
        for idx, stream in enumerate(streams):
            quality = stream.abr if audio_only else stream.resolution
            print(f"{idx + 1}. {quality}")
            qualities.append(stream)
        
        if not qualities:
            print("No downloadable streams found for this video.")
            return None
            
        while True:
            choice = input(f"Select quality (1-{len(qualities)}): ")
            if choice.isdigit() and 1 <= int(choice) <= len(qualities):
                return qualities[int(choice) - 1]
            else:
                print("Invalid choice. Please select a valid quality.")
    except Exception as e:
        print(f"Error fetching streams: {e}\nThis video may not be available for download.")
        return None


def download_video(stream, yt, audio_only=False):
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    print(f"\nDownloading: {yt.title}")
    
    # Define callback to show progress
    def progress_callback(stream, chunk, bytes_remaining):
        size = stream.filesize
        progress = (size - bytes_remaining) / size * 100
        sys.stdout.write(f"\rProgress: {progress:.1f}%")
        sys.stdout.flush()
    
    # Register callback
    yt.register_on_progress_callback(progress_callback)
    
    out_path = stream.download(output_path=DOWNLOAD_DIR)
    print("\n")  # New line after progress
    
    if audio_only:
        try:
            base, _ = os.path.splitext(out_path)
            new_path = base + '.mp3'
            os.rename(out_path, new_path)
            out_path = new_path
        except Exception as e:
            print(f"Error converting to MP3: {e}")
    
    print(f"✓ Download completed!")
    print(f"📂 File saved: {out_path}")


def get_video_formats_ytdlp(url):
    try:
        # Get video formats
        command = [
            'python', '-m', 'yt_dlp',
            '-F',  # List formats
            '--no-warnings',
            '--quiet',
            url
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        formats = result.stdout.strip().split('\n')
        
        # Filter and organize formats
        quality_options = {
            '1080p': [],
            '720p': [],
            '480p': [],
            '360p': [],
            '240p': [],
            '144p': []
        }
        
        # Parse formats
        for line in formats:
            if line and not line.startswith('['):
                parts = line.split()
                if len(parts) >= 3:
                    format_id = parts[0]
                    ext = parts[1]
                    if ext == 'mp4':
                        # Look for resolution in the line
                        for quality in quality_options.keys():
                            if quality in line:
                                # Check if it's a complete format (has both video and audio)
                                has_audio = 'video only' not in line
                                size = next((part for part in parts if 'MiB' in part or 'KiB' in part), 'N/A')
                                quality_options[quality].append((format_id, has_audio, size))
        
        # Organize available formats
        available_formats = []
        print("\n📺 Available Video Qualities:")
        print("─" * 50)
        print(f"{'ID':<4} {'Quality':<8} {'Size':<10} {'Type':<15}")
        print("─" * 50)
        
        idx = 1
        for quality in reversed(quality_options.keys()):
            formats = quality_options[quality]
            if formats:
                # Prefer formats with audio, then sort by format ID
                formats.sort(key=lambda x: (not x[1], x[0]))
                format_id, has_audio, size = formats[0]  # Take the best option for each quality
                type_str = "Video + Audio" if has_audio else "Video only"
                print(f"{idx:<4} {quality:<8} {size:<10} {type_str}")
                available_formats.append(format_id)
                idx += 1
        
        print("─" * 50)
        
        if not available_formats:
            return None
            
        while True:
            choice = input("\n💫 Select quality (1-%d): " % len(available_formats))
            if choice.isdigit() and 1 <= int(choice) <= len(available_formats):
                return available_formats[int(choice)-1]
            print("❌ Invalid choice. Please try again.")
            
    except Exception as e:
        print("⚠️ Error fetching video formats. Using default quality.")
        return None


def download_with_ytdlp(url, audio_only=False):
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    print("\nStarting download...")
    try:
        command = [
            'python', '-m', 'yt_dlp',
            '-P', DOWNLOAD_DIR,
            '--newline',
            '--progress-template', '%(progress._percent_str)s',
            '--no-warnings',
            '--quiet',
            '--progress',
        ]
        
        if audio_only:
            command.extend([
                '-x',
                '--audio-format', 'mp3',
                '--audio-quality', '0'
            ])
        else:
            # Get video format choice
            format_code = get_video_formats_ytdlp(url)
            if format_code:
                command.extend(['-f', format_code])
        
        command.append(url)
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Monitor the output
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                if '%' in output:
                    sys.stdout.write(f"\rProgress: {output.strip()}")
                    sys.stdout.flush()
        
        print("\n✓ Download completed!")
        print(f"📂 File saved in: {DOWNLOAD_DIR}")
        
    except Exception as e:
        print(f"Error during download: {e}")


def main():
    while True:
        choice = show_menu()
        if choice in ['1', '2', '3', '4']:
            url = input("Enter a valid YouTube video URL: ").strip()
            
            if choice == '1':  # Download Video with pytube
                try:
                    yt = YouTube(url)
                    stream = select_quality(yt)
                    if stream:
                        download_video(stream, yt)
                    else:
                        print("Trying alternative download method...")
                        download_with_ytdlp(url)
                except Exception as e:
                    print("Trying alternative download method...")
                    download_with_ytdlp(url)
                    
            elif choice == '2':  # Download Audio with pytube
                try:
                    yt = YouTube(url)
                    stream = select_quality(yt, audio_only=True)
                    if stream:
                        download_video(stream, yt, audio_only=True)
                    else:
                        print("Trying alternative download method...")
                        download_with_ytdlp(url, audio_only=True)
                except Exception as e:
                    print("Trying alternative download method...")
                    download_with_ytdlp(url, audio_only=True)
                    
            elif choice == '3':  # Download Video with yt-dlp
                download_with_ytdlp(url)
                
            elif choice == '4':  # Download Audio with yt-dlp
                download_with_ytdlp(url, audio_only=True)
                
        elif choice == '5':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == "__main__":
    main()
