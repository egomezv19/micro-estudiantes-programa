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

    # Accedemos directamente a los valores en el body
    body = event['body']  # Asumimos que `body` ya es un diccionario
    programa_id = body['programa_id']
    alumno_id = body['alumno_id']
    programa = body.get('programa')
    
    if not programa:
        return {
            'statusCode': 400,
            'message': 'Datos del programa faltantes'
        }

    # Construir la expresión de actualización dinámicamente
    update_expression = "SET "
    expression_attribute_values = {}
    
    if 'descripcion' in programa:
        update_expression += "inscripcion.programa.descripcion = :descripcion, "
        expression_attribute_values[':descripcion'] = programa['descripcion']
    if 'fecha_inicio' in programa:
        update_expression += "inscripcion.programa.fecha_inicio = :fecha_inicio, "
        expression_attribute_values[':fecha_inicio'] = programa['fecha_inicio']
    if 'fecha_fin' in programa:
        update_expression += "inscripcion.programa.fecha_fin = :fecha_fin, "
        expression_attribute_values[':fecha_fin'] = programa['fecha_fin']
    if 'nombre' in programa:
        update_expression += "inscripcion.programa.nombre = :nombre, "
        expression_attribute_values[':nombre'] = programa['nombre']
    
    # Remover la última coma y espacio de la expresión de actualización
    update_expression = update_expression.rstrip(", ")

    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_estudiantes')

    # Actualizar el elemento específico
    response = table.update_item(
        Key={
            'programa_id': programa_id,
            'alumno_id': alumno_id
        },
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW"
    )

    # Salida (json)
    return {
        'statusCode': 200,
        'message': 'Información del programa actualizada exitosamente',
        'updated_attributes': response.get('Attributes')
    }