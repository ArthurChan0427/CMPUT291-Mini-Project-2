from pymongo import MongoClient

port = int(input('Please enter the port to connect to: '))
client = MongoClient('localhost', port)
db = client['291db']


def main():
    exit = False
    while not exit:
        userID = input("\nEnter your user ID: ")
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
        })
    print('\nnumber of questions owned: ' + str(questionCounts) + '\n')
    if questionCounts > 0:
        averageQuestionScore = postsCollection.aggregate([
            {'$match': {
                '$and': [{'OwnerUserId': userID}, {'PostTypeId': '1'}]}},
            {'$group': {'_id': None, 'score': {'$avg': '$Score'}}
             }])
        print('\naverage score of questions: ' +
              str(round(list(averageQuestionScore)[0]['score'], 2)) + '\n')

    answerCounts = postsCollection.count_documents(
        {
            '$and': [
                {'OwnerUserId': userID},
                {'PostTypeId': '2'}
            ]
        })
    print('\nnumber of answers owned: ' + str(answerCounts) + '\n')
    if answerCounts > 0:
        averageAnswerScore = postsCollection.aggregate([
            {'$match': {
                '$and': [{'OwnerUserId': userID}, {'PostTypeId': '2'}]}},
            {'$group': {'_id': None, 'score': {'$avg': '$Score'}}
             }])
        print('\naverage score of answers: ' +
              str(round(list(averageAnswerScore)[0]['score'], 2)) + '\n')

    if questionCounts > 0 or answerCounts > 0:
        totalScore = postsCollection.aggregate([
            {'$match': {'OwnerUserId': userID}},
            {'$group': {'_id': None, 'score': {'$sum': '$Score'}}
             }])
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
    title = input('Please Enter the title of the post:')
    body = input('Please enter the body of the post')
    tag = input('Please enter tags ')


def searchQuestions(userID):
    pass


main()
