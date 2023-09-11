import json
import boto3

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
        
        if not note_exists(note_id):
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Note not found'})
            }

        table = dynamodb.Table(table_name)
        response = table.delete_item(
            Key={'noteId': note_id}
        )

        if 'ResponseMetadata' in response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return {
                'statusCode': 204,
                'body': json.dumps({'message': 'Note deleted successfully'})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Note not found'})
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