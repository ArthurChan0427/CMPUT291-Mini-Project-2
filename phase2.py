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
    pass


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
    pass


def searchQuestions(userID):
    pass


main()
