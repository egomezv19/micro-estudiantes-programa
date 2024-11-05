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
    nombre = body.get('nombre')
    email = body.get('email')
    dni = body.get('dni')
    nro_tel = body.get('nro_tel')
    inscripcion = body.get('inscripcion')
    
    # Crear expresión de actualización
    update_expression = "SET "
    expression_attribute_values = {}

    if nombre:
        update_expression += "nombre = :nombre, "
        expression_attribute_values[':nombre'] = nombre
    if email:
        update_expression += "email = :email, "
        expression_attribute_values[':email'] = email
    if dni:
        update_expression += "dni = :dni, "
        expression_attribute_values[':dni'] = dni
    if nro_tel:
        update_expression += "nro_tel = :nro_tel, "
        expression_attribute_values[':nro_tel'] = nro_tel
    if inscripcion:
        update_expression += "inscripcion = :inscripcion, "
        expression_attribute_values[':inscripcion'] = inscripcion

    # Eliminar la última coma y espacio de la expresión
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
        'message': 'Estudiante actualizado exitosamente',
        'updated_attributes': response.get('Attributes')
    }