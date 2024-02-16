import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options


def start_session(headless=False):
    options = Options()
    if headless:
        options.headless = headless
        options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)
    browser.get("https://www.nytimes.com/games/wordle/index.html")
    root = get_element(browser, By.TAG_NAME, "html")
    return browser, root


def get_element(browser, by, predicate, time_out=30):
    element = wait(browser, time_out).until(EC.presence_of_element_located((by, predicate,)))
    browser.execute_script("arguments[0].scrollIntoView();", element)
    return element


def press_play(browser):
    play_button = get_element(browser, By.XPATH, "//button[@data-testid='Play']")
    play_button.click()

    close_module(browser)
    return True


def close_module(browser):
    try:
        close_button = get_element(browser, By.XPATH, "//button[@aria-label='Close']", 2)
        close_button.click()
        return True
    except Exception as _:
        return False


def make_guess(root, word):
    for char in word:
        root.send_keys(char)
    root.send_keys(Keys.ENTER)

    return True


def get_feedback(browser, root, attempt):
    time.sleep(2)
    row = get_element(browser, By.XPATH, f"//div[@aria-label='Row {attempt}']")
    squares = row.find_elements(By.TAG_NAME, "div")

    feedback = ""
    for square in squares:
        if square.aria_role == 'image' and square.accessible_name is not None:
            if "correct" in square.accessible_name:
                feedback += "y"
            elif "present in another position" in square.accessible_name:
                feedback += "?"
            elif "absent" in square.accessible_name:
                feedback += "n"
            else:
                feedback += "x"

    for _ in range(2):
        if feedback == "xxxxx":
            for _ in range(5):
                root.send_keys(Keys.BACKSPACE)
            return None, False
        elif "x" in feedback or len(feedback) != 5:
            time.sleep(2)
            close_module(browser)
            time.sleep(2)
        else:
            return feedback, True

    raise RuntimeError("Something went wrong. Please check and try again.")


def get_correct_word(browser):
    time.sleep(5)
    close_module(browser)
    toast = get_element(browser, By.ID, "ToastContainer-module_gameToaster__HPkaC")
    toast = toast.find_element(By.TAG_NAME, "div")
    return toast.text.upper()
