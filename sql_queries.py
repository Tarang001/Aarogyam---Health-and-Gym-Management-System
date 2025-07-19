from connection import connection
from mysql.connector import Error

conn = connection()
cursor = conn.cursor()

def target_muscles(exercise):
  query = "select  muscle_group_name  from exercise join exercise_muscle_group on exercise.exercise_id = exercise_muscle_group.exercise_id join muscle_group on muscle_group.muscle_group_id = exercise_muscle_group.muscle_group_id where exercise_name=%s"
  cursor.execute(query,(exercise,))
  response = cursor.fetchall()
  target_muscle = [muscle[0] for muscle in response]
  return target_muscle


# test = target_muscles('Push-up')
# print(test)
  