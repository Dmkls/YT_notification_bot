# YT_notification_bot

Telegram bot to send notifications from YouTube about the release of new videos

In order to run it you need to do 3 things:<br><br>

1. Create Google App and get client_secret file:
<ul>
  <li>In Google Cloud, create a project without an organization - <a href="https://www.youtube.com/watch?v=jd6xq3KfNTY&ab_channel=ROITraining">video tutorial</a></li>
  <li>In the OAuth section, create an <i>External</i> app and publish it</li>
  <li>In the Credentials section, click <i>"CREATE CREDENTIALS"</i>, select the OAuth client ID and select the application type <i>"DESCTOP APP"</i></li>
  <li>Download the client_secret file, rename it to <i>client_secret.json</i> and place it in the root of the project</li>
</ul><br>

2. Register Telegram Bot and create Ngrok account (or you can use your public ip address if you have one)

<ul>
  <li>How to create Telegram bot - <a href="https://flowxo.com/how-to-create-a-bot-for-telegram-short-and-simple-guide-for-beginners/">click</a></li>
  <li>Register account on <a href="https://dashboard.ngrok.com/signup">Ngrok</a></li>
  <li>Put tokens in the <i>config.py</i> file</li>
</ul><br>

3. <i>pip install -r requirements.txt</i>

To run the bot properly, first run <b>back.py</b>, then <b>bot.py</b>
