import json
import uuid
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = 'NotesTable'

def lambda_handler(event, context):
    try:
        # Check if the event body is empty or None
        if 'body' not in event or event['body'] is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Please provide a valid JSON request body'})
            }
        
        data = json.loads(event['body'])

        # Validation
        if not all(data.get(key, '').strip() for key in ['title', 'content']):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Please provide title and content'})
            }

        # Create Note
        note_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        table = dynamodb.Table(table_name)
        table.put_item(
            Item={
                'noteId': note_id,
                'title': data['title'],
                'content': data['content'],
                'createdAt': current_time,
                'updatedAt': current_time
            }
        )

        # Response
        response_body = {
            'noteId': note_id,
            'message': 'Note created successfully'
        }
        return {
            'statusCode': 201,
            'body': json.dumps(response_body)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
