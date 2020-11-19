from pymongo import MongoClient
from datetime import datetime

port = int(input('Please enter the port to connect to: '))
client = MongoClient('localhost', port)
db = client['291db']


def main():
    exit = False
    while not exit:
        userID = input("\nEnter your user ID: ").strip()
        if userID != '':
            displayUserReport(userID)
        exit = displayMainMenu(userID)
    print('shutting down...')


def displayUserReport(userID):
    print('\nLogging in as user ' + userID + '\n')
    postsCollection = db['posts_collection']

    questionCounts = postsCollection.count_documents(
        {
            '$and': [
                {'OwnerUserId': userID},
                {'PostTypeId': '1'}
            ]
        }
    )
    print('\nnumber of questions owned: ' + str(questionCounts) + '\n')
    if questionCounts > 0:
        averageQuestionScore = postsCollection.aggregate([
            {'$match': {
                '$and': [{'OwnerUserId': userID}, {'PostTypeId': '1'}]}},
            {'$group': {'_id': None, 'score': {'$avg': '$Score'}}}
        ])
        print('\naverage score of questions: ' +
              str(round(list(averageQuestionScore)[0]['score'], 2)) + '\n')

    answerCounts = postsCollection.count_documents(
        {
            '$and': [
                {'OwnerUserId': userID},
                {'PostTypeId': '2'}
            ]
        }
    )
    print('\nnumber of answers owned: ' + str(answerCounts) + '\n')
    if answerCounts > 0:
        averageAnswerScore = postsCollection.aggregate([
            {'$match': {
                '$and': [{'OwnerUserId': userID}, {'PostTypeId': '2'}]}},
            {'$group': {'_id': None, 'score': {'$avg': '$Score'}}}
        ])
        print('\naverage score of answers: ' +
              str(round(list(averageAnswerScore)[0]['score'], 2)) + '\n')

    if questionCounts > 0 or answerCounts > 0:
        totalScore = postsCollection.aggregate([
            {'$match': {'OwnerUserId': userID}},
            {'$group': {'_id': None, 'score': {'$sum': '$Score'}}
             }
        ])
        print('\ntotal votes received: ' +
              str(list(totalScore)[0]['score']) + '\n')


def displayMainMenu(userID):
    while True:
        print('\nEnter "x" to logout')
        print('Enter 1 to post a question')
        print('Enter 2 to search for questions\n')
        command = input()
        if command == '1':
            postQuestion(userID)
        elif command == '2':
            searchQuestions(userID)
        elif command == 'x' or command == 'X':
            exit = input('exit the program (y / n): ')
            if exit == 'y' or exit == 'Y':
                return True
            return False
        else:
            print('Invalid command: ' + command + '\n')


def postQuestion(userID):
    if userID == '':
        userID = None
    title = input('Please Enter the title of the question: ').strip()
    body = input('Please enter the body of the question: ').strip()
    tags = input(
        'Please enter tags sepearated by spaces (tag1 tag2 ...): ').strip()
    # id = generateUniquePostID()

    db['posts_collection'].insert_one(
        {
            # 'Id': id,
            'Title': title,
            'Body': body,
            'Tags': tags,
            'OwnerUserId': userID,
            'CreationDate': str(datetime.now()),
            'PostTypeId': '1',
            'Score': '0',
            'ViewCount': '0',
            'AnswerCount': '0',
            'CommentCount': '0',
            'FavouriteCount': '0',
            'ContentLicense': 'CC BY-SA 2.5',
        }
    )


# def generateUniquePostID():
#     largestpostID = db['posts_collection'].aggregate([
#         {'$group': {'_id': None, 'maxId': {'$max': '$Id'}}}
#     ])
#     return str(int(list(largestpostID)[0]['maxId']) + 1)


def searchQuestions(userID):
    pass


main()
