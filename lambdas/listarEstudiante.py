import boto3
from boto3.dynamodb.conditions import Key
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
    # Acceder al body directamente (asumiendo que ya es un diccionario)
    body = event['body']
    programa_id = body['programa_id']
    
    # Inicialización de DynamoDB y tabla
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_estudiantes')
    
    # Realizar la consulta para obtener detalles del programa específico
    response = table.query(
        KeyConditionExpression=Key('programa_id').eq(programa_id)
    )
    
    # Salida (json)
    return {
        'statusCode': 200,
        'response': response['Items']  # Devuelve todos los detalles del programa
    }