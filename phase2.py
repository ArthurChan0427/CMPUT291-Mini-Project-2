from pymongo import MongoClient
from datetime import datetime

port = int(input('Please enter the port to connect to: '))
client = MongoClient('localhost', port)
db = client['291db']


def main():
    """
        The program entry point which implements a simple loop prompts for a userID, display the corresponding user report, then display the main menu
        Input: None
        Output: None
    """
    exit = False
    while not exit:
        userID = input("\nEnter your user ID: ").strip()
        if userID != '':
            displayUserReport(userID)
        exit = displayMainMenu(userID)
    print('shutting down...')


def displayUserReport(userID):
    """
        Display the user report as per project specification.
        Input: userID - an unique Id representing the user
        Output: None
    """
    print('\nLogging in as user ' + userID)
    postsCollection = db['posts_collection']

    questionCounts = postsCollection.count_documents(
        {
            '$and': [
                {'OwnerUserId': userID},
                {'PostTypeId': '1'}
            ]
        }
    )
    print('number of questions owned: ' + str(questionCounts))
    if questionCounts > 0:
        averageQuestionScore = postsCollection.aggregate([
            {'$match': {
                '$and': [{'OwnerUserId': userID}, {'PostTypeId': '1'}]}},
            {'$group': {'_id': None, 'score': {'$avg': '$Score'}}}
        ])
        print('average score of questions: ' +
              str(round(list(averageQuestionScore)[0]['score'], 2)))

    answerCounts = postsCollection.count_documents(
        {
            '$and': [
                {'OwnerUserId': userID},
                {'PostTypeId': '2'}
            ]
        }
    )
    print('number of answers owned: ' + str(answerCounts))
    if answerCounts > 0:
        averageAnswerScore = postsCollection.aggregate([
            {'$match': {
                '$and': [{'OwnerUserId': userID}, {'PostTypeId': '2'}]}},
            {'$group': {'_id': None, 'score': {'$avg': '$Score'}}}
        ])
        print('average score of answers: ' +
              str(round(list(averageAnswerScore)[0]['score'], 2)))

    
    voteCount = db['votes_collection'].aggregate([
        {'$match': {'UserId': userID}},
        {'$group': {'_id': None, 'count': {'$sum': 1}}
            }
    ])
    print('total votes casted: ' +
            str(list(voteCount)[0]['count']))


def displayMainMenu(userID):
    """
        The main menu and the main driver which calls other functions.
        Input: userID - an unique Id representing the user
        Output: None
    """
    while True:
        print('\nEnter "x" to logout')
        print('Enter 1 to post a question')
        print('Enter 2 to search for questions')
        command = input()
        if command == '1':
            postQuestion(userID)
        elif command == '2':
            results, resultsCount = searchQuestions()
            if resultsCount > 0:
                selectedQuestion = displayQuestions(results, resultsCount)
                if selectedQuestion != None:
                    questionAction = displaySelectedQuestion(selectedQuestion)
                    if questionAction == 1:
                        postAnswer(userID, selectedQuestion)
                    elif questionAction == 2:
                        resultsA, resultsCountA = listAnswers(
                            selectedQuestion['Id'])
                        if resultsCountA > 0:
                            selectedAnswer = displayAnswer(
                                resultsA, resultsCountA)
                            if selectedAnswer != None:
                                AnswerAction = displaySelectedAnswer(
                                    selectedAnswer)
                                if AnswerAction == 1:
                                    castVote(userID, selectedAnswer['Id'])
                        else:
                            print('No matching results...')
                    elif questionAction == 3:
                        castVote(userID, selectedQuestion['Id'])
            else:
                print('No matching results...')
        elif command == 'x' or command == 'X':
            exit = input('exit the program (y / n): ')
            if exit == 'y' or exit == 'Y':
                return True
            return False
        else:
            print('Invalid command: ' + command)


