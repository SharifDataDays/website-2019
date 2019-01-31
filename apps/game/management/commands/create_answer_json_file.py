from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import os
import json
from sys import exit
from django.apps import apps
from django.db import models


# THIS FILE IS ULTIMATE TOF AND I KNOW IT! BUT IT WORKS, DEAL WITH IT!


MAX_DOC_ID = 999999
FILE_UPLOAD_QUESTION_GROUP = 93949596


answers = {}


TERMINOLOGY_MAP = {
    "multiple": "multiple_choice",
    "numeric_range": "interval_number",
    "string": "single_answer",
    "multi_string": "multiple_answer",
    "numeric": "single_number",
}



def add_questions(questions_file_path):
    print(questions_file_path)
    questions = pd.read_csv(questions_file_path)

    for i in range(len(questions)):
        question = questions.iloc[i].to_dict()
        
        question_type = question['type']
        
        if pd.isna(question_type):
            print('DONE :)')
            break
            
        if question_type not in list(TERMINOLOGY_MAP.keys()):
            print('INVALID TYPE "{}"'.format(question_type))
            print(i)
            exit(0)
        
        choices, answer = FUNCTION_MAP[TERMINOLOGY_MAP[question_type]](question)
        skill = question['skill']
        definition = question['question']
        group_id = question['group_id']
        difficulty = question['level']
        question_id = question['id']

        answers[question_id] = answer
        
    # TODO
    # in order to add file_upload questions to db we must run generator script and then call save_in_database
    # function with these inputs:
    # 1. question_type = "file_upload"
    # 2. definition = <dataset download file url on server>
    # 3. choices = ""
    # 4. answer = <answer file path on server (not reachable from outside of server)>
    # 5. skill = "categorization"

    # this part can be automated but since the generator is another script, 
    # its better to do these instructions manually.


def add_datasets(datasets_folder_path):
    for i, dataset in enumerate(os.listdir('{}/tds'.format(datasets_folder_path))):
        dataset_hash = dataset[:-4] # drop .csv format
        dataset_file_path = '{}/tds/{}'.format(datasets_folder_path, dataset)
        dataset_answer_path = '{}/tdsa/{}_answer'.format(datasets_folder_path, dataset)

        answers[MAX_DOC_ID - i] = dataset_answer_path


def score_from_level(question_type, difficulty):
    if question_type in ['multiple_choice']:
        return {'Easy': 100, 'Medium': 200, 'Difficult': 300}[difficulty]
    elif question_type in ['file_upload']:
        return 1000
    else:
        return {'Easy': 150, 'Medium': 300, 'Difficult': 600}[difficulty]


diff_map = {'Easy': 'easy', 'Medium': 'medium', 'Difficult': 'difficult'}

x = 0

def answer_multiple_choice(question):
    choices = []
    if not pd.isna(question['choices']):
        choices.append(question['choices'])
        
    if not pd.isna(question['Unnamed: 6']):
        choices.append(question['Unnamed: 6'])

    if not pd.isna(question['Unnamed: 7']):
        choices.append(question['Unnamed: 7'])

    if not pd.isna(question['Unnamed: 8']):
        choices.append(question['Unnamed: 8'])

    choices = '$'.join(choices)
    answer = question['answer_multiple']
    return choices, answer


def answer_single_answer(question):
    answer = question['answer_string']
    return None, answer


def answer_multiple_answer(question):
    answer = question['answer_string']
    answer = answer.strip()[1:-1].split(',')
    answer = '$'.join(answer)
    
    return None, answer


def answer_single_number(question):
    answer = question['answer_numeric']
    return None, answer


def answer_interval_number(question):
    answer = '{}${}'.format(question['from'], question['to'])
    return None, answer


class Command(BaseCommand):
    help = 'Adds questions specifiied in csv input file to database'

    def add_arguments(self, parser):
        parser.add_argument('csv_file_path', nargs='+', type=str)
        parser.add_argument('ddatasets_folder_path', nargs='+', type=str)
        parser.add_argument('result_json_file_path', nargs='+', type=str)

    def handle(self, *args, **options):
        csv_file_path = options['csv_file_path'][0]
        ddatasets_folder_path = options['ddatasets_folder_path'][0]
        result_json_file_path = options['result_json_file_path'][0]

        self.stdout.write(self.style.SUCCESS('Adding questions'))
        add_questions(csv_file_path)
        self.stdout.write(self.style.SUCCESS('Finished adding questions'))
        self.stdout.write(self.style.SUCCESS('Adding datasets'))
        add_datasets(ddatasets_folder_path)
        self.stdout.write(self.style.SUCCESS('Finished adding datasets'))
        self.stdout.write(self.style.SUCCESS('Writing json file'))

        with open(result_json_file_path, mode='w') as f:
            json.dump(answers, f)

        self.stdout.write(self.style.SUCCESS('Finished writing json file'))
        self.stdout.write(self.style.SUCCESS('DONE'))        

FUNCTION_MAP = {
    "multiple_choice": answer_multiple_choice,
    "single_answer": answer_single_answer,
    "multiple_answer": answer_multiple_answer,
    "single_number": answer_single_number,
    "interval_number": answer_interval_number,
}


