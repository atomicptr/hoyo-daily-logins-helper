# hoyo-daily-login-helper

Get hoyo daily login rewards automatically!

## Usage

1. Get your cookie string, open the daily check in page
   * [Daily Check-in page for Genshin](https://act.hoyolab.com/ys/event/signin-sea-v3/index.html?act_id=e202102251931481)
   * [Daily Check-in page for Star Rail](#test)
2. Open a development console (F12) and insert the following code:
    ```javascript
    document.cookie
    ```
3. Copy the returned string should be something like "ltoken=....; account_id=....;" this is your cookie string
4. Open a terminal with the command prepared and enter:
    ```bash
    $ hoyo-daily-logins-helper --cookie="your cookie string" --genshin
    ```
   (or ``--starrail`` for Honkai Star Rail)
5. Done!