def postAnswer(userID, selectedQuestion):
    """
        Inserts an answer to the selected question.
        Input: userID - an unique Id representing the user
               selectedQuestion - a dictionary representing the selected question
        Output: None
    """
    text = input('Please enter the body of the answer: ').strip()

    document = {
        'Id': generateUniqueID(1),
        'Body': text,
        'ParentId': selectedQuestion['Id'],
        'CreationDate': str(datetime.now()),
        'PostTypeId': '2',
        'Score': 0,
        'CommentCount': 0,
        'ViewCount': 0,
        'ContentLicense': 'CC BY-SA 2.5',
    }
    if userID != '':
        document['OwnerUserId'] = userID
    db['posts_collection'].insert_one(document)
    db['posts_collection'].update_one(
        {'Id': selectedQuestion['Id']}, {'$inc': {'AnswerCount': 1}})


def castVote(userID, postID):
    """
        Inserts a vote to the selected post
        Input: userID - an unique Id representing the user
               postID - an unique Id representing the selected post
        Output: None
    """
    if userID != '':
        if db['votes_collection'].find({'$and': [{'UserId': userID}, {'PostID': postID}]}).limit(1).count() > 0:
            print("You have already voted on this post!")
        else:
            db['posts_collection'].update_one(
                {'Id': postID}, {'$inc': {'Score': 1}})
            document = {
                'Id': generateUniqueID(3),
                'CreationDate': str(datetime.now()),
                'VoteTypeId': '2',
                'UserId': userID,
                'PostID': postID,
            }
            db['votes_collection'].insert_one(document)
            print("Your vote has been casted")
    else:
        db['posts_collection'].update_one(
            {'Id': postID}, {'$inc': {'Score': 1}})
        document = {
            'Id': generateUniqueID(3),
            'CreationDate': str(datetime.now()),
            'VoteTypeId': '2',
            'PostID': postID,
        }
        db['votes_collection'].insert_one(document)
        print("Your vote has been casted.")


def postQuestion(userID):
    """
        Inserts a question.
        Input: userID - an unique Id representing the user
        Output: None
    """
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
        'Score': 0,
        'ViewCount': 0,
        'AnswerCount': 0,
        'CommentCount': 0,
        'FavouriteCount': 0,
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
            db['tags_collection'].update_one(
                {'TagName': tag}, {'$inc': {'Count': 1}})
        else:
            document = {
                'Id': generateUniqueID(2),
                'TagName': tag,
                'Count': 1,
            }
            db['tags_collection'].insert_one(document)


def searchQuestions():
    """
        Prompts for keywords and query posts_collection for results with at least one matching keyword.
        Input: None
        Output: results - a list of dictionaries representing the retrieved questions
                len(results) - number of questions retrieved
    """
    reg = '|'.join(input(
        'Please enter keywords separated by spaces (word1 word2 ...): ').strip().split())

    searchCondition = {
        '$and': [
            {'$or': [
                {'Title': {'$regex': reg, '$options': 'i'}},
                {'Body': {'$regex': reg, '$options': 'i'}},
                {'Tags': {'$regex': reg, '$options': 'i'}}]},
            {'PostTypeId': '1'}
        ]
    }
    results = list(db['posts_collection'].find(searchCondition))
    return (results, len(results))


def listAnswers(postID):
    """
        Returns all existing answers to a selected question.
        Input: postID - an unique Id representing the selected post
        Output: resultsA - a list of dictionaries representing the retrieved answers
                len(resultsA) - number of answers retrieved
    """
    resultsA = list(db['posts_collection'].find(
        {'$and': [
            {'$or': [
                {'ParentId': postID}]},

            {'PostTypeId': '2'}
        ]}
    ))
    return (resultsA, len(resultsA))


