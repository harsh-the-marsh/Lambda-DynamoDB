import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'NotesTable'
default_page_size = 3

def lambda_handler(event, context):
    try:
        query_params = event['queryStringParameters'] or {}
        
        page_size = int(query_params.get('pageSize', default_page_size))
        if page_size <= 0:
            raise ValueError("pageSize must be a positive integer")
        
        page_number = int(query_params.get('pageNumber', 1))
        if page_number <= 0:
            raise ValueError("pageNumber must be a positive integer")
        
        sort_by = query_params.get('sortBy', 'createdAt')
        if sort_by not in ['createdAt', 'updatedAt']:
            raise ValueError("Invalid sortBy parameter. Use 'createdAt' or 'updatedAt'")
        
        title_filter = query_params.get('title')
        content_filter = query_params.get('content')
        
        # Calculate starting index and ending index for pagination
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        
        notes = list_notes_items(start_index, end_index, title_filter, content_filter)
        notes = sort_notes(notes, sort_by)

        return {
            'statusCode': 200,
            'body': json.dumps(notes)
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


def list_notes_items(start_index, end_index, title_filter=None, content_filter=None):
    table = dynamodb.Table(table_name)
    
    filter_expression = None
    expression_attribute_values = {}
    
    if title_filter:
        filter_expression = "contains(title, :title_filter)"
        expression_attribute_values[':title_filter'] = title_filter
    
    if content_filter:
        if filter_expression:
            filter_expression += " AND "
        else:
            filter_expression = ""
        filter_expression += "contains(content, :content_filter)"
        expression_attribute_values[':content_filter'] = content_filter
    
    if filter_expression:
        response = table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ProjectionExpression="noteId, title, content, createdAt, updatedAt",
        )
    else:
        response = table.scan(
            ProjectionExpression="noteId, title, content, createdAt, updatedAt",
        )

    items = response.get('Items', [])
    
    # Apply pagination after scanning
    items = items[start_index:end_index]
    
    return items


def sort_notes(notes, sort_by):
    notes.sort(key=lambda x: x[sort_by], reverse=True)
    return notes
