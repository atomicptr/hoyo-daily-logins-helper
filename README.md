# hoyo-daily-login-helper

Get hoyo daily login rewards automatically!

## Usage

1. Get your cookie string, open the daily check in page
   * [Daily Check-in page for Genshin](https://act.hoyolab.com/ys/event/signin-sea-v3/index.html?act_id=e202102251931481)
   * [Daily Check-in page for Star Rail](https://act.hoyolab.com/bbs/event/signin/hkrpg/index.html?act_id=e202303301540311)
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

## Installation

### Docker

The command line options are also available via environment variables which
allows you to easily run this script in Docker/Podman!

```bash
$ docker run --rm --env GAME=starrail --env COOKIE="your cookie string" ghcr.io/atomicptr/hoyo-daily-logins-helper
```

### pip

```bash
$ pip install hoyo-daily-logins-helper
```

PyPi: https://pypi.org/project/hoyo-daily-logins-helper/


## Configuration

### Cookie

You can provide the cookie information either via the **COOKIE** environment variable or using the --cookie CLI flag.

### Game

You can provide the cookie information either via the **GAME** environment variable or using the --genshin/--starrail CLI flags.

**Supported Games**: Genshin Impact (genshin), Honkai Starrail (starrail)

### Debug mode

If something doesn't work properly and/or you want to report an issue try running the tool with the **DEBUG_MODE** environment variable set to 1! Or provide the --debug flag!

```bash
$ DEBUG_MODE=1 hoyo-daily-logins-helper --starrail --cookie="..."
```

### Language

If you want to see the results in other languages than English you can change them via the **LANGUAGE** environment variable

```bash
$ LANGUAGE=ja-jp hoyo-daily-logins-helper --genshin --cookie="..."
```

## License

GNU General Public License v3

![](https://www.gnu.org/graphics/gplv3-127x51.png)