def displayAnswer(results, resultsCount):
    """
        Display a list of answers and prompts the user to select an answer
        Input: results - a list of dictionaries representing the answers
               resultsCount - number of answers in the list
        Output: the selected answer, or None
    """
    displayCount = 3
    i = 0
    temp = [0] * displayCount
    while True:
        for j in range(displayCount):
            if i == resultsCount:
                i = 0
            temp[j] = i
            result = results[i]
            print('-' * 20 + ' ' + str(j + 1) + ' ' + '-' * 20)
            print('Answer: ' + str(result['Body']))
            print('CreationDate: ' + str(result['CreationDate']))
            print('Score: ' + str(result['Score']))
            i = i + 1
        print('\nEnter 1 (top), 2, or 3 (bottom) to select the post currently displayed.')
        print('Enter "x" to return to main menu.')
        print('Enter anything else to see more results.')
        choice = input().strip().lower()
        if choice in ['1', '2', '3']:
            return results[temp[int(choice) - 1]]
        elif choice == 'x':
            return None


def displayQuestions(results, resultsCount):
    """
        Displays a list of questions and prompts the user to select a question
        Input: results - a list of dictionaries representing the questions
               resultsCount - number of questions in the list
        Output: the selected question, or None
    """
    displayCount = 3
    i = 0
    temp = [0] * displayCount
    while True:
        for j in range(displayCount):
            if i == resultsCount:
                i = 0
            temp[j] = i
            result = results[i]
            print('-' * 20 + ' ' + str(j + 1) + ' ' + '-' * 20)
            print('Title: ' + str(result['Title']))
            print('CreationDate: ' + str(result['CreationDate']))
            print('Score: ' + str(result['Score']))
            print('AnswerCount: ' + str(result['AnswerCount']))
            i = i + 1
        print('\nEnter 1 (top), 2, or 3 (bottom) to select the post currently displayed.')
        print('Enter "x" to return to main menu.')
        print('Enter anything else to see more results.')
        choice = input().strip().lower()
        if choice in ['1', '2', '3']:
            return results[temp[int(choice) - 1]]
        elif choice == 'x':
            return None


def displaySelectedQuestion(selectedQuestion):
    """
        Display all fields of a selected question and prompt for an action from the user.
        Input: selectedQuestion - a dictionary representing the selected question
        Output: optionEntered - action selected by the user
    """
    db['posts_collection'].update_one(
        {'Id': selectedQuestion['Id']}, {'$inc': {'ViewCount': 1}})
    if 'ViewCount' in selectedQuestion:
        selectedQuestion['ViewCount'] += 1
    print('\n' + '-' * 20 + ' Your selection ' + '-' * 20)
    for field in selectedQuestion.keys():
        print(field + ": " + str(selectedQuestion[field]))
    print('\nEnter 1 to post an answer to this question.')
    print('Enter 2 to list all existing answers to this question.')
    print('Enter 3 to vote for this question.')
    print('Enter anything else to return to main menu.')
    optionEntered = input()
    if optionEntered.isdigit():
        return int(optionEntered)
    return optionEntered


def displaySelectedAnswer(selectedAnswer):
    """
        Display all fields of a selected answer and prompt for an action from the user.
        Input: selectedAnswer - a dictionary representing the selected answer
        Output: optionEntered - action selected by the user
    """
    db['posts_collection'].update_one(
        {'Id': selectedAnswer['Id']}, {'$inc': {'ViewCount': 1}})
    if 'ViewCount' in selectedAnswer:
        selectedAnswer['ViewCount'] += 1
    print('\n' + '-' * 20 + ' Your selection ' + '-' * 20)
    for field in selectedAnswer.keys():
        print(field + ": " + str(selectedAnswer[field]))
    print('Enter 1 to vote for this answer.')
    print('Enter anything else to return to main menu.')
    optionEntered = input()
    if optionEntered.isdigit():
        return int(optionEntered)
    return optionEntered


def generateUniqueID(type):
    """
        Return an Id that is unique with respect to the selected collection
        Input: type - 1 = posts_collection, 2 = tags_collection, 3 = votes_collection
        Output: generated Id
    """
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
