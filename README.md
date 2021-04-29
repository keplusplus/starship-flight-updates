This project is licensed under the terms of the [GNU General Public License v3.0](./LICENSE).

# SpaceX Starship Flight Updates
## Telegram and Discord bot announcing breaking Starship news

This small script parses data from multiple sources and broadcasts big news to Discord and Telegram. Based on data like road closures and weather it assesses the chances of SpaceX performing an upcoming Starship test. Moreover, there are notifications when something important is happening at the Starship construction site (e. g. rollout).

### Provided notifications
Every day at 12:00 pm the bot will send a "Daily Update" with all relevant information whether a flight is possible.
```
𝗗𝗮𝗶𝗹𝘆 𝗙𝗹𝗶𝗴𝗵𝘁 𝗦𝘁𝗮𝘁𝘂𝘀 (local time 06:00)
Road Closure: no
nothing scheduled!
TFR: no
(max alt. needs to be unlimited for flight)
from Feb 08 21:10 to Mar 31 23:59 (max alt.: 7200 ft)
Weather today: ok
Clouds (broken clouds)
Wind: ok
Windy (25.67 km/h)

Presumably no flight today
Nothing big happening on current data!
(We will keep you updated if anything changes!)
```
There are also additional notifications:
* A road closure gets active or cancelled
* A road closure for the same day is cancelled or rescheduled
* A TFR gets active or cancelled
* A TFR for the same day is cancelled or rescheduled
* The weather changes (only when restrictions are in place)
* Something changes in the "prototypes" table at https://en.wikipedia.org/wiki/Starship_development_history
* Selected Tweets by Mary (@BocaChicaGal), SpaceX and Elon Musk
* A YouTube-Livestream about Starship gets scheduled by SpaceX

### Our instance
The original instance (hosted by [Fliens](https://github.com/Fliens)) is posting its messages in the [Telegram channel "SpaceX Starship Status"](https://t.me/StarshipStatus) and in a broadcast channel on the ["SpaceX Starship Status" discord server](https://discord.gg/mhvXctSJhv). Feel free to join to see the bot in action.

### Host by yourself
You can host this script by yourself and connect it to your own Telegram bot and Discord server.

To get this script working you need a recent version of Python 3. We have tested it with Python 3.8.4, but other version may also work. To install dependencies pip is recommended.

Just clone the repository and make your own `.env` file by copying the template `.env.default` and fill it with your own secrets. Then you need to install a few dependencies. With pip just do:

```
$ pip install beautifulsoup4 requests xmltodict schedule pytz python-dateutil
```

Make sure your pip command is using Python 3. Check with `pip -V` if you are not sure.

Then you should be able to run the script:

```
$ python main.py
```

Again, some systems might run the wrong python version, you can verify that with `python -V`.

### More documentation

Documentation about the code itself still needs to be written. You can help us by contributing.
### Contributing

If you have any ideas and want to contribute to this project, feel free to fork this repository and open pull requests.