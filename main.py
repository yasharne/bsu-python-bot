from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,ConversationHandler)
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
import logging
import emoji
from pymongo import MongoClient
import time
from QuestionSet import QuestionSet
import os
from Question import Question
from Result import Result
import pprint

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

client = MongoClient('mongodb://admin:bsu123456@ds151282.mlab.com:51282/bsu')
bsu = client.bsu
students = bsu.students
categories = bsu.cats
questionsets = bsu.questionsets
results = bsu.results

SEEMYSCORE = "See my scores"
TAKETEST = "Take a test"

s_firstname = ''
s_lastname = ''
current_category = ''
current_exam = ''
timestamp = 0
# QuestionSet object
q = None
current_question = None
# Result object
result = None
# Accepted input for a state in telegram bot
accepted_inputs = []

EXAMORSCORE, FIRSTNAME, LASTNAME, CHOOSESET, QUESTIONS, ASKAQUESTION = range(6)

def start(bot, update):
    global result
    result = Result()
    student = students.find_one({'id': str(update.message.chat_id)})
    if (student is not None):
        reply_keyboard = [[SEEMYSCORE, TAKETEST]]
        update.message.reply_text(emoji.emojize("Hello " + student["firstname"] + ":wave:\n"
                                                                               "What do you want to do?", use_aliases=True),
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True)
                                  )
        result.set_s_id(student['_id'])
        return EXAMORSCORE
    else:
        update.message.reply_text("Welcome to the BSU exam Bot\n"
                                  "To start using the bot you need to register first", reply_markup=ReplyKeyboardRemove())
        update.message.reply_text("Enter your firstname: ", reply_markup=ReplyKeyboardRemove())
        return FIRSTNAME


def exam_or_score(bot, update):
    ''' Determines whether user wants to see scores or take a exam'''
    global accepted_inputs
    accepted_inputs = []
    if update.message.text == TAKETEST:
        reply_keyboard = [[]]
        cats = categories.find({})
        for cat in cats:
            reply_keyboard[0].append(cat['name'])
            accepted_inputs.append(cat['name'])
        update.message.reply_text("Select your category:",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CHOOSESET
    elif update.message.text == SEEMYSCORE:
        update.message.reply_text("Not implemented yet :)",
                                  reply_markup=ReplyKeyboardRemove())



def firstname(bot, update):
    global s_firstname
    s_firstname = update.message.text
    update.message.reply_text("OK " + s_firstname + ", now enter your lastname: ", reply_markup=ReplyKeyboardRemove())
    return LASTNAME

def lastname(bot, update):
    global result
    global s_lastname
    reply_keyboard = [[SEEMYSCORE, TAKETEST]]
    s_lastname = update.message.text
    student = {'id': str(update.message.chat_id), 'firstname': s_firstname,
               'lastname': s_lastname, 'score': 0}
    result.set_s_id(students.insert_one(student))
    update.message.reply_text(emoji.emojize("Hello " + s_firstname + ":wave:\n"
                                                                              "What do you want to do?",
                                            use_aliases=True),
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True)
                              )
    return EXAMORSCORE


def chooseset(bot, update):
    global result, accepted_inputs
    if update.message.text not in accepted_inputs:
        update.message.reply_text('Please choose your Category from the list')
        return CHOOSESET
    accepted_inputs = []
    reply_keyboard = [[]]
    qss = questionsets.find({'category': update.message.text}, {'name': 1})
    result.set_category(update.message.text)
    for qs in qss:
        reply_keyboard[0].append(qs['name'])
        accepted_inputs.append(qs['name'])
    # update.message.reply_text("Select test set:", reply_markup=ReplyKeyboardMarkup(reply_keyboard,
    #                                                                                one_time_keyboard=True))
    update.message.reply_text("Enter test set name:")
    return QUESTIONS


def questions(bot, update):
    global timestamp, q, current_question, result, accepted_inputs
    if update.message.text not in accepted_inputs:
        update.message.reply_text('Please Enter test set correctly')
        return QUESTIONS
    accepted_inputs = []
    testset = update.message.text
    update.message.reply_text("Examset " + testset, reply_markup=ReplyKeyboardRemove())
    questionset = questionsets.find_one({'name': testset})
    result.set_q_id(questionset['_id'])
    result.reset_score()
    q = QuestionSet(questionset)
    current_question = q.get_question()
    result.set_begin_time()
    update.message.reply_text(emoji.emojize(":question: Question #" + str(q.get_question_number()) +
                                            " from " + str(q.number_of_questions()) + "\n\n"
                                                                                      ":black_circle: " + current_question.question,
                                            use_aliases=True))
    for possible_answer in current_question.answers:
        update.message.reply_text(possible_answer)

    return ASKAQUESTION


def ask_a_question(bot, update):
    global q, result, current_question
    u_answer = update.message.text
    if u_answer.lower() == current_question.correct_answer.lower():
        result.add_score(current_question.get_score())
        update.message.reply_text(emoji.emojize(':thumbsup: Correct answer\n'
                                                ':trophy: Your score: ' + str(result.get_score()), use_aliases=True))
    else:
        update.message.reply_text(emoji.emojize(':thumbsdown: Wrong answer\n'
                                                'Be more Careful next time', use_aliases=True))

    result.add_answer(current_question.get_id(), u_answer)
    """No more questions remained"""
    if q.number_of_remaining_questions() == 0:
        update.message.reply_text(emoji.emojize(':tada: End of the examset\n'
                                                'your total score: ' + str(result.get_score()), use_aliases=True))
        # print(result.get_answers())
        result.set_end_time()
        results.insert_one({
            's_id': result.get_s_id(),
            'q_id': result.get_q_id(),
            'begin_time': result.get_begin_time(),
            'endtime': result.get_end_time(),
            'category': result.get_category(),
            'score': result.get_score(),
            'answers': result.get_answers()
        })
        reply_keyboard = [[SEEMYSCORE, TAKETEST]]
        update.message.reply_text(emoji.emojize("What do you want to do?",
                                                use_aliases=True),
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True)
                                  )
        return EXAMORSCORE
    else:
        current_question = q.get_question()
        update.message.reply_text(emoji.emojize(":question: Question #" + str(q.get_question_number()) +
                                                " from " + str(q.number_of_questions()) + "\n\n"
                                                                                          ":black_circle: " + current_question.question,
                                                use_aliases=True))
        for possible_answer in current_question.answers:
            update.message.reply_text(possible_answer)
        return ASKAQUESTION



def done(bot, update, user_data):
    pass


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    TOKEN = 'TOKEN-BOT HERE'
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    converration_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            EXAMORSCORE: [RegexHandler('^(' + SEEMYSCORE + '|' + TAKETEST + ')$', exam_or_score)],
            FIRSTNAME: [MessageHandler(Filters.text, firstname)],
            LASTNAME: [MessageHandler(Filters.text, lastname)],
            CHOOSESET: [MessageHandler(Filters.text, chooseset)],
            QUESTIONS: [MessageHandler(Filters.text, questions)],
            ASKAQUESTION: [MessageHandler(Filters.text, ask_a_question)]
        },
        fallbacks=[RegexHandler('^Done$', done, pass_user_data=True)]
    )
    dp.add_handler(converration_handler)
    dp.add_error_handler(error)
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=PORT,
    #                       url_path=TOKEN)
    # updater.bot.set_webhook("https://fathomless-waters-22601.herokuapp.com/" + TOKEN)
    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()