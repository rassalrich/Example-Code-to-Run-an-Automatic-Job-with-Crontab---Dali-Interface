import mysql.connector #pip install mysql-connector
import paho.mqtt.client as mqtt #pip install paho-mqtt
import time
import threading
#this part is for user(Operator/technician) definations so you should fill it as the point you get from variable name
DB_username = "phpmyadmin"
DB_password = "dietpi"
DB_name = "scheduler"
DB_host = "localhost" #this one is localhost at 99% of projects
DB_scene_job_tableName = "scene_jobs"
DB_scene_list_tableName = "scenes"
MQTT_server = "localhost" #this one is localhost at 99% of projects
MQTT_port = 1883
timezone = "Asia/Dubai" ###IMPORTANT### update this variable with your timezone with tz standard
###IMPORTANT### run ####mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -uroot mysql### once to load timezone database to your mysql
#end of variable defination part

#connecting to Database
mydb = mysql.connector.connect(
  host=DB_host,
  user=DB_username,
  password=DB_password,
  database=DB_name
)
mycursor = mydb.cursor()
print("Connection to DB done. username and password are true")
mycursor.execute("set time_zone = '" + timezone + "'")
print("DB timezone updated")
#end of connecting DB

#connecting to MQTT
def mqtt_connector():
  client.loop_forever()
def on_connect(client, userdata, flags, rc):
    print("Connection to MQTT server done")
client = mqtt.Client()
client.on_connect = on_connect
client.connect(MQTT_server, MQTT_port)
#MQTT connection done

#fetching jobs to check if there is one for now?
def fetchDB():
  while 1:
    mydb.connect()
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT scene_id FROM " + DB_scene_job_tableName + " WHERE HOUR(run_at) = HOUR(CURRENT_TIME()) and MINUTE(run_at) = MINUTE(CURRENT_TIME())")
    scene_jobs_result = mycursor.fetchall()
    for job in scene_jobs_result:
      mycursor.execute("SELECT * FROM " + DB_scene_list_tableName + " WHERE id=" + str(job["scene_id"]))
      scene_list_result = mycursor.fetchall()
      for scene in scene_list_result:
        client.publish(str(scene["building_id"]) + "/" + str(scene["master_id"]) + "/Dali/In" ,str("{\"CMD\"\r\n:\"" + str(scene["scene_id"]) + "\"\r\n,\"BROADCAST\"\r\n:\"ALL\"\r\n}"))
    mydb.close()
    time.sleep(60)
#end fetch

if __name__ == "__main__":
  threading.Thread(target=mqtt_connector, args=()).start()
  threading.Thread(target=fetchDB, args=()).start()