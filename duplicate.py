from modules.logger import setup_logger
import logging
from datetime import datetime
import praw
import prawcore
from modules.login import reddit
from modules.footer import footer

logger = setup_logger('duplicates')

def run_bot(sub_id):
    if True:
        try:
            logging.debug('Starting submission {}'.format(sub_id))
            blockeduser = 0
            duplicates = []
            submission = praw.models.Submission(reddit, id = sub_id)
            with open('blockusers.txt','r') as newfile:
                for line in newfile.readlines():
                    line = line.strip('\n')
                    if str(submission.author) == line or 'bot' in str(submission.author).lower():
                        blockeduser = 1
                        logger.debug('User {}\'s submission {} was blocked from posting'.format(str(submission.author),str(sub_id)))
                    else:
                        pass
            if blockeduser == 0:
                for duplicate in submission.duplicates():   
                    dup_sub = praw.models.Submission(reddit, id = duplicate)
                    if 'imagesof' not in str(dup_sub.subreddit).lower() and 'auto' not in str(dup_sub.subreddit).lower() and 'bot' not in str(dup_sub.author).lower() and 'mistyfront' not in str(dup_sub.subreddit).lower() and 'unitedfederation' not in str(dup_sub.subreddit).lower():
                        time = dup_sub.created
                        time = str(datetime.fromtimestamp(time))
                        author = '/u/'+str(dup_sub.author)
                        if str(submission.author) == author:
                            author = author + ' [author of both threads]'
                        duplicates.append({'title':str(dup_sub.title), 'subreddit':str(dup_sub.subreddit), 'link':'https://www.reddit.com'+str(dup_sub.permalink), 'time':str(time), 'author':author, 'karma': str(dup_sub.score)})
                        if len(duplicates) > 0:
                            message = 'Here is a list of threads in other subreddits about the same content:\n'
                            for dup in duplicates:
                                message = str(message + '\n * [{}]({}) on /r/{} with {} karma (created at {} by {})').format(dup['title'], dup['link'], dup['subreddit'], dup['karma'],dup['time'], dup['author'])
                            message = message + footer
                try:
                    submission.reply(message)
                    logger.info('Message posted on {}'.format(sub_id))
                    logger.debug('Message: {}'.format(message))
                    message = ''
                except(praw.exceptions.APIException, UnboundLocalError)as e:
                    logger.debug('Submission {} has been skipped due to missing text'.format(sub_id))
                    message = ''
                except(prawcore.exceptions.Forbidden):
                    logger.debug('You are blocked on /r/{}'.format(str(submission.subreddit)))
                    message = ''
                except(AssertionError):
                    logger.debug('Assertion Error occured! Printing message and traceback.')
                    logger.debug(message + str(len(message)), exc_info=True)
                    message = ''
                except(KeyboardInterrupt):
                    raise KeyboardInterrupt
                except:
                    logger.error('Error occured!', exc_info=True)
                    message = ''
        except(KeyboardInterrupt):
            raise KeyboardInterrupt
        except:
            logger.error('Error on submission {} occured.'.format(str(sub_id)), exc_info=True)


def action():
    for sub_id in reddit.subreddit('all').stream.submissions():
        run_bot(sub_id)
            

if __name__ == '__main__':
    while True:
        try:
            action()
        except(KeyboardInterrupt):
            raise KeyboardInterrupt
        except:
            logger.critical('Error has occured when running main loop, please resolve asap', exc_info=True)