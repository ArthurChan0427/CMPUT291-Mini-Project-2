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
            results = searchQuestions()
            if results.count(True) > 0:
                selectedQuestion = displayResults(results)
                if selectedQuestion != None:
                    displaySelectedQuestion(selectedQuestion)
            else:
                print('No matching results...')
        elif command == 'x' or command == 'X':
            exit = input('exit the program (y / n): ')
            if exit == 'y' or exit == 'Y':
                return True
            return False
        else:
            print('Invalid command: ' + command + '\n')

def postAnswer(userID,qID):
    #control userID
    
    text = input('Please enter the body of the question: ').strip()
    #id = generateUniquePostID()

    db['posts_collection'].insert_one(
        {
            # 'Id': id,
            'Body': text,
            'OwnerUserId': userID,
            'ParentID': qID, 
            'CreationDate': str(datetime.now()),
            'PostTypeId': '2',
            'Score': '0',
            'CommentCount': '0',
            'ContentLicense': 'CC BY-SA 2.5',
        }
    )

def listAnswers(postID):
    db['posts_collection'].find({
        
    })

def castVote(userID, postID):
    pass


def postQuestion(userID):
    title = input('Please Enter the title of the question: ').strip()
    body = input('Please enter the body of the question: ').strip()
    tags = set(input(
        'Please enter tags sepearated by spaces (tag1 tag2 ...): ').strip().lower().split())
    document = {
        'Id': generateUniqueID(1),
        'Title': title,
        'Body': body,
        'CreationDate': str(datetime.now()),
        'PostTypeId': '1',
        'Score': '0',
        'ViewCount': '0',
        'AnswerCount': '0',
        'CommentCount': '0',
        'FavouriteCount': '0',
        'ContentLicense': 'CC BY-SA 2.5',
    }
    if userID != '':
        document['OwnerUserId'] = userID
    if tags != set():
        document['Tags'] = ' '.join(tags)
    db['posts_collection'].insert_one(document)
    for tag in tags:
        result = db['tags_collection'].count_documents({'TagName': tag})
        if result > 0:
            db['tags_collection'].update(
                {'TagName': tag}, {'$inc': {'Count': 1}})
        else:
            document = {
                'Id': generateUniqueID(2),
                'TagName': tag,
                'Count': 1,
            }
            db['tags_collection'].insert(document)


def searchQuestions():
    reg = '|'.join(input(
        'Please enter keywords separated by spaces (word1 word2 ...): ').strip().split())

    results = db['posts_collection'].find(
        {'$and': [
            {'$or': [
                {'Title': {'$regex': reg, '$options': 'i'}},
                {'Body': {'$regex': reg, '$options': 'i'}},
                {'Tags': {'$regex': reg, '$options': 'i'}}]},
            {'PostTypeId': '1'}
        ]}
    )

    return results


def displayResults(results):
    displayCount = 3
    i = 0
    temp = [0] * displayCount
    while True:
        for j in range(displayCount):
            if i == results.count(True):
                i = 0
            temp[j] = i
            print('-' * 50)
            print('Title: ' + str(results[i]['Title']))
            print('CreationDate: ' + str(results[i]['CreationDate']))
            print('Score: ' + str(results[i]['Score']))
            print('AnswerCount: ' + str(results[i]['AnswerCount']))
            i = i + 1
        choice = input('Enter 1 (top), 2, or 3 (bottom) to select the post currently displayed.\nEnter "x" to return to main menu\nEnter anything else to see more results').strip().lower()
        if choice in ['1', '2', '3']:
            return results[temp[int(choice)]]
        elif choice == 'x':
            return None


def displaySelectedQuestion(selectedQuestion):
    pass


def generateUniqueID(type):
    collection = ''
    if type == 1:
        collection = 'posts_collection'
    elif type == 2:
        collection = 'tags_collection'
    elif type == 3:
        collection = 'votes_collection'
    maxID = db[collection].aggregate([
        {'$group': {'_id': None, 'maxId': {
            '$max': {'$convert': {'input': '$Id', 'to': 'double'}}}}}
    ])
    return str(int(list(maxID)[0]['maxId']) + 1)


main()
