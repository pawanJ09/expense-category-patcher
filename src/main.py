from boto3 import resource
from botocore.exceptions import ClientError
import json
import os

resource = resource('dynamodb', region_name='us-east-2')
table = resource.Table('expense-categories')


def lambda_handler(event, context):
    try:
        print(f'Incoming event: {event}')
        event_http_method = event['requestContext']['http']['method']
        print(f'Incoming API Gateway HTTP Method: {event_http_method}')
        event_path = event['requestContext']['http']['path']
        print(f'Incoming API Gateway Path: {event_path}')
        body = event['body']
        print(f'Incoming API Gateway Body: {body}')
        req = json.loads(body)
        table_item = table.get_item(Key={'category': req['category']})
        if table_item['Item']:
            print(f'{req["category"]} found in table. Now updating')
            vals = list()
            try:
                vals = table_item['Item']['val']
            except KeyError as ke:
                print(f'Category has no existing val')
            vals.extend(req['val'])
            vals_list = list(set(vals))
            # Converting to set and back to list to remove duplicates
            response = table.update_item(Key={'category': req['category']},
                                         UpdateExpression="set val=:v",
                                         ExpressionAttributeValues={':v': vals_list},
                                         ReturnValues="UPDATED_NEW")
            print('Returning successful response')
            return {
                "statusCode": 200
            }


    except (AttributeError, KeyError) as er:
        msg = '{"message": "Category not found. Use POST instead."}'
        print(f'Exception caught: {msg}')
        return {
            "statusCode": 404,
            "body": json.dumps(msg)
        }
    except (Exception, ClientError) as e:
        msg = e.response['Error']['Message']
        print(f'Exception caught: {msg}')
        return {
            "statusCode": 500,
            "body": json.dumps(msg)
        }


if __name__ == '__main__':
    script_dir = os.path.dirname(__file__)
    rel_path = '../events/test-agw-event.json'
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path) as f:
        test_event = json.load(f)
        lambda_handler(test_event, None)