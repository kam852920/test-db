from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'nagp'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddData.html')


@app.route("/addData", methods=['POST'])
def addData():
    user_name = request.form['user_name']
    user_image_file = request.files['user_image_file']

    insert_sql = "INSERT INTO nagp VALUES (%s, %s)"
    cursor = db_conn.cursor()

    if user_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (user_name, user_image_file))
        db_conn.commit()
        # s3_file_name = "" + user_name + " " + user_image_file
        # Uplaod image file in S3 #
        image_file_name_in_s3 = user_name + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=image_file_name_in_s3, Body=user_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddDataOutput.html', name=user_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088, debug=True)
