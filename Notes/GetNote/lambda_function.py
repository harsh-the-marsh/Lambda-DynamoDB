import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'NotesTable'

def lambda_handler(event, context):
    try:
        if 'pathParameters' not in event or 'noteId' not in event['pathParameters']:
            raise ValueError("noteId is missing in pathParameters.")

        note_id = event['pathParameters']['noteId']
        if not note_id:
            raise ValueError("'noteId' cannot be empty.")

        response = dynamodb.Table(table_name).get_item(Key={'noteId': note_id})

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Note not found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(response['Item'])
        }
    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(ve)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
