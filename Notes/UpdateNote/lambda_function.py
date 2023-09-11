import json
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = 'NotesTable'

def lambda_handler(event, context):
    try:
        if 'body' not in event or event['body'] is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Please provide a valid JSON request body'})
            }
        
        if 'pathParameters' not in event or 'noteId' not in event['pathParameters']:
            raise ValueError("Invalid request. 'noteId' is missing in pathParameters.")

        note_id = event['pathParameters']['noteId']
        if not note_id:
            raise ValueError("'noteId' cannot be empty.")

        request_body = json.loads(event['body'])

        if 'title' not in request_body or 'content' not in request_body:
            raise ValueError("Invalid request body. 'title' and 'content' are required fields.")
        
        if not note_exists(note_id):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Note not found'})
            }

        table = dynamodb.Table(table_name)
        response = table.update_item(
            Key={'noteId': note_id},
            UpdateExpression="SET title = :title, content = :content, updatedAt = :updatedAt",
            ExpressionAttributeValues={
                ':title': request_body['title'],
                ':content': request_body['content'],
                ':updatedAt': datetime.now().isoformat()
            },
            ReturnValues="ALL_NEW"
        )

        if 'Attributes' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Note not found'})
            }

        return {
            'statusCode': 200,
            'body': json.dumps(response['Attributes'])
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


def note_exists(note_id):
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={'noteId': note_id})
    return 'Item' in response