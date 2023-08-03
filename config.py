import webbrowser


class c:
    VIOLET = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    # Learned word (from learned.txt file)
    GREEN = '\033[92m'
    # Unlearned word (from unlearned.txt file)
    YELLOW = '\033[93m'
    # Unknown word (word doesn't exist in my database)
    RED = '\033[91m'
    GREY = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def setup_webbrowser():
    webbrowser.register('chrome',
                        None,
                        webbrowser.BackgroundBrowser("C://Program Files//Google//Chrome//Application//chrome.exe"))
    return webbrowser.get('chrome')
