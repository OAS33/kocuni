import coloredlogs
from json import load, dumps, dump
import praw
import logging
from time import time
import random
from colorama import init
from sys import stdout
from os import system
init()


def process_post(submission):
    global json_objects
    global posts_in_ram
    completion_list = []
    if submission.subreddit.display_name == "":
        prompt = random.choice([])
        completion_list.append(f"{submission.title} {submission.selftext}")
    else:
        prompt = f"{submission.title} {submission.selftext}"

        for index, comment in enumerate(submission.comments):
            loop_break = True
            if index >= CONFIG["REDDIT"]["COMMENT"]["NUMBER"]:
                break
            if comment.stickied:
                continue
            try:
                if comment.author.is_mod:
                    continue
            except Exception as e:
                logging.debug("User deleted")
            for word in CONFIG["REDDIT"]["POST"]["BLACKLIST"]:
                if word in comment.body:
                    break
            else:
                loop_break = False
            if loop_break != False:
                continue

            completion_list.append(comment.body)
            logging.debug(comment.body)
        logging.info(
            f"Harvested {len(completion_list)} comments, preparing them for training.")
        if completion_list == []:
            return
    for completion in completion_list:
        json_object = {}
        json_object["prompt"] = f"{prompt}⚿"
        json_object["completion"] = f" {completion}⚿"
        json_objects += dumps(json_object) + "\n"
    posts_in_ram += 1
    logging.debug(f"Current dataset in ram is {posts_in_ram} posts")
    if posts_in_ram > 15:
        logging.warning("Don't exit now.")
        with open(f"output/{filename}.jsonl", "a", encoding="utf-8") as f:
            f.write(json_objects)
            json_objects = ""
            posts_in_ram = 0


def main():
    global USED_POSTS
    global mode
    flairless_subs = []
    with open("used_posts.json", "r", encoding="utf-8") as f:
        USED_POSTS = load(f)
    logging.info("reading config file")
    CONFIG["REDDIT"]["CREDENTIALS"][
        "USER_AGENT"] = f"windows:{CONFIG['REDDIT']['CREDENTIALS']['CLIENT_ID']}:v1.0 (by u/rizzfarmer)"

    try:
        config = CONFIG["REDDIT"]["CREDENTIALS"]
        reddit = praw.Reddit(
            client_id=config["CLIENT_ID"],
            client_secret=config["CLIENT_SECRET"],
            user_agent=config["USER_AGENT"],
            password=config["PASSWORD"],
            username=config["USERNAME"])
        del (config)
    except Exception as e:
        logging.critical("Couldn't connect to reddit", exc_info=True)
        exit()

    logging.info(f"Connected to reddit: {not reddit.read_only}")

    if choice == 2:
        while True:
            url = input("Post url or ID:")
            try:
                post_id = url.split("/")[url.split("/").index("comments") + 1]
            except ValueError:
                post_id = url
            system("cls")
            logging.info("Fetching post...")
            try:
                submission = reddit.submission(post_id)
            except:
                logging.error("Invalid input")
                continue
            process_post(submission)
            USED_POSTS[submission.id] = 1

    logging.info("Searching for submissions...")

    subreddit = reddit.subreddit("+".join(CONFIG["REDDIT"]["SUBREDDITS"]))
    reached_end = False
    if mode == 1:
        mode = subreddit.new(limit=None)
    elif mode == 2:
        mode = subreddit.top(limit=None, time_filter="all")
    else:
        mode = subreddit.top(limit=None, time_filter="week")
    count = 0
    for submission in mode:
        loop_break = True
        logging.info("Searching for submissions...")
        logging.debug(
            f"Got post from: {submission.subreddit.display_name}(cm:{submission.num_comments},score:{submission.score},up_r:{submission.upvote_ratio}), checking for conformity")
        try:
            if USED_POSTS[submission.id] == 1:
                logging.debug(f"post has been used before {e}", exc_info=True)

                if reached_end == False:
                    reached_end = True
                    logging.critical("This post has been used before")
                    if input("KEEP SCROLLING(y/n)? :") != "y":
                        break
                continue
        except:
            pass
        if submission.num_comments < CONFIG["REDDIT"]["POST"]["MIN_COMMENTS"] or submission.score < CONFIG["REDDIT"]["POST"]["MIN_UPVOTES"] or submission.upvote_ratio < CONFIG["REDDIT"]["POST"]["MIN_UPVOTE_RATIO"] or submission.stickied:
            logging.debug("Post isn't eligible to be used")
            continue
        logging.info(
            f"Found post! Getting title and comments(sbrddt:{submission.subreddit})")
        try:
            flair = submission.link_flair_text.lower()
        except AttributeError:
            logging.debug("Post flair is None")
            flair = ""
        if "question" not in flair and "situation" not in flair:
            if submission.subreddit.display_name not in flairless_subs:
                continue
        for word in CONFIG["REDDIT"]["POST"]["BLACKLIST"]:
            if word in submission.title or word in submission.selftext:
                break
        else:
            loop_break = False
        if loop_break != False:
            continue
        USED_POSTS[submission.id] = 1
        count += 1
        if count % 10 == 0:
            system("cls")
            logging.info(
                f"Done {count} posts in {round(time()-START, 2)} seconds. ({round(count/(time()-START), 3)}/second)")
        process_post(submission)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    coloredlogs.install(level="INFO",
                        fmt='%(levelname)s: %(message)s || %(asctime)s')
    USED_POSTS = {}
    json_objects = ""
    posts_in_ram = 0
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG = load(f)
    choice = int(input("Prepare 1-Automatically, 2-Manually: "))
    if choice == 1:
        mode = int(input("Sort by 1-New, 2-Top(all time) 3-Top(weekly): "))
    system("cls")
    filename = str(time()).split(".")[0]
    START = time()
    try:
        main()
    except KeyboardInterrupt:
        with open("used_posts.json", "w", encoding="utf-8") as f:
            dump(USED_POSTS, f) 
        exit()
    except Exception as e:
        logging.critical("ERROR IN MAIN", exc_info=True)
        with open("used_posts.json", "w", encoding="utf-8") as f:
            dump(USED_POSTS, f)
        exit()
    with open("used_posts.json", "w", encoding="utf-8") as f:
        dump(USED_POSTS, f)
