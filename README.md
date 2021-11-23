## Youtube Channel DL Bot
_A Telegram bot to download youtube channel contents and upload them to telegram. (may be slow becoz youtube limitations)_

## 📌 Deploy to Heroku
Click below button to deploy.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/samadii/YT-Channel-DL)


## Local Deploying

1. Clone the repo
   ```
   git clone https://github.com/samadii/YT-Channel-DL
   ```

2. Install [FFmpeg](www.ffmpeg.org) & [Google Chrome](https://support.google.com/chrome/answer/95346?hl=en&co=GENIE.Platform%3DDesktop) and [ChromeDriver](https://chromedriver.chromium.org/downloads).

3. Add ChromeDriver folder path to your System PATH environment variable.
Also add ffmpeg bin folder path.

4. Go to [this line](https://github.com/samadii/YT-Channel-DL/blob/main/plugins/download.py#L27) and add path where chromedriver is there.

5. Enter the directory
   ```
   cd YT-Channel-DL
   ```
  
6. Install all requirements using pip.
   ```
   pip3 install -r requirements.txt
   ```

7. Run the file
   ```
   python3 bot.py
   ```

## 📌 Credits
- [AnjanaMadu](https://github.com/AnjanaMadu) for his [YTPlaylistDL](https://github.com/AnjanaMadu/YTPlaylistDL)
- [Me](https://github.com/samadii)
