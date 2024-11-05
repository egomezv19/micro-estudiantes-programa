import boto3
import json 
def lambda_handler(event, context):
    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']
    lambda_client = boto3.client('lambda')
    payload_string = json.dumps({"token": token})
    
    invoke_response = lambda_client.invoke(
        FunctionName="ValidarTokenAcceso",  # Nombre de la función Lambda que valida el token
        InvocationType="RequestResponse",
        Payload=payload_string
    )
    
    response = json.loads(invoke_response['Payload'].read())
    
    if response.get('statusCode') == 403:
        return {
            'statusCode': 403,
            'status': 'Forbidden - Acceso No Autorizado'
        }
    # Fin - Proteger el Lambda
    body = event['body']
    programa_id = body['programa_id']
    alumno_id = body['alumno_id']
    
    # Proceso: Inicialización de DynamoDB y tabla
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_estudiantes')  # Cambia 't_estudiantes' al nombre real de tu tabla
    
    # Eliminar el elemento específico
    response = table.delete_item(
        Key={
            'programa_id': programa_id,
            'alumno_id': alumno_id
        }
    )
    
    # Salida (json)
    return {
        'statusCode': 200,
        'response': response
    